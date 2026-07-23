from datetime import datetime, timedelta, timezone


def _create_course(client, auth_headers, name="Kompyuter savodxonligi"):
    resp = client.post("/api/admin/courses", headers=auth_headers, json={"name": name})
    return resp.json()["id"]


def _create_group(client, auth_headers, course_id, name="G1"):
    resp = client.post("/api/admin/groups", headers=auth_headers, json={"course_id": course_id, "name": name})
    return resp.json()["id"]


def _add_questions(client, auth_headers, course_id, count):
    for i in range(count):
        client.post(
            f"/api/admin/courses/{course_id}/questions",
            headers=auth_headers,
            json={"text": f"Q{i}", "options": ["a", "b"], "correct_index": 0},
        )


def _exam_payload(course_id, group_id, **overrides):
    payload = {
        "course_id": course_id,
        "group_id": group_id,
        "title": "Yakuniy imtihon",
        "starts_at": datetime.now(timezone.utc).isoformat(),
        "duration_minutes": 30,
        "question_count": 5,
        "totp_digits": 6,
        "totp_period": 30,
    }
    payload.update(overrides)
    return payload


def test_create_exam_hides_totp_secret(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_questions(client, auth_headers, course_id, 5)

    resp = client.post("/api/admin/exams", headers=auth_headers, json=_exam_payload(course_id, group_id))
    assert resp.status_code == 201
    body = resp.json()
    assert "totp_secret" not in body
    assert body["status"] == "draft"
    assert len(body["access_code"]) >= 6


def test_create_exam_question_count_exceeds_available_rejected(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_questions(client, auth_headers, course_id, 2)

    resp = client.post(
        "/api/admin/exams", headers=auth_headers, json=_exam_payload(course_id, group_id, question_count=5)
    )
    assert resp.status_code == 422


def test_create_exam_invalid_totp_settings_rejected(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_questions(client, auth_headers, course_id, 5)

    resp = client.post(
        "/api/admin/exams", headers=auth_headers, json=_exam_payload(course_id, group_id, totp_digits=5)
    )
    assert resp.status_code == 422

    resp2 = client.post(
        "/api/admin/exams", headers=auth_headers, json=_exam_payload(course_id, group_id, totp_period=45)
    )
    assert resp2.status_code == 422


def test_exam_status_transition(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_questions(client, auth_headers, course_id, 5)
    create = client.post("/api/admin/exams", headers=auth_headers, json=_exam_payload(course_id, group_id))
    exam_id = create.json()["id"]

    resp = client.post(f"/api/admin/exams/{exam_id}/status", headers=auth_headers, json={"status": "open"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "open"

    bad = client.post(f"/api/admin/exams/{exam_id}/status", headers=auth_headers, json={"status": "bogus"})
    assert bad.status_code == 422


def test_exam_live_totp_code_matches_configured_digits(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_questions(client, auth_headers, course_id, 5)
    create = client.post(
        "/api/admin/exams",
        headers=auth_headers,
        json=_exam_payload(course_id, group_id, totp_digits=4, totp_period=60),
    )
    exam_id = create.json()["id"]

    resp = client.get(f"/api/admin/exams/{exam_id}/totp", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["code"]) == 4
    assert 0 < body["seconds_left"] <= 60


def test_update_exam_question_count_validated_against_active_questions(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_questions(client, auth_headers, course_id, 3)
    create = client.post(
        "/api/admin/exams", headers=auth_headers, json=_exam_payload(course_id, group_id, question_count=3)
    )
    exam_id = create.json()["id"]

    resp = client.put(f"/api/admin/exams/{exam_id}", headers=auth_headers, json={"question_count": 10})
    assert resp.status_code == 422


def test_delete_exam_is_soft(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_questions(client, auth_headers, course_id, 5)
    create = client.post("/api/admin/exams", headers=auth_headers, json=_exam_payload(course_id, group_id))
    exam_id = create.json()["id"]

    delete = client.delete(f"/api/admin/exams/{exam_id}", headers=auth_headers)
    assert delete.status_code == 204

    listing = client.get("/api/admin/exams", headers=auth_headers, params={"course_id": course_id})
    assert all(e["id"] != exam_id for e in listing.json())


def test_exam_results_reflects_completed_attempt(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    client.post(
        f"/api/admin/groups/{group_id}/students", headers=auth_headers, json={"text": "Aliyev Vali"}
    )
    _add_questions(client, auth_headers, course_id, 3)

    payload = _exam_payload(
        course_id,
        group_id,
        question_count=3,
        starts_at=(datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        shuffle_options=False,
    )
    create = client.post("/api/admin/exams", headers=auth_headers, json=payload)
    exam_id = create.json()["id"]
    access_code = create.json()["access_code"]
    client.post(f"/api/admin/exams/{exam_id}/status", headers=auth_headers, json={"status": "open"})

    empty_results = client.get(f"/api/admin/exams/{exam_id}/results", headers=auth_headers)
    assert empty_results.status_code == 200
    assert empty_results.json() == []

    code = client.get(f"/api/admin/exams/{exam_id}/totp", headers=auth_headers).json()["code"]
    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()
    student_id = students[0]["id"]

    start = client.post(f"/api/exam/{access_code}/start", json={"student_id": student_id, "code": code})
    answers = {q["id"]: 0 for q in start.json()["questions"]}
    client.post(
        f"/api/exam/{access_code}/submit",
        json={"attempt_id": start.json()["attempt_id"], "answers": answers},
    )

    results = client.get(f"/api/admin/exams/{exam_id}/results", headers=auth_headers).json()
    assert len(results) == 1
    assert results[0]["student_name"] == "Aliyev Vali"
    assert results[0]["score"] == 3
    assert results[0]["total"] == 3
    assert results[0]["percent"] == 100
    assert results[0]["grade"] == "A"
    assert results[0]["status"] == "submitted"
