def scale_bars(values, width=50):
    if type(width) is not int or not 1 <= width <= 200:
        raise ValueError("width must be an integer between 1 and 200")
    if not isinstance(values, list) or any(
        type(v) is not int or v < 0 for v in values
    ):
        raise ValueError("values must be a list of non-negative integers")

    peak = max(values, default=0)
    if not peak:
        return [0] * len(values)
    return [max(1, (v * width + peak // 2) // peak) if v else 0 for v in values]
