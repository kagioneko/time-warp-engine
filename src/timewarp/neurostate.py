"""
NeuroState adapter for TimeWarpEngine.

Accepts a NeuroState-compatible dict and delegates to TimeWarpEngine.
"""

from __future__ import annotations

from typing import Any

from .engine import TimeWarpEngine, TimeWarpResult


class NeuroStateTimeWarp:
    """
    Drop-in adapter that reads a NeuroState snapshot dict and
    returns a TimeWarpResult without manual field extraction.

    Expected NeuroState keys (all optional, default 0.0):
        joy, stress, curiosity, sorrow, guilt, openness, ...

    Example::

        adapter = NeuroStateTimeWarp()
        state = {"joy": 80, "stress": 10, "curiosity": 60, "sorrow": 5}
        result = adapter.warp(real_minutes=60.0, neurostate=state)
        print(result)
    """

    def __init__(self, engine: TimeWarpEngine | None = None) -> None:
        self.engine = engine or TimeWarpEngine()

    def warp(
        self,
        real_minutes: float,
        neurostate: dict[str, Any],
    ) -> TimeWarpResult:
        """Warp time using a raw NeuroState snapshot dict."""
        return self.engine.warp_from_neurostate(
            real_minutes=real_minutes,
            joy=float(neurostate.get("joy", 0.0)),
            stress=float(neurostate.get("stress", 0.0)),
            curiosity=float(neurostate.get("curiosity", 0.0)),
            sorrow=float(neurostate.get("sorrow", 0.0)),
        )

    def log_entry(
        self,
        real_minutes: float,
        neurostate: dict[str, Any],
        agent_id: str = "agent",
    ) -> str:
        """Return an Observatory-compatible log line."""
        result = self.warp(real_minutes, neurostate)
        return (
            f"[TimeWarp][{agent_id}] "
            f"real={result.real_minutes:.1f}m "
            f"perceived={result.perceived_minutes:.1f}m "
            f"state={result.state} coef={result.coefficient:.3f} | "
            f"{result.message}"
        )
