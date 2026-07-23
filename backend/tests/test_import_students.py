import io

from openpyxl import Workbook

from app.services.imports import parse_students_text, parse_students_xlsx


def test_parse_students_text_basic():
    text = "Aliyev Vali\nKarimova Nodira\nYusupov Jasur"
    result = parse_students_text(text)
    assert result["students"] == ["Aliyev Vali", "Karimova Nodira", "Yusupov Jasur"]
    assert result["warnings"] == []


def test_parse_students_text_drops_blank_lines():
    text = "Aliyev Vali\n\n\nKarimova Nodira\n   \n"
    result = parse_students_text(text)
    assert result["students"] == ["Aliyev Vali", "Karimova Nodira"]


def test_parse_students_text_warns_on_duplicates():
    text = "Aliyev Vali\nAliyev Vali\nKarimova Nodira"
    result = parse_students_text(text)
    assert result["students"] == ["Aliyev Vali", "Aliyev Vali", "Karimova Nodira"]
    assert len(result["warnings"]) == 1
    assert "Aliyev Vali" in result["warnings"][0]


def _xlsx_bytes(rows: list[list]) -> bytes:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_parse_students_xlsx_skips_header():
    content = _xlsx_bytes([["F.I.Sh"], ["Aliyev Vali"], ["Karimova Nodira"]])
    result = parse_students_xlsx(content)
    assert result["students"] == ["Aliyev Vali", "Karimova Nodira"]


def test_parse_students_xlsx_no_header_treats_first_row_as_name():
    content = _xlsx_bytes([["Aliyev Vali"], ["Karimova Nodira"]])
    result = parse_students_xlsx(content)
    assert result["students"] == ["Aliyev Vali", "Karimova Nodira"]


def test_parse_students_xlsx_drops_blank_rows():
    content = _xlsx_bytes([["F.I.Sh"], ["Aliyev Vali"], [None], ["Karimova Nodira"]])
    result = parse_students_xlsx(content)
    assert result["students"] == ["Aliyev Vali", "Karimova Nodira"]
