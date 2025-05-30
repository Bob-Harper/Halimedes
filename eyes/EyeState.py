from dataclasses import dataclass


@dataclass
class EyeState:
    x: int = 90
    y: int = 90
    pupil: float = 1.0
    expression: str = "neutral"
    blink: float = 0.0
    name: str = "default"
    eyelid_cfg: dict | None = None  # overrides from interpolated expression/blink