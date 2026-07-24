def _create_course(client, auth_headers, name="Kompyuter savodxonligi"):
    resp = client.post("/api/admin/courses", headers=auth_headers, json={"name": name})
    return resp.json()["id"]


def test_create_and_list_group(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    resp = client.post(
        "/api/admin/groups", headers=auth_headers, json={"course_id": course_id, "name": "KS-2026-Iyul"}
    )
    assert resp.status_code == 201
    group_id = resp.json()["id"]

    listing = client.get("/api/admin/groups", headers=auth_headers, params={"course_id": course_id})
    assert listing.status_code == 200
    assert any(g["id"] == group_id for g in listing.json())


def test_update_and_delete_group(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    create = client.post("/api/admin/groups", headers=auth_headers, json={"course_id": course_id, "name": "Old"})
    group_id = create.json()["id"]

    update = client.put(f"/api/admin/groups/{group_id}", headers=auth_headers, json={"name": "New"})
    assert update.status_code == 200
    assert update.json()["name"] == "New"

    delete = client.delete(f"/api/admin/groups/{group_id}", headers=auth_headers)
    assert delete.status_code == 204

    listing = client.get("/api/admin/groups", headers=auth_headers, params={"course_id": course_id})
    assert all(g["id"] != group_id for g in listing.json())


def test_add_students_via_text(client, auth_headers):
    course_id = _create_course(client, auth_headers)
    group = client.post("/api/admin/groups", headers=auth_headers, json={"course_id": course_id, "name": "G1"})
    group_id = group.json()["id"]

    resp = client.post(
        f"/api/admin/groups/{group_id}/students",
        headers=auth_headers,
        json={"text": "Aliyev Vali\nKarimova Nodira\n\nYusupov Jasur"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["created"]) == 3
    assert body["warnings"] == []

    listing = client.get(f"/api/admin/groups/{group_id}/students", headers=auth_headers)
    assert len(listing.json()) == 3


def test_add_students_via_xlsx(client, auth_headers):
    import io

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["F.I.Sh"])
    ws.append(["Aliyev Vali"])
    ws.append(["Karimova Nodira"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    course_id = _create_course(client, auth_headers)
    group = client.post("/api/admin/groups", headers=auth_headers, json={"course_id": course_id, "name": "G1"})
    group_id = group.json()["id"]

    resp = client.post(
        f"/api/admin/groups/{group_id}/students/import",
        headers=auth_headers,
        files={"file": ("students.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert resp.status_code == 201
    assert len(resp.json()["created"]) == 2


def test_download_students_sample(client, auth_headers):
    resp = client.get("/api/admin/samples/students.xlsx", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/vnd.openxmlformats")


def test_download_students_sample_without_auth(client):
    # Sample downloads are plain <a href> links in the UI - browsers can't attach
    # a Bearer token to those, so this route must not require authentication.
    resp = client.get("/api/admin/samples/students.xlsx")
    assert resp.status_code == 200
