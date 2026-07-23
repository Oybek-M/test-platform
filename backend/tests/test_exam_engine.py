from app.services.exam_engine import grade_attempt, pick_questions

SAMPLE_BANK = [
    {"id": 1, "text": "Q1", "options": ["a", "b", "c"], "correct_index": 0},
    {"id": 2, "text": "Q2", "options": ["a", "b"], "correct_index": 1},
    {"id": 3, "text": "Q3", "options": ["a", "b", "c", "d"], "correct_index": 2},
    {"id": 4, "text": "Q4", "options": ["a", "b"], "correct_index": 0},
]


def test_pick_questions_returns_requested_count():
    result = pick_questions(SAMPLE_BANK, count=2, shuffle_questions=True, shuffle_options=False)
    assert len(result) == 2
    ids = {q["id"] for q in result}
    assert ids.issubset({q["id"] for q in SAMPLE_BANK})


def test_pick_questions_no_shuffle_preserves_order_and_correct_index():
    result = pick_questions(SAMPLE_BANK, count=4, shuffle_questions=False, shuffle_options=False)
    assert [q["id"] for q in result] == [1, 2, 3, 4]
    for original, picked in zip(SAMPLE_BANK, result):
        assert picked["options"] == original["options"]
        assert picked["correct_index"] == original["correct_index"]


def test_pick_questions_shuffle_options_keeps_correct_value_pointed_to():
    for _ in range(20):  # run many times to shake out shuffle-related bugs
        result = pick_questions(SAMPLE_BANK, count=4, shuffle_questions=False, shuffle_options=True)
        for original, picked in zip(SAMPLE_BANK, result):
            correct_value = original["options"][original["correct_index"]]
            assert picked["options"][picked["correct_index"]] == correct_value
            assert sorted(picked["options"]) == sorted(original["options"])


def test_pick_questions_count_capped_at_pool_size():
    result = pick_questions(SAMPLE_BANK, count=100, shuffle_questions=True, shuffle_options=False)
    assert len(result) == len(SAMPLE_BANK)


def test_grade_attempt_all_correct():
    snapshot = [
        {"id": 1, "text": "Q1", "options": ["a", "b"], "correct_index": 0},
        {"id": 2, "text": "Q2", "options": ["a", "b"], "correct_index": 1},
    ]
    answers = {"1": 0, "2": 1}
    score, total = grade_attempt(snapshot, answers)
    assert (score, total) == (2, 2)


def test_grade_attempt_partial_and_missing_answers():
    snapshot = [
        {"id": 1, "text": "Q1", "options": ["a", "b"], "correct_index": 0},
        {"id": 2, "text": "Q2", "options": ["a", "b"], "correct_index": 1},
        {"id": 3, "text": "Q3", "options": ["a", "b"], "correct_index": 0},
    ]
    answers = {"1": 0, "2": 0}  # q2 wrong, q3 unanswered
    score, total = grade_attempt(snapshot, answers)
    assert (score, total) == (1, 3)


def test_grade_attempt_accepts_int_keys_too():
    snapshot = [{"id": 1, "text": "Q1", "options": ["a", "b"], "correct_index": 0}]
    answers = {1: 0}
    score, total = grade_attempt(snapshot, answers)
    assert (score, total) == (1, 1)
