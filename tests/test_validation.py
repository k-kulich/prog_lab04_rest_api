def test_missing_required_field_message(client):
    r = client.post("/api/tutors", json={"email": "a@b.c", "subject": "S"})
    assert r.status_code == 400
    assert r.json() == {"status": 400, "reason": "Field 'fio' is required"}


def test_too_long_field(client):
    r = client.post(
        "/api/tutors",
        json={"fio": "x" * 200, "email": "a@b.c", "subject": "S"},
    )
    assert r.status_code == 400
    assert "at most 100" in r.json()["reason"]


def test_invalid_grade_level_range(client, tutor_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    r = client.post(
        "/api/students",
        json={
            "fio": "И",
            "email": "s@e.ru",
            "birth_date": "2007-05-12",
            "grade_level": 99,
            "tutor_id": tid,
        },
    )
    assert r.status_code == 400
    assert "Field 'grade_level'" in r.json()["reason"]
    assert "less then 11" in r.json()["reason"]


def test_invalid_status_literal(client, tutor_payload, student_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    student_payload["tutor_id"] = tid
    sid = client.post("/api/students", json=student_payload).json()["student"]["id"]
    r = client.post(
        "/api/lessons",
        json={
            "title": "L",
            "subject": "S",
            "start_at": "2025-12-01T15:00:00",
            "duration_min": 60,
            "status": "bogus",
            "tutor_id": tid,
            "student_id": sid,
        },
    )
    assert r.status_code == 400
    assert "status" in r.json()["reason"]


def test_invalid_email(client):
    r = client.post(
        "/api/tutors",
        json={"fio": "A", "email": "not-an-email", "subject": "S"},
    )
    assert r.status_code == 400
    assert "email" in r.json()["reason"]


def test_invalid_date_format(client, tutor_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    r = client.post(
        "/api/students",
        json={
            "fio": "И",
            "email": "s@e.ru",
            "birth_date": "12/05/2007",
            "grade_level": 5,
            "tutor_id": tid,
        },
    )
    assert r.status_code == 400


def test_not_found_returns_404_with_body(client):
    r = client.get("/api/tutors/9999")
    assert r.status_code == 404
    assert r.json()["status"] == 404
    assert "not found" in r.json()["reason"]


def test_invalid_json_body(client):
    r = client.post(
        "/api/tutors",
        content="{ not a json }",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400