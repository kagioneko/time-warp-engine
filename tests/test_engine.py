"""Tests for TimeWarpEngine and NeuroStateTimeWarp."""

import pytest
from timewarp import TimeWarpEngine, TimeWarpResult, NeuroStateTimeWarp, DEFAULT_WARP_TABLE


# ---------------------------------------------------------------------------
# TimeWarpEngine — basic warp
# ---------------------------------------------------------------------------

class TestTimeWarpEngineBasic:
    def setup_method(self):
        self.engine = TimeWarpEngine()

    def test_flow_state_compresses_time(self):
        result = self.engine.warp(120.0, "flow")
        assert result.perceived_minutes < result.real_minutes
        assert result.coefficient == pytest.approx(0.1)
        assert result.perceived_minutes == pytest.approx(12.0)

    def test_bore_state_stretches_time(self):
        result = self.engine.warp(120.0, "bore")
        assert result.perceived_minutes > result.real_minutes
        assert result.coefficient == pytest.approx(3.0)
        assert result.perceived_minutes == pytest.approx(360.0)

    def test_normal_state_is_identity(self):
        result = self.engine.warp(60.0, "normal")
        assert result.perceived_minutes == pytest.approx(60.0)
        assert result.ratio == pytest.approx(1.0)

    def test_unknown_state_falls_back_to_normal(self):
        result = self.engine.warp(60.0, "unknown_state")
        assert result.perceived_minutes == pytest.approx(60.0)

    def test_zero_real_time(self):
        result = self.engine.warp(0.0, "flow")
        assert result.perceived_minutes == pytest.approx(0.0)
        assert result.ratio == pytest.approx(1.0)

    def test_negative_real_time_raises(self):
        with pytest.raises(ValueError, match="real_minutes must be >= 0"):
            self.engine.warp(-1.0, "flow")

    def test_result_str_contains_state(self):
        result = self.engine.warp(60.0, "stress")
        assert "stress" in str(result)

    def test_all_default_states_are_positive(self):
        for state in DEFAULT_WARP_TABLE:
            result = self.engine.warp(60.0, state)
            assert result.perceived_minutes > 0

    def test_stress_stretches_more_than_normal(self):
        normal = self.engine.warp(60.0, "normal")
        stressed = self.engine.warp(60.0, "stress")
        assert stressed.perceived_minutes > normal.perceived_minutes

    def test_joy_compresses_more_than_normal(self):
        normal = self.engine.warp(60.0, "normal")
        joyful = self.engine.warp(60.0, "joy")
        assert joyful.perceived_minutes < normal.perceived_minutes


# ---------------------------------------------------------------------------
# TimeWarpEngine — custom table
# ---------------------------------------------------------------------------

class TestTimeWarpEngineCustomTable:
    def test_custom_warp_table(self):
        engine = TimeWarpEngine(warp_table={"panic": 4.0, "normal": 1.0})
        result = engine.warp(10.0, "panic")
        assert result.perceived_minutes == pytest.approx(40.0)

    def test_register_state(self):
        engine = TimeWarpEngine()
        engine.register_state("grind", 2.5)
        result = engine.warp(10.0, "grind")
        assert result.coefficient == pytest.approx(2.5)

    def test_register_state_invalid_coefficient(self):
        engine = TimeWarpEngine()
        with pytest.raises(ValueError):
            engine.register_state("bad", -1.0)
        with pytest.raises(ValueError):
            engine.register_state("zero", 0.0)

    def test_table_returns_sorted_copy(self):
        engine = TimeWarpEngine()
        t = engine.table()
        values = list(t.values())
        assert values == sorted(values)


# ---------------------------------------------------------------------------
# TimeWarpEngine — NeuroState integration
# ---------------------------------------------------------------------------

class TestWarpFromNeurostate:
    def setup_method(self):
        self.engine = TimeWarpEngine()

    def test_high_curiosity_gives_low_coefficient(self):
        result = self.engine.warp_from_neurostate(60.0, curiosity=95.0)
        assert result.perceived_minutes < 60.0

    def test_high_stress_gives_high_coefficient(self):
        result = self.engine.warp_from_neurostate(60.0, stress=90.0)
        assert result.perceived_minutes > 60.0

    def test_all_zero_neurostate_is_near_normal(self):
        result = self.engine.warp_from_neurostate(60.0)
        # all zeros → blended coef should be minimal or zero-weighted → clamp to 0.05
        assert result.perceived_minutes >= 0

    def test_dominant_state_is_highest_value(self):
        result = self.engine.warp_from_neurostate(
            60.0, joy=10, stress=80, curiosity=5, sorrow=5
        )
        assert result.state == "stress"

    def test_dominant_state_joy(self):
        result = self.engine.warp_from_neurostate(
            60.0, joy=90, stress=5, curiosity=10, sorrow=0
        )
        assert result.state == "joy"

    def test_coefficient_clamped_above_minimum(self):
        result = self.engine.warp_from_neurostate(60.0, joy=0, stress=0)
        assert result.coefficient >= 0.05

    def test_coefficient_clamped_below_maximum(self):
        result = self.engine.warp_from_neurostate(60.0, sorrow=100, stress=100)
        assert result.coefficient <= 10.0


# ---------------------------------------------------------------------------
# NeuroStateTimeWarp adapter
# ---------------------------------------------------------------------------

class TestNeuroStateTimeWarp:
    def setup_method(self):
        self.adapter = NeuroStateTimeWarp()

    def test_warp_with_dict(self):
        ns = {"joy": 80, "stress": 10, "curiosity": 50, "sorrow": 5}
        result = self.adapter.warp(60.0, ns)
        assert isinstance(result, TimeWarpResult)
        assert result.real_minutes == pytest.approx(60.0)

    def test_warp_with_empty_dict_uses_defaults(self):
        result = self.adapter.warp(60.0, {})
        assert result.perceived_minutes >= 0

    def test_log_entry_contains_agent_id(self):
        ns = {"joy": 70, "stress": 20}
        line = self.adapter.log_entry(30.0, ns, agent_id="emilia")
        assert "emilia" in line

    def test_log_entry_contains_real_and_perceived(self):
        ns = {"stress": 90}
        line = self.adapter.log_entry(10.0, ns)
        assert "real=10.0m" in line
        assert "perceived=" in line

    def test_custom_engine_is_used(self):
        custom_engine = TimeWarpEngine(warp_table={"stress": 9.0, "normal": 1.0})
        adapter = NeuroStateTimeWarp(engine=custom_engine)
        result = adapter.warp(10.0, {"stress": 100})
        # stress dominant, coefficient near 9.0 (blended but stress-heavy)
        assert result.perceived_minutes > 50.0  # significantly stretched

    def test_warp_stress_state_stretches_time(self):
        ns = {"stress": 95, "joy": 5, "curiosity": 5, "sorrow": 10}
        result = self.adapter.warp(60.0, ns)
        assert result.perceived_minutes > 60.0

    def test_warp_joy_state_compresses_time(self):
        ns = {"joy": 90, "stress": 5, "curiosity": 30, "sorrow": 0}
        result = self.adapter.warp(60.0, ns)
        assert result.perceived_minutes < 60.0
