from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "questions_sample.xlsx"


def _create_course(client, auth_headers, name="Kompyuter savodxonligi"):
    resp = client.post("/api/admin/courses", headers=auth_headers, json={"name": name})
    return resp.json()["id"]


def test_create_and_list_question(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    resp = client.post(
        f"/api/admin/courses/{course_id}/questions",
        headers=auth_headers,
        json={
            "text": "CPU nima?",
            "options": ["Protsessor", "Xotira", "Disk", "Monitor"],
            "correct_index": 0,
            "topic": "Apparat",
        },
    )
    assert resp.status_code == 201
    question_id = resp.json()["id"]

    listing = client.get(f"/api/admin/courses/{course_id}/questions", headers=auth_headers)
    assert listing.status_code == 200
    assert any(q["id"] == question_id for q in listing.json())


def test_create_question_invalid_correct_index_rejected(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    resp = client.post(
        f"/api/admin/courses/{course_id}/questions",
        headers=auth_headers,
        json={"text": "Q", "options": ["a", "b"], "correct_index": 5},
    )
    assert resp.status_code == 422


def test_filter_questions_by_topic_and_active(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    client.post(
        f"/api/admin/courses/{course_id}/questions",
        headers=auth_headers,
        json={"text": "Q1", "options": ["a", "b"], "correct_index": 0, "topic": "Apparat"},
    )
    client.post(
        f"/api/admin/courses/{course_id}/questions",
        headers=auth_headers,
        json={"text": "Q2", "options": ["a", "b"], "correct_index": 0, "topic": "Dasturlash"},
    )

    filtered = client.get(
        f"/api/admin/courses/{course_id}/questions", headers=auth_headers, params={"topic": "Apparat"}
    )
    assert filtered.status_code == 200
    assert all(q["topic"] == "Apparat" for q in filtered.json())
    assert len(filtered.json()) == 1


def test_update_question(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    create = client.post(
        f"/api/admin/courses/{course_id}/questions",
        headers=auth_headers,
        json={"text": "Old", "options": ["a", "b"], "correct_index": 0},
    )
    question_id = create.json()["id"]

    update = client.put(
        f"/api/admin/courses/{course_id}/questions/{question_id}",
        headers=auth_headers,
        json={"text": "New", "is_active": False},
    )
    assert update.status_code == 200
    assert update.json()["text"] == "New"
    assert update.json()["is_active"] is False


def test_delete_question_is_soft(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    create = client.post(
        f"/api/admin/courses/{course_id}/questions",
        headers=auth_headers,
        json={"text": "To delete", "options": ["a", "b"], "correct_index": 0},
    )
    question_id = create.json()["id"]

    delete = client.delete(f"/api/admin/courses/{course_id}/questions/{question_id}", headers=auth_headers)
    assert delete.status_code == 204

    listing = client.get(f"/api/admin/courses/{course_id}/questions", headers=auth_headers)
    assert all(q["id"] != question_id for q in listing.json())


def test_import_preview_does_not_persist(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    with open(FIXTURE_PATH, "rb") as f:
        resp = client.post(
            f"/api/admin/courses/{course_id}/questions/import",
            headers=auth_headers,
            files={"file": ("questions.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    # fixture file contains bad rows -> parser reports errors -> 422
    assert resp.status_code == 422
    body = resp.json()["detail"]
    assert body["questions_found"] == 3
    assert len(body["errors"]) == 3

    listing = client.get(f"/api/admin/courses/{course_id}/questions", headers=auth_headers)
    assert listing.json() == []


def test_import_confirm_persists_clean_file(client, auth_headers):
    import io

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["savol", "variant_A", "variant_B", "variant_C", "variant_D", "togri_javob", "mavzu"])
    ws.append(["CPU nima?", "Protsessor", "Xotira", "Disk", "Monitor", "A", "Apparat"])
    ws.append(["RAM nima?", "Operativ xotira", "Disk", "Ekran", "Sichqoncha", "1", "Apparat"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    course_id = _create_course(client, auth_headers)

    preview = client.post(
        f"/api/admin/courses/{course_id}/questions/import",
        headers=auth_headers,
        files={"file": ("clean.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert preview.status_code == 200
    assert preview.json()["questions_found"] == 2

    buf.seek(0)
    confirm = client.post(
        f"/api/admin/courses/{course_id}/questions/import",
        headers=auth_headers,
        data={"confirm": "true"},
        files={"file": ("clean.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert confirm.status_code == 200
    assert confirm.json()["imported"] == 2

    listing = client.get(f"/api/admin/courses/{course_id}/questions", headers=auth_headers)
    assert len(listing.json()) == 2


def test_download_sample_template(client, auth_headers):
    resp = client.get("/api/admin/samples/questions.xlsx", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/vnd.openxmlformats")


def test_download_sample_template_without_auth(client):
    # Sample downloads are plain <a href> links in the UI - browsers can't attach
    # a Bearer token to those, so this route must not require authentication.
    resp = client.get("/api/admin/samples/questions.xlsx")
    assert resp.status_code == 200
