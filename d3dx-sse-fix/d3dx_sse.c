// SSE replacements for Wine 7.7's d3dx9 D3DXVec3Project / D3DXVec3ProjectArray,
// injected into th12.exe as thcrap codecaves.
//
// Wine's versions run every point through identity * world * view * proj (three 4x4
// matrix multiplies) and the transform, all in x87, which Rosetta emulates slowly.
// These do the same arithmetic in the same operation order (so results match Wine's
// when the x87 precision control is single, which d3d9 sets), but in SSE, and
// ProjectArray builds the combined matrix once per call instead of once per point.
//
// Constraints for codecave use: each exported function must be self-contained
// (no calls, no relocations, no constant-pool loads), stdcall, 32-bit.
#include <emmintrin.h>

typedef struct { float x, y, z; } V3;
typedef struct { unsigned X, Y, Width, Height; float MinZ, MaxZ; } VP;

#define INLINE static inline __attribute__((always_inline))

// Float constants built from integer bits through inline asm so the compiler
// cannot fold them into a (relocated) constant pool.
INLINE __m128 const_ps(unsigned bits) {
    __m128 r;
    __asm__("movd %1, %0\n\tshufps $0, %0, %0" : "=x"(r) : "r"(bits));
    return r;
}

// r = r * b  (row-vector convention, like D3DXMatrixMultiply(out, r, b)).
// Wine: out[i][j] = ((r[i][0]*b[0][j] + r[i][1]*b[1][j]) + r[i][2]*b[2][j]) + r[i][3]*b[3][j]
INLINE void mat_mul(__m128 r[4], const float *b) {
    __m128 b0 = _mm_loadu_ps(b), b1 = _mm_loadu_ps(b + 4);
    __m128 b2 = _mm_loadu_ps(b + 8), b3 = _mm_loadu_ps(b + 12);
    for (int i = 0; i < 4; i++) {
        __m128 a = r[i];
        __m128 s = _mm_mul_ps(_mm_shuffle_ps(a, a, 0x00), b0);
        s = _mm_add_ps(s, _mm_mul_ps(_mm_shuffle_ps(a, a, 0x55), b1));
        s = _mm_add_ps(s, _mm_mul_ps(_mm_shuffle_ps(a, a, 0xaa), b2));
        s = _mm_add_ps(s, _mm_mul_ps(_mm_shuffle_ps(a, a, 0xff), b3));
        r[i] = s;
    }
}

// m = identity; if (world) m *= world; if (view) m *= view; if (proj) m *= proj;
INLINE void build(__m128 r[4], const float *proj, const float *view, const float *world) {
    __m128 e0 = _mm_move_ss(_mm_setzero_ps(), const_ps(0x3f800000u)); // (1,0,0,0)
    r[0] = e0;
    r[1] = _mm_shuffle_ps(e0, e0, _MM_SHUFFLE(1, 1, 0, 1));             // (0,1,0,0)
    r[2] = _mm_shuffle_ps(e0, e0, _MM_SHUFFLE(1, 0, 1, 1));             // (0,0,1,0)
    r[3] = _mm_shuffle_ps(e0, e0, _MM_SHUFFLE(0, 1, 1, 1));             // (0,0,0,1)
    if (world) mat_mul(r, world);
    if (view) mat_mul(r, view);
    if (proj) mat_mul(r, proj);
}

// D3DXVec3TransformCoord: (((x*m0 + y*m1) + z*m2) + m3) / w
INLINE __m128 xform(const __m128 r[4], const V3 *v) {
    __m128 x = _mm_load1_ps(&v->x), y = _mm_load1_ps(&v->y), z = _mm_load1_ps(&v->z);
    __m128 s = _mm_add_ps(_mm_mul_ps(x, r[0]), _mm_mul_ps(y, r[1]));
    s = _mm_add_ps(s, _mm_mul_ps(z, r[2]));
    s = _mm_add_ps(s, r[3]);
    return _mm_div_ps(s, _mm_shuffle_ps(s, s, 0xff));
}

INLINE void store3(V3 *o, __m128 p) {
    o->x = _mm_cvtss_f32(p);
    o->y = _mm_cvtss_f32(_mm_shuffle_ps(p, p, 0x55));
    o->z = _mm_cvtss_f32(_mm_shuffle_ps(p, p, 0xaa));
}

// Viewport mapping, as Wine:
//   x = X + ((1 + x) * Width) * 0.5
//   y = Y + ((1 - y) * Height) * 0.5
//   z = MinZ + z * (MaxZ - MinZ)
typedef struct { __m128 one, half, fx, fy, fw, fh, minz, dz; } VPC;

INLINE void vp_prep(VPC *c, const VP *vp) {
    c->one = const_ps(0x3f800000u);
    c->half = const_ps(0x3f000000u);
    c->fx = _mm_cvtsi32_ss(_mm_setzero_ps(), (int)vp->X);
    c->fy = _mm_cvtsi32_ss(_mm_setzero_ps(), (int)vp->Y);
    c->fw = _mm_cvtsi32_ss(_mm_setzero_ps(), (int)vp->Width);
    c->fh = _mm_cvtsi32_ss(_mm_setzero_ps(), (int)vp->Height);
    c->minz = _mm_load_ss(&vp->MinZ);
    c->dz = _mm_sub_ss(_mm_load_ss(&vp->MaxZ), c->minz);
}

INLINE void vp_store(V3 *o, __m128 p, const VPC *c) {
    __m128 px = p, py = _mm_shuffle_ps(p, p, 0x55), pz = _mm_shuffle_ps(p, p, 0xaa);
    __m128 ox = _mm_add_ss(c->fx, _mm_mul_ss(_mm_mul_ss(_mm_add_ss(c->one, px), c->fw), c->half));
    __m128 oy = _mm_add_ss(c->fy, _mm_mul_ss(_mm_mul_ss(_mm_sub_ss(c->one, py), c->fh), c->half));
    __m128 oz = _mm_add_ss(c->minz, _mm_mul_ss(pz, c->dz));
    o->x = _mm_cvtss_f32(ox);
    o->y = _mm_cvtss_f32(oy);
    o->z = _mm_cvtss_f32(oz);
}

__attribute__((stdcall)) V3 *sse_Vec3Project(V3 *out, const V3 *v, const VP *vp,
        const float *proj, const float *view, const float *world) {
    __m128 r[4];
    build(r, proj, view, world);
    __m128 p = xform(r, v);
    if (vp) {
        VPC c;
        vp_prep(&c, vp);
        vp_store(out, p, &c);
    } else {
        store3(out, p);
    }
    return out;
}

__attribute__((stdcall)) V3 *sse_Vec3ProjectArray(V3 *out, unsigned outstride, const V3 *in,
        unsigned instride, const VP *vp, const float *proj, const float *view,
        const float *world, unsigned n) {
    if (!n) return out;
    __m128 r[4];
    build(r, proj, view, world);
    char *o = (char *)out;
    const char *s = (const char *)in;
    if (vp) {
        VPC c;
        vp_prep(&c, vp);
        for (unsigned i = 0; i < n; i++, o += outstride, s += instride)
            vp_store((V3 *)o, xform(r, (const V3 *)s), &c);
    } else {
        for (unsigned i = 0; i < n; i++, o += outstride, s += instride)
            store3((V3 *)o, xform(r, (const V3 *)s));
    }
    return out;
}
