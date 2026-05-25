"""CLI entry point: timewarp demo / timewarp warp / timewarp table"""

from __future__ import annotations

import argparse
import sys

from .engine import TimeWarpEngine


def cmd_demo(_args: argparse.Namespace) -> None:
    import subprocess, sys
    subprocess.run([sys.executable, "examples/demo.py"])


def cmd_warp(args: argparse.Namespace) -> None:
    engine = TimeWarpEngine()
    result = engine.warp(args.minutes, args.state)
    print(result)


def cmd_table(_args: argparse.Namespace) -> None:
    engine = TimeWarpEngine()
    print("State         Coefficient   Effect")
    print("-" * 45)
    for state, coef in engine.table().items():
        effect = "compresses" if coef < 1.0 else ("identity" if coef == 1.0 else "stretches")
        print(f"{state:<14} {coef:<14.2f} {effect}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="timewarp",
        description="TimeWarpEngine — subjective time for LLM agents",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("demo", help="Run the full demo")

    p_warp = sub.add_parser("warp", help="Calculate perceived time")
    p_warp.add_argument("minutes", type=float, help="Real elapsed minutes")
    p_warp.add_argument("state", nargs="?", default="normal",
                        help="Emotional state (default: normal)")

    sub.add_parser("table", help="Show the warp coefficient table")

    args = parser.parse_args()

    dispatch = {"demo": cmd_demo, "warp": cmd_warp, "table": cmd_table}
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
