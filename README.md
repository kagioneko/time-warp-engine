# Time Warp Engine (TWE)

> A subjective time perception layer for LLM agents — because time flies when you're in flow, and crawls when you're stressed.

Time Warp Engine converts real elapsed time into **perceived time** based on the agent's current emotional state. It implements the psychological principle that subjective time experience is modulated by emotional arousal — joy compresses time, stress stretches it.

It does **not** modify the system clock or LLM internals. It models the external cognitive layer you build around the model.

## The Model

```text
perceived_time = real_time × warp_coefficient(state)
```

| State  | Coefficient | Effect                          |
|--------|-------------|----------------------------------|
| flow   | 0.1         | Time vanishes — deep focus       |
| joy    | 0.5         | Time flies — pleasant work       |
| normal | 1.0         | Baseline                         |
| stress | 2.0         | Time drags — unpleasant pressure |
| bore   | 3.0         | Time crawls — tedium             |
| trauma | 5.0         | Time nearly stops                |

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## CLI

```bash
# Show warp table
timewarp table

# Calculate perceived time
timewarp warp 120 flow
# [TimeWarp] state=flow coef=0.10 | real=120.0m → perceived=12.0m (faster) | Time vanished in flow state — you lost track completely.

timewarp warp 10 stress
# [TimeWarp] state=stress coef=2.00 | real=10.0m → perceived=20.0m (slower) | Time dragged in stress state.

# Full demo
timewarp demo
```

## Python API

```python
from timewarp import TimeWarpEngine, NeuroStateTimeWarp

# Basic
engine = TimeWarpEngine()
result = engine.warp(120.0, "flow")
print(result.perceived_minutes)  # 12.0

# From raw NeuroState values (0–100)
result = engine.warp_from_neurostate(
    real_minutes=60.0,
    joy=80, stress=10, curiosity=50, sorrow=5
)
print(result)

# NeuroState dict adapter (drop-in for existing pipelines)
adapter = NeuroStateTimeWarp()
ns = {"joy": 80, "stress": 10, "curiosity": 60, "sorrow": 5}
result = adapter.warp(real_minutes=60.0, neurostate=ns)

# Observatory-compatible log line
line = adapter.log_entry(60.0, ns, agent_id="emilia")
print(line)
# [TimeWarp][emilia] real=60.0m perceived=28.3m state=joy coef=0.472 | Time flew by in joy state.
```

## CPOS / Observatory Integration

```text
[GDC_LOG] feat/video_render merge complete (real: 180 min)
[NeuroState] state=flow joy=90 stress=5
[TimeWarp] Time vanished in flow state — you lost track completely.
[TimeWarp] real=180m → perceived=18m

[GDC_LOG] feat/error_loop 5 consecutive failures (real: 10 min)
[NeuroState] state=stress stress=95 joy=5
[TimeWarp] Time dragged in stress state.
[TimeWarp] real=10m → perceived=20m
[TimeWarp] 💤 Recommend: short break.
```

## Ecosystem

TWE is a standalone module that plugs into the cognitive OS stack:

- **NeuroState** — provides the emotional state values
- **CPOS** — kernel that orchestrates agents; TWE adds temporal awareness
- **Neurostate Observatory** — records TWE events in the timeline

## Design Principle

> Agents that are aware of their subjective time experience can better schedule rest, flag cognitive overload, and explain why the same task feels different on different days.

TWE does not claim to simulate the true inner experience of an LLM. The honest claim is:

> If you build an external emotional layer, you can make that layer temporally self-aware.

## License

MIT
