def _mk_lesson(client, tutor_payload, student_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    student_payload["tutor_id"] = tid
    sid = client.post("/api/students", json=student_payload).json()["student"]["id"]
    lesson_body = {
        "title": "Алгебра",
        "subject": "Математика",
        "start_at": "2025-12-01T15:00:00",
        "duration_min": 60,
        "tutor_id": tid,
        "student_id": sid,
    }
    lid = client.post("/api/lessons", json=lesson_body).json()["lesson"]["id"]
    return lid


def _hw(lid, **overrides):
    base = {
        "title": "ДЗ №1",
        "description": "Решить 10 примеров",
        "due_date": "2025-12-05",
        "status": "assigned",
        "grade": None,
        "lesson_id": lid,
    }
    base.update(overrides)
    return base


def test_create_and_get_homework(client, tutor_payload, student_payload):
    lid = _mk_lesson(client, tutor_payload, student_payload)
    r = client.post("/api/homework", json=_hw(lid))
    assert r.status_code == 200, r.text
    hwid = r.json()["homework"]["id"]
    assert r.json()["homework"]["title"] == "ДЗ №1"

    r2 = client.get(f"/api/homework/{hwid}")
    assert r2.status_code == 200


def test_create_homework_with_unknown_lesson_returns_400(client):
    r = client.post("/api/homework", json=_hw(9999))
    assert r.status_code == 400
    assert "lesson_id" in r.json()["reason"]


def test_list_lesson_homework(client, tutor_payload, student_payload):
    lid = _mk_lesson(client, tutor_payload, student_payload)
    client.post("/api/homework", json=_hw(lid))
    client.post("/api/homework", json=_hw(lid, title="ДЗ №2"))
    r = client.get(f"/api/lessons/{lid}/homework")
    assert r.status_code == 200
    assert len(r.json()["list"]) == 2


def test_student_homework_endpoint(client, tutor_payload, student_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    student_payload["tutor_id"] = tid
    sid = client.post("/api/students", json=student_payload).json()["student"]["id"]
    lesson_body = {
        "title": "L",
        "subject": "S",
        "start_at": "2025-12-01T15:00:00",
        "duration_min": 60,
        "tutor_id": tid,
        "student_id": sid,
    }
    lid = client.post("/api/lessons", json=lesson_body).json()["lesson"]["id"]
    client.post("/api/homework", json=_hw(lid))
    r = client.get(f"/api/students/{sid}/homework")
    assert r.status_code == 200
    assert len(r.json()["list"]) == 1


def test_patch_homework_grade(client, tutor_payload, student_payload):
    lid = _mk_lesson(client, tutor_payload, student_payload)
    hwid = client.post("/api/homework", json=_hw(lid)).json()["homework"]["id"]
    r = client.patch(f"/api/homework/{hwid}", json={"status": "graded", "grade": 95})
    assert r.status_code == 200
    assert r.json()["homework"]["status"] == "graded"
    assert r.json()["homework"]["grade"] == 95


def test_delete_homework(client, tutor_payload, student_payload):
    lid = _mk_lesson(client, tutor_payload, student_payload)
    hwid = client.post("/api/homework", json=_hw(lid)).json()["homework"]["id"]
    assert client.delete(f"/api/homework/{hwid}").status_code == 202
    assert client.get(f"/api/homework/{hwid}").status_code == 404