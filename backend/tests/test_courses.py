def test_create_course_uses_default_grading_scale(client, auth_headers):
    resp = client.post("/api/admin/courses", headers=auth_headers, json={"name": "Kompyuter savodxonligi"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Kompyuter savodxonligi"
    assert body["grading_scale"][0] == {"grade": "A", "min": 90}


def test_create_course_requires_auth(client):
    resp = client.post("/api/admin/courses", json={"name": "No auth"})
    assert resp.status_code == 401


def test_create_course_blank_name_rejected(client, auth_headers):
    resp = client.post("/api/admin/courses", headers=auth_headers, json={"name": "   "})
    assert resp.status_code == 422


def test_create_course_invalid_grading_scale_rejected(client, auth_headers):
    resp = client.post(
        "/api/admin/courses",
        headers=auth_headers,
        json={"name": "Bad scale", "grading_scale": []},
    )
    assert resp.status_code == 422


def test_list_and_get_course(client, auth_headers):
    create = client.post("/api/admin/courses", headers=auth_headers, json={"name": "Frontend"})
    course_id = create.json()["id"]

    listing = client.get("/api/admin/courses", headers=auth_headers)
    assert listing.status_code == 200
    assert any(c["id"] == course_id for c in listing.json())

    single = client.get(f"/api/admin/courses/{course_id}", headers=auth_headers)
    assert single.status_code == 200
    assert single.json()["name"] == "Frontend"


def test_update_course_grading_scale(client, auth_headers):
    create = client.post("/api/admin/courses", headers=auth_headers, json={"name": "Backend"})
    course_id = create.json()["id"]

    custom_scale = [{"grade": "Pass", "min": 60}, {"grade": "Fail", "min": 0}]
    update = client.put(
        f"/api/admin/courses/{course_id}",
        headers=auth_headers,
        json={"grading_scale": custom_scale},
    )
    assert update.status_code == 200
    assert update.json()["grading_scale"] == custom_scale


def test_delete_course_is_soft_and_hides_from_list(client, auth_headers):
    create = client.post("/api/admin/courses", headers=auth_headers, json={"name": "To delete"})
    course_id = create.json()["id"]

    delete = client.delete(f"/api/admin/courses/{course_id}", headers=auth_headers)
    assert delete.status_code == 204

    listing = client.get("/api/admin/courses", headers=auth_headers)
    assert all(c["id"] != course_id for c in listing.json())

    get_after_delete = client.get(f"/api/admin/courses/{course_id}", headers=auth_headers)
    assert get_after_delete.status_code == 404
