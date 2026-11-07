#!/usr/bin/env python3
"""Detect likely stop-the-world GC pauses in a HotSpot 8 process from outside.

HotSpot 8 on macOS only names Java threads ("Java: ..."); GC worker threads are
unnamed. A STW pause shows up as several unnamed threads burning CPU together
while "Java: Client thread" is idle.

Usage: gcwatch.py <pid> [seconds=20] [interval_ms=10]
"""
import sys, time
sys.path.insert(0, __import__("os").path.dirname(__file__))
from threadmon import snapshot  # noqa: E402


def main():
    pid = int(sys.argv[1])
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 20
    iv = (float(sys.argv[3]) if len(sys.argv) > 3 else 10) / 1000

    prev, pt = snapshot(pid), time.monotonic()
    t0, t_end = pt, pt + secs
    events, cur_ev = [], None
    client_busy = n = 0
    while time.monotonic() < t_end:
        time.sleep(iv)
        cur, ct = snapshot(pid), time.monotonic()
        dt = (ct - pt) * 1e9
        unnamed = client = 0.0
        for h, (cpu, name, _) in cur.items():
            if h in prev:
                frac = (cpu - prev[h][0]) / dt
                if name.startswith("<tid"):
                    unnamed += frac
                elif name == "Java: Client thread":
                    client = frac
        n += 1
        client_busy += client >= 0.9
        if unnamed >= 1.5 and client < 0.2:  # >=1.5 cores of GC-ish work, game thread stopped
            if cur_ev is None:
                cur_ev = [pt - t0, ct - t0, unnamed]
            else:
                cur_ev[1], cur_ev[2] = ct - t0, max(cur_ev[2], unnamed)
        elif cur_ev is not None:
            events.append(cur_ev)
            cur_ev = None
        prev, pt = cur, ct
    if cur_ev:
        events.append(cur_ev)

    print(f"{secs:.0f}s window, {n} samples; Client thread >=90% busy in {client_busy/n*100:.0f}% of samples")
    print(f"likely STW GC pauses: {len(events)}")
    for s, e, peak in events:
        print(f"  t={s:6.2f}s  ~{(e-s)*1000:5.0f} ms  (unnamed threads peak {peak*100:.0f}% CPU)")


if __name__ == "__main__":
    main()
