def _mk_pair(client, tutor_payload, student_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    student_payload["tutor_id"] = tid
    sid = client.post("/api/students", json=student_payload).json()["student"]["id"]
    return tid, sid


def _lesson(tid, sid, **overrides):
    base = {
        "title": "Алгебра",
        "subject": "Математика",
        "topic": "Логарифмы",
        "start_at": "2025-12-01T15:00:00",
        "duration_min": 60,
        "lesson_url": "https://zoom.us/j/123",
        "description": "Разбор задач",
        "status": "scheduled",
        "tutor_id": tid,
        "student_id": sid,
    }
    base.update(overrides)
    return base


def test_create_and_get_lesson(client, tutor_payload, student_payload):
    tid, sid = _mk_pair(client, tutor_payload, student_payload)
    r = client.post("/api/lessons", json=_lesson(tid, sid))
    assert r.status_code == 200, r.text
    lid = r.json()["lesson"]["id"]
    assert r.json()["lesson"]["title"] == "Алгебра"
    assert client.get(f"/api/lessons/{lid}").status_code == 200


def test_create_lesson_with_unknown_tutor_returns_400(client, tutor_payload, student_payload):
    tid, sid = _mk_pair(client, tutor_payload, student_payload)
    body = _lesson(tid, sid, tutor_id=9999)
    r = client.post("/api/lessons", json=body)
    assert r.status_code == 400
    assert "tutor_id" in r.json()["reason"]


def test_student_of_wrong_tutor_returns_400(client, tutor_payload, student_payload):
    tid, sid = _mk_pair(client, tutor_payload, student_payload)
    tid2 = client.post(
        "/api/tutors",
        json={"fio": "Другой", "email": "x@y.z", "subject": "Физика"},
    ).json()["tutor"]["id"]
    r = client.post("/api/lessons", json=_lesson(tid2, sid))
    assert r.status_code == 400


def test_list_lessons_of_student(client, tutor_payload, student_payload):
    tid, sid = _mk_pair(client, tutor_payload, student_payload)
    client.post("/api/lessons", json=_lesson(tid, sid))
    r = client.get(f"/api/students/{sid}/lessons")
    assert r.status_code == 200
    assert len(r.json()["list"]) == 1


def test_patch_lesson(client, tutor_payload, student_payload):
    tid, sid = _mk_pair(client, tutor_payload, student_payload)
    lid = client.post("/api/lessons", json=_lesson(tid, sid)).json()["lesson"]["id"]
    r = client.patch(f"/api/lessons/{lid}", json={"status": "done"})
    assert r.status_code == 200
    assert r.json()["lesson"]["status"] == "done"


def test_delete_lesson(client, tutor_payload, student_payload):
    tid, sid = _mk_pair(client, tutor_payload, student_payload)
    lid = client.post("/api/lessons", json=_lesson(tid, sid)).json()["lesson"]["id"]
    assert client.delete(f"/api/lessons/{lid}").status_code == 202
    assert client.get(f"/api/lessons/{lid}").status_code == 404