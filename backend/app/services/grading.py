def calc_percent(score: int, total: int) -> int:
    return 0 if total == 0 else round(score / total * 100)


def calc_grade(percent: int, scale: list[dict]) -> str:
    for item in sorted(scale, key=lambda x: x["min"], reverse=True):
        if percent >= item["min"]:
            return item["grade"]
    return scale[-1]["grade"] if scale else "F"
