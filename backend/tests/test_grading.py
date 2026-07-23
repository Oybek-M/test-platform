from app.services.grading import calc_grade, calc_percent

DEFAULT_SCALE = [
    {"grade": "A", "min": 90},
    {"grade": "B", "min": 80},
    {"grade": "C", "min": 70},
    {"grade": "D", "min": 60},
    {"grade": "F", "min": 0},
]


def test_calc_percent_basic():
    assert calc_percent(9, 10) == 90
    assert calc_percent(7, 10) == 70
    assert calc_percent(5, 10) == 50


def test_calc_percent_zero_total_is_zero():
    assert calc_percent(0, 0) == 0


def test_calc_percent_rounds():
    assert calc_percent(1, 3) == 33
    assert calc_percent(2, 3) == 67


def test_calc_grade_boundaries_default_scale():
    assert calc_grade(90, DEFAULT_SCALE) == "A"
    assert calc_grade(70, DEFAULT_SCALE) == "C"
    assert calc_grade(50, DEFAULT_SCALE) == "F"
    assert calc_grade(0, DEFAULT_SCALE) == "F"
    assert calc_grade(100, DEFAULT_SCALE) == "A"


def test_calc_grade_custom_scale():
    custom = [{"grade": "Pass", "min": 60}, {"grade": "Fail", "min": 0}]
    assert calc_grade(75, custom) == "Pass"
    assert calc_grade(59, custom) == "Fail"


def test_calc_grade_end_to_end_with_percent():
    percent = calc_percent(9, 10)
    assert calc_grade(percent, DEFAULT_SCALE) == "A"
    percent = calc_percent(5, 10)
    assert calc_grade(percent, DEFAULT_SCALE) == "F"
