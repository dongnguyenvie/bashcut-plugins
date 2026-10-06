"""Safe scene motion settings and FFmpeg zoom/pan expressions."""

import math
from typing import Any, Dict, List


DEFAULT_MOTION = {"type": "none", "strength": "subtle"}
MOTION_TYPES = {
    "none", "zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up",
    "pan_down", "drift_left", "drift_right", "shake",
}
MOTION_STRENGTHS = {"subtle", "medium"}


def normalize_motion(value: Any) -> Dict[str, str]:
    """Return a supported motion, falling back as a whole for malformed input."""
    if (not isinstance(value, dict)
            or not isinstance(value.get("type"), str)
            or not isinstance(value.get("strength"), str)
            or value["type"] not in MOTION_TYPES
            or value["strength"] not in MOTION_STRENGTHS):
        return DEFAULT_MOTION.copy()
    return {"type": value["type"], "strength": value["strength"]}


def _motion_range(motion: Dict[str, str]):
    kind, strength = motion["type"], motion["strength"]
    if kind == "zoom_in":
        return (1, 1.05 if strength == "subtle" else 1.10, 0, 0, 0, 0)
    if kind == "zoom_out":
        return (1.05 if strength == "subtle" else 1.10, 1, 0, 0, 0, 0)
    if kind.startswith("pan_"):
        distance = 0.03 if strength == "subtle" else 0.06
        # Six percent travel needs at least 1.12x to keep the image edge covered.
        scale = 1.06 if strength == "subtle" else 1.12
        x = distance * (1 if kind == "pan_right" else -1 if kind == "pan_left" else 0)
        y = distance * (1 if kind == "pan_down" else -1 if kind == "pan_up" else 0)
        return (scale, scale, 0, x, 0, y)
    if kind.startswith("drift_"):
        if strength == "subtle":
            start_scale, end_scale, start_x, end_x = 1.03, 1.06, 0.01, -0.02
        else:
            start_scale, end_scale, start_x, end_x = 1.04, 1.09, 0.02, -0.04
        direction = 1 if kind == "drift_left" else -1
        return (start_scale, end_scale, start_x * direction, end_x * direction, 0, 0)
    return (1, 1, 0, 0, 0, 0)


def get_motion_values(motion: Any, progress: float, frame: int, fps: int) -> Dict[str, float]:
    """Evaluate a motion at scene progress (translations are frame fractions or pixels)."""
    setting = normalize_motion(motion)
    progress = max(0.0, min(1.0, progress))
    eased = (1 - math.cos(math.pi * progress)) / 2
    start_scale, end_scale, start_x, end_x, start_y, end_y = _motion_range(setting)
    result = {
        "scale": start_scale + (end_scale - start_scale) * eased,
        "translate_x": start_x + (end_x - start_x) * eased,
        "translate_y": start_y + (end_y - start_y) * eased,
        "translate_x_px": 0.0,
        "translate_y_px": 0.0,
    }
    if setting["type"] == "shake" and fps > 0:
        amplitude = 2 if setting["strength"] == "subtle" else 4
        envelope = math.sin(math.pi * progress) ** 2
        result["translate_x_px"] = amplitude * envelope * math.sin(2 * math.pi * 11 * frame / fps)
        result["translate_y_px"] = amplitude * envelope * math.cos(2 * math.pi * 13 * frame / fps)
    return result


