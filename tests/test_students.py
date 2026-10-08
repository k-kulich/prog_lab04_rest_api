def _mk_tutor(client, payload):
    return client.post("/api/tutors", json=payload).json()["tutor"]["id"]


def test_create_and_get_student(client, tutor_payload, student_payload):
    tid = _mk_tutor(client, tutor_payload)
    student_payload["tutor_id"] = tid
    r = client.post("/api/students", json=student_payload)
    assert r.status_code == 200, r.text
    sid = r.json()["student"]["id"]
    assert r.json()["student"]["grade_level"] == 10

    r2 = client.get(f"/api/students/{sid}")
    assert r2.status_code == 200


def test_create_student_with_unknown_tutor_returns_400(client, student_payload):
    student_payload["tutor_id"] = 9999
    r = client.post("/api/students", json=student_payload)
    assert r.status_code == 400
    assert "tutor_id" in r.json()["reason"]


def test_list_students_of_tutor(client, tutor_payload, student_payload):
    tid = _mk_tutor(client, tutor_payload)
    student_payload["tutor_id"] = tid
    client.post("/api/students", json=student_payload)
    r = client.get(f"/api/tutors/{tid}/students")
    assert r.status_code == 200
    assert len(r.json()["list"]) == 1


def test_patch_student(client, tutor_payload, student_payload):
    tid = _mk_tutor(client, tutor_payload)
    student_payload["tutor_id"] = tid
    sid = client.post("/api/students", json=student_payload).json()["student"]["id"]
    r = client.patch(f"/api/students/{sid}", json={"grade_level": 11})
    assert r.status_code == 200
    assert r.json()["student"]["grade_level"] == 11


def test_delete_student(client, tutor_payload, student_payload):
    tid = _mk_tutor(client, tutor_payload)
    student_payload["tutor_id"] = tid
    sid = client.post("/api/students", json=student_payload).json()["student"]["id"]
    assert client.delete(f"/api/students/{sid}").status_code == 202
    assert client.get(f"/api/students/{sid}").status_code == 404