import random


def pick_questions(
    active_questions: list[dict],
    count: int,
    shuffle_questions: bool,
    shuffle_options: bool,
) -> list[dict]:
    """Select and prepare the question set presented to a single exam attempt.

    active_questions: [{"id", "text", "options", "correct_index"}, ...] from the course bank.
    Returns `count` items shaped the same way; when shuffle_options is on, each item's
    options are reordered and correct_index is remapped to match the new order - the
    original question records are never mutated.
    """
    pool = list(active_questions)
    if shuffle_questions:
        chosen = random.sample(pool, min(count, len(pool)))
    else:
        chosen = pool[:count]

    presented = []
    for q in chosen:
        options = list(q["options"])
        correct_index = q["correct_index"]
        if shuffle_options:
            correct_value = options[correct_index]
            random.shuffle(options)
            correct_index = options.index(correct_value)
        presented.append(
            {
                "id": q["id"],
                "text": q["text"],
                "options": options,
                "correct_index": correct_index,
            }
        )
    return presented


def grade_attempt(question_snapshot: list[dict], answers: dict) -> tuple[int, int]:
    """Grade an attempt against its own presented-question snapshot.

    answers keys may arrive as int or str question ids (JSON always uses string keys).
    """
    total = len(question_snapshot)
    score = 0
    for q in question_snapshot:
        selected = answers.get(q["id"], answers.get(str(q["id"])))
        if selected is not None and selected == q["correct_index"]:
            score += 1
    return score, total
