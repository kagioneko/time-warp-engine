"""
TimeWarpEngine — Subjective time perception layer for LLM agents.

Maps NeuroState values to a perceived-time coefficient, simulating
the human experience that joyful time flies and stressful time crawls.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Warp coefficient table
# Higher coefficient = time feels longer (stress/bore)
# Lower coefficient  = time feels shorter (flow/joy)
# ---------------------------------------------------------------------------
DEFAULT_WARP_TABLE: dict[str, float] = {
    "flow":   0.1,   # deep focus — time disappears
    "joy":    0.5,   # pleasant — time flies
    "normal": 1.0,   # baseline
    "stress": 2.0,   # unpleasant — time drags
    "bore":   3.0,   # tedium — time crawls
    "trauma": 5.0,   # acute distress — time almost stops
}


@dataclass
class TimeWarpResult:
    real_minutes: float
    perceived_minutes: float
    state: str
    coefficient: float
    message: str

    @property
    def ratio(self) -> float:
        """perceived / real — >1 means time felt longer, <1 means shorter."""
        if self.real_minutes == 0:
            return 1.0
        return self.perceived_minutes / self.real_minutes

    def __str__(self) -> str:
        direction = "slower" if self.ratio > 1 else "faster"
        return (
            f"[TimeWarp] state={self.state} coef={self.coefficient:.2f} | "
            f"real={self.real_minutes:.1f}m → perceived={self.perceived_minutes:.1f}m "
            f"({direction}) | {self.message}"
        )


class TimeWarpEngine:
    """
    Converts real elapsed time into subjective (perceived) time
    based on the agent's current NeuroState-compatible emotional state.

    Usage::

        engine = TimeWarpEngine()
        result = engine.warp(real_minutes=120.0, state="flow")
        print(result)
    """

    def __init__(self, warp_table: Optional[dict[str, float]] = None) -> None:
        self.warp_table: dict[str, float] = (
            dict(warp_table) if warp_table else dict(DEFAULT_WARP_TABLE)
        )

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def warp(self, real_minutes: float, state: str = "normal") -> TimeWarpResult:
        """Calculate perceived time from real time and emotional state."""
        if real_minutes < 0:
            raise ValueError(f"real_minutes must be >= 0, got {real_minutes}")

        coef = self.warp_table.get(state, self.warp_table["normal"])
        perceived = real_minutes * coef
        message = self._make_message(real_minutes, perceived, state)

        return TimeWarpResult(
            real_minutes=real_minutes,
            perceived_minutes=perceived,
            state=state,
            coefficient=coef,
            message=message,
        )

    def warp_from_neurostate(
        self,
        real_minutes: float,
        joy: float = 0.0,
        stress: float = 0.0,
        curiosity: float = 0.0,
        sorrow: float = 0.0,
    ) -> TimeWarpResult:
        """
        Derive perceived time directly from raw NeuroState values (0–100).

        The dominant emotion determines the base coefficient.
        Composite scoring blends multiple states smoothly.
        """
        state, coef = self._derive_state(joy=joy, stress=stress,
                                         curiosity=curiosity, sorrow=sorrow)
        perceived = real_minutes * coef
        message = self._make_message(real_minutes, perceived, state)

        return TimeWarpResult(
            real_minutes=real_minutes,
            perceived_minutes=perceived,
            state=state,
            coefficient=round(coef, 3),
            message=message,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _derive_state(
        self,
        joy: float,
        stress: float,
        curiosity: float,
        sorrow: float,
    ) -> tuple[str, float]:
        """Map raw NeuroState values to (dominant_state, coefficient)."""
        scores: dict[str, float] = {
            "joy":    joy,
            "stress": stress,
            "flow":   curiosity,   # high curiosity ≈ flow
            "bore":   sorrow,      # high sorrow ≈ bore/heaviness
        }
        dominant = max(scores, key=lambda k: scores[k])

        # Weighted blend across all dimensions (0–100 → 0.0–1.0)
        total = sum(scores.values()) or 1.0
        blended_coef = sum(
            (v / total) * self.warp_table.get(k, 1.0)
            for k, v in scores.items()
        )
        # Clamp to sane range
        blended_coef = max(0.05, min(blended_coef, 10.0))

        return dominant, blended_coef

    @staticmethod
    def _make_message(real: float, perceived: float, state: str) -> str:
        ratio = perceived / real if real > 0 else 1.0
        if ratio < 0.3:
            return f"Time vanished in {state} state — you lost track completely."
        if ratio < 0.8:
            return f"Time flew by in {state} state."
        if ratio < 1.2:
            return "Time passed at a normal pace."
        if ratio < 2.5:
            return f"Time dragged in {state} state."
        return f"Time nearly stopped — {state} was overwhelming."

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def register_state(self, name: str, coefficient: float) -> None:
        """Add or override a state in the warp table."""
        if coefficient <= 0:
            raise ValueError("coefficient must be > 0")
        self.warp_table[name] = coefficient

    def table(self) -> dict[str, float]:
        """Return a sorted copy of the warp table."""
        return dict(sorted(self.warp_table.items(), key=lambda x: x[1]))
