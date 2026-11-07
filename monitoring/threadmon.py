#!/usr/bin/env python3
"""Per-thread CPU monitor for a macOS process (no root needed for own processes).

Usage: threadmon.py <pid> [seconds=10] [interval_ms=50]

Reports, per named thread: average CPU%, peak CPU% over one interval, and the
fraction of intervals in which the thread was >=90% busy (i.e. saturated).
"""
import ctypes, ctypes.util, sys, time

libproc = ctypes.CDLL(ctypes.util.find_library("proc"))
libproc.proc_pidinfo.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_int]
libproc.proc_pidinfo.restype = ctypes.c_int

PROC_PIDTHREADINFO = 5
PROC_PIDLISTTHREADS = 6


class ThreadInfo(ctypes.Structure):
    _fields_ = [
        ("user_time", ctypes.c_uint64),   # ns
        ("system_time", ctypes.c_uint64), # ns
        ("cpu_usage", ctypes.c_int32),
        ("policy", ctypes.c_int32),
        ("run_state", ctypes.c_int32),
        ("flags", ctypes.c_int32),
        ("sleep_time", ctypes.c_int32),
        ("curpri", ctypes.c_int32),
        ("priority", ctypes.c_int32),
        ("maxpriority", ctypes.c_int32),
        ("name", ctypes.c_char * 64),
    ]


def snapshot(pid):
    buf = (ctypes.c_uint64 * 4096)()
    n = libproc.proc_pidinfo(pid, PROC_PIDLISTTHREADS, 0, buf, ctypes.sizeof(buf))
    if n <= 0:
        raise SystemExit(f"cannot list threads of pid {pid}")
    out = {}
    for h in buf[: n // 8]:
        ti = ThreadInfo()
        if libproc.proc_pidinfo(pid, PROC_PIDTHREADINFO, h, ctypes.byref(ti), ctypes.sizeof(ti)) == ctypes.sizeof(ti):
            out[h] = (ti.user_time + ti.system_time, ti.name.decode(errors="replace") or f"<tid {h:x}>", ti.curpri)
    return out


def main():
    pid = int(sys.argv[1])
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 10
    iv = (float(sys.argv[3]) if len(sys.argv) > 3 else 50) / 1000

    stats = {}  # handle -> [name, pri, total_ns, peak_frac, n_sat, n_iv]
    prev, pt = snapshot(pid), time.monotonic()
    t_end = pt + secs
    total_wall = 0.0
    while time.monotonic() < t_end:
        time.sleep(iv)
        cur, ct = snapshot(pid), time.monotonic()
        dt = (ct - pt) * 1e9
        total_wall += dt
        for h, (cpu, name, pri) in cur.items():
            if h not in prev:
                continue
            frac = (cpu - prev[h][0]) / dt
            s = stats.setdefault(h, [name, pri, 0, 0.0, 0, 0])
            s[0], s[1] = name, pri
            s[2] += cpu - prev[h][0]
            s[3] = max(s[3], frac)
            s[4] += frac >= 0.90
            s[5] += 1
        prev, pt = cur, ct

    rows = sorted(stats.values(), key=lambda s: -s[2])
    proc_total = sum(s[2] for s in rows) / total_wall * 100
    print(f"pid {pid}: {total_wall/1e9:.1f}s window, process total {proc_total:.0f}% CPU\n")
    print(f"{'thread':48} {'pri':>3} {'avg%':>6} {'peak%':>6} {'>=90% busy':>11}")
    for name, pri, tot, peak, nsat, niv in rows:
        avg = tot / total_wall * 100
        if avg < 0.5:
            continue
        print(f"{name[:48]:48} {pri:>3} {avg:6.1f} {peak*100:6.0f} {nsat/max(niv,1)*100:10.0f}%")


if __name__ == "__main__":
    main()
