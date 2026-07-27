import json
from datetime import datetime, timedelta, timezone


def _create_course(client, auth_headers, name="Kompyuter savodxonligi"):
    resp = client.post("/api/admin/courses", headers=auth_headers, json={"name": name})
    return resp.json()["id"]


def _create_group(client, auth_headers, course_id, name="G1"):
    resp = client.post("/api/admin/groups", headers=auth_headers, json={"course_id": course_id, "name": name})
    return resp.json()["id"]


def _add_students(client, auth_headers, group_id, names):
    client.post(f"/api/admin/groups/{group_id}/students", headers=auth_headers, json={"text": "\n".join(names)})


def _add_questions(client, auth_headers, course_id, count):
    for i in range(count):
        client.post(
            f"/api/admin/courses/{course_id}/questions",
            headers=auth_headers,
            json={"text": f"Q{i}", "options": ["a", "b", "c", "d"], "correct_index": 0},
        )


def _create_open_exam(client, auth_headers, course_id, group_id, **overrides):
    payload = {
        "course_id": course_id,
        "group_id": group_id,
        "title": "Yakuniy imtihon",
        "starts_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        "duration_minutes": 30,
        "question_count": 3,
        "allow_resume": False,
        "show_result_to_student": True,
        "totp_digits": 6,
        "totp_period": 30,
    }
    payload.update(overrides)
    create = client.post("/api/admin/exams", headers=auth_headers, json=payload)
    exam_id = create.json()["id"]
    access_code = create.json()["access_code"]
    client.post(f"/api/admin/exams/{exam_id}/status", headers=auth_headers, json={"status": "open"})
    return exam_id, access_code


def _current_code(client, auth_headers, exam_id):
    resp = client.get(f"/api/admin/exams/{exam_id}/totp", headers=auth_headers)
    return resp.json()["code"]


def _setup_full_exam(client, auth_headers, **exam_overrides):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_students(client, auth_headers, group_id, ["Aliyev Vali", "Karimova Nodira"])
    _add_questions(client, auth_headers, course_id, 3)
    exam_id, access_code = _create_open_exam(client, auth_headers, course_id, group_id, **exam_overrides)
    return exam_id, access_code


def test_get_exam_status_public(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers)
    resp = client.get(f"/api/exam/{access_code}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Yakuniy imtihon"
    assert body["is_open_now"] is True


def test_verify_code_wrong_is_rejected(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers)
    resp = client.post(f"/api/exam/{access_code}/verify-code", json={"code": "000000"})
    assert resp.status_code == 403


def test_verify_code_correct_succeeds(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers)
    code = _current_code(client, auth_headers, exam_id)
    resp = client.post(f"/api/exam/{access_code}/verify-code", json={"code": code})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_list_students_shows_all_when_no_attempts(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers)
    code = _current_code(client, auth_headers, exam_id)
    resp = client.get(f"/api/exam/{access_code}/students", params={"code": code})
    assert resp.status_code == 200
    names = {s["full_name"] for s in resp.json()}
    assert names == {"Aliyev Vali", "Karimova Nodira"}


def test_full_flow_start_and_submit(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers)
    code = _current_code(client, auth_headers, exam_id)

    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()
    student_id = students[0]["id"]

    start = client.post(
        f"/api/exam/{access_code}/start", json={"student_id": student_id, "code": code}
    )
    assert start.status_code == 200
    body = start.json()
    assert "attempt_id" in body
    assert len(body["questions"]) == 3

    # correct_index must never leak to the student
    raw_text = json.dumps(body)
    assert "correct_index" not in raw_text

    # options may be shuffled per-attempt; answer with the option text known to be correct ("a")
    answers = {q["id"]: q["options"].index("a") for q in body["questions"]}
    submit = client.post(
        f"/api/exam/{access_code}/submit",
        json={"attempt_id": body["attempt_id"], "answers": answers},
    )
    assert submit.status_code == 200
    result = submit.json()
    assert result["score"] == 3
    assert result["total"] == 3
    assert result["percent"] == 100
    assert result["grade"] == "A"


def test_reentry_blocked_after_submit_when_resume_disabled(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers, allow_resume=False)
    code = _current_code(client, auth_headers, exam_id)

    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()
    student_id = students[0]["id"]

    start = client.post(f"/api/exam/{access_code}/start", json={"student_id": student_id, "code": code})
    attempt_id = start.json()["attempt_id"]
    answers = {q["id"]: 0 for q in start.json()["questions"]}
    client.post(f"/api/exam/{access_code}/submit", json={"attempt_id": attempt_id, "answers": answers})

    # blocked from student list now
    remaining = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()
    assert all(s["id"] != student_id for s in remaining)

    # blocked from starting a new attempt
    retry = client.post(f"/api/exam/{access_code}/start", json={"student_id": student_id, "code": code})
    assert retry.status_code == 409


def test_late_entry_gets_full_duration_not_truncated_by_shared_window(client, auth_headers):
    # starts_at is far enough in the past that the old shared start+duration window would
    # have already closed - a late student must still get their own full duration from the
    # moment they actually start, not be capped by that shared window.
    exam_id, access_code = _setup_full_exam(
        client,
        auth_headers,
        starts_at=(datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
        duration_minutes=10,
    )
    code = _current_code(client, auth_headers, exam_id)
    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()

    start = client.post(
        f"/api/exam/{access_code}/start", json={"student_id": students[0]["id"], "code": code}
    )
    assert start.status_code == 200
    ends_at = datetime.fromisoformat(start.json()["ends_at"].replace("Z", "+00:00"))
    assert ends_at > datetime.now(timezone.utc)


def test_resume_allowed_after_exam_closed_by_admin(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers, allow_resume=True)
    code = _current_code(client, auth_headers, exam_id)
    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()
    student_id = students[0]["id"]

    first = client.post(f"/api/exam/{access_code}/start", json={"student_id": student_id, "code": code})
    assert first.status_code == 200
    attempt_id = first.json()["attempt_id"]

    client.post(f"/api/admin/exams/{exam_id}/status", headers=auth_headers, json={"status": "closed"})

    resumed = client.post(f"/api/exam/{access_code}/start", json={"student_id": student_id, "code": code})
    assert resumed.status_code == 200
    assert resumed.json()["attempt_id"] == attempt_id


def test_new_start_rejected_after_exam_closed_by_admin(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers)
    code = _current_code(client, auth_headers, exam_id)
    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()

    client.post(f"/api/admin/exams/{exam_id}/status", headers=auth_headers, json={"status": "closed"})

    resp = client.post(
        f"/api/exam/{access_code}/start", json={"student_id": students[0]["id"], "code": code}
    )
    assert resp.status_code == 403


def test_start_rejects_wrong_code(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers)
    students_code = _current_code(client, auth_headers, exam_id)
    students = client.get(f"/api/exam/{access_code}/students", params={"code": students_code}).json()

    resp = client.post(
        f"/api/exam/{access_code}/start", json={"student_id": students[0]["id"], "code": "000000"}
    )
    assert resp.status_code == 403


def test_start_rejects_when_exam_not_open(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group_id = _create_group(client, auth_headers, course_id)
    _add_students(client, auth_headers, group_id, ["Aliyev Vali"])
    _add_questions(client, auth_headers, course_id, 3)

    payload = {
        "course_id": course_id,
        "group_id": group_id,
        "title": "Draft exam",
        "starts_at": datetime.now(timezone.utc).isoformat(),
        "duration_minutes": 30,
        "question_count": 3,
    }
    create = client.post("/api/admin/exams", headers=auth_headers, json=payload)
    exam_id = create.json()["id"]
    access_code = create.json()["access_code"]
    # status left as "draft" - never opened

    code = _current_code(client, auth_headers, exam_id)
    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()

    resp = client.post(
        f"/api/exam/{access_code}/start", json={"student_id": students[0]["id"], "code": code}
    )
    assert resp.status_code == 403


def test_show_result_false_hides_score(client, auth_headers):
    exam_id, access_code = _setup_full_exam(client, auth_headers, show_result_to_student=False)
    code = _current_code(client, auth_headers, exam_id)
    students = client.get(f"/api/exam/{access_code}/students", params={"code": code}).json()

    start = client.post(
        f"/api/exam/{access_code}/start", json={"student_id": students[0]["id"], "code": code}
    )
    answers = {q["id"]: 0 for q in start.json()["questions"]}
    submit = client.post(
        f"/api/exam/{access_code}/submit",
        json={"attempt_id": start.json()["attempt_id"], "answers": answers},
    )
    assert submit.status_code == 200
    assert submit.json() == {"submitted": True}
