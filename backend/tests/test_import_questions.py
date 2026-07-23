from pathlib import Path

from app.services.imports import parse_questions_xlsx

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "questions_sample.xlsx"


def _load_fixture_bytes() -> bytes:
    return FIXTURE_PATH.read_bytes()


def test_parse_valid_rows():
    result = parse_questions_xlsx(_load_fixture_bytes())
    assert len(result["questions"]) == 3

    first = result["questions"][0]
    assert first["text"] == "CPU nima?"
    assert first["options"] == ["Protsessor", "Xotira", "Disk", "Monitor"]
    assert first["correct_index"] == 0
    assert first["topic"] == "Apparat"


def test_parse_numeric_correct_answer():
    result = parse_questions_xlsx(_load_fixture_bytes())
    second = result["questions"][1]
    assert second["text"] == "RAM nima?"
    assert second["correct_index"] == 0  # "1" -> index 0


def test_parse_reports_errors_for_bad_rows():
    result = parse_questions_xlsx(_load_fixture_bytes())
    assert len(result["errors"]) == 3
    joined = " ".join(result["errors"])
    assert "savol matni bo'sh" in joined
    assert "kamida 2 ta variant" in joined
    assert "togri_javob noto'g'ri" in joined


def test_parse_header_only_file_returns_no_questions_no_errors():
    import io

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["savol", "variant_A", "variant_B", "togri_javob"])
    buf = io.BytesIO()
    wb.save(buf)

    result = parse_questions_xlsx(buf.getvalue())
    assert result["questions"] == []
    assert result["errors"] == []


def test_parse_missing_required_columns():
    import io

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["question", "option1"])
    buf = io.BytesIO()
    wb.save(buf)

    result = parse_questions_xlsx(buf.getvalue())
    assert result["questions"] == []
    assert len(result["errors"]) == 1
