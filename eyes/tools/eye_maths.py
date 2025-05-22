def quantize_pupil(pupil: float, min_val=0.8, max_val=1.05) -> float:
    clamped = max(min(pupil, max_val), min_val)
    quantized = round(clamped / 0.01) * 0.01
    return round(quantized, 2)
