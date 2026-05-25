"""
timewarp demo — run with:  python examples/demo.py
"""

from timewarp import TimeWarpEngine, NeuroStateTimeWarp

def demo_basic() -> None:
    print("=" * 60)
    print("TimeWarpEngine — Basic Demo")
    print("=" * 60)
    engine = TimeWarpEngine()

    scenarios = [
        (120.0, "flow",   "Deep coding session"),
        (120.0, "joy",    "Fun pair-programming"),
        (120.0, "normal", "Routine task"),
        (120.0, "stress", "Bug hunting under deadline"),
        (120.0, "bore",   "Waiting for CI to finish"),
        (10.0,  "stress", "10-min error loop"),
    ]

    for real, state, label in scenarios:
        result = engine.warp(real, state)
        print(f"\n{label}")
        print(f"  {result}")

def demo_neurostate() -> None:
    print("\n" + "=" * 60)
    print("NeuroStateTimeWarp — Adapter Demo")
    print("=" * 60)

    adapter = NeuroStateTimeWarp()

    snapshots = [
        ("flow_state",    {"joy": 20, "stress": 5,  "curiosity": 95, "sorrow": 0}),
        ("joyful",        {"joy": 85, "stress": 10, "curiosity": 50, "sorrow": 5}),
        ("under_pressure",{"joy": 10, "stress": 90, "curiosity": 20, "sorrow": 30}),
        ("drained",       {"joy": 5,  "stress": 40, "curiosity": 10, "sorrow": 80}),
    ]

    for agent_id, state in snapshots:
        line = adapter.log_entry(60.0, state, agent_id=agent_id)
        print(f"\n  {line}")

def demo_cpos_log() -> None:
    print("\n" + "=" * 60)
    print("CPOS-style Log Integration Example")
    print("=" * 60)

    engine = TimeWarpEngine()

    print("\n[GDC_LOG] feat/video_render merge complete (real: 180 min)")
    r = engine.warp(180.0, "flow")
    print(f"[NeuroState] state=flow joy=90 stress=5")
    print(f"[TimeWarp] {r.message}")
    print(f"[TimeWarp] real={r.real_minutes:.0f}m → perceived={r.perceived_minutes:.0f}m")

    print("\n[GDC_LOG] feat/error_loop 5 consecutive failures (real: 10 min)")
    r2 = engine.warp(10.0, "stress")
    print(f"[NeuroState] state=stress stress=95 joy=5")
    print(f"[TimeWarp] {r2.message}")
    print(f"[TimeWarp] real={r2.real_minutes:.0f}m → perceived={r2.perceived_minutes:.0f}m")
    print("[TimeWarp] 💤 Recommend: short break.")

if __name__ == "__main__":
    demo_basic()
    demo_neurostate()
    demo_cpos_log()
