def test_list_tutors_empty(client):
    r = client.get("/api/tutors")
    assert r.status_code == 200
    assert r.json() == {"list": []}


def test_create_and_get_tutor(client, tutor_payload):
    r = client.post("/api/tutors", json=tutor_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "tutor" in body
    tid = body["tutor"]["id"]
    assert body["tutor"]["fio"] == "Иван Петров"

    r2 = client.get(f"/api/tutors/{tid}")
    assert r2.status_code == 200
    assert r2.json()["tutor"]["email"] == "ivan@example.com"


def test_create_tutor_wrapped_body(client, tutor_payload):
    r = client.post("/api/tutors", json={"tutor": tutor_payload})
    assert r.status_code == 200
    assert r.json()["tutor"]["subject"] == "Математика"


def test_get_missing_tutor_returns_404(client):
    r = client.get("/api/tutors/9999")
    assert r.status_code == 404


def test_patch_tutor(client, tutor_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    r = client.patch(f"/api/tutors/{tid}", json={"subject": "Физика"})
    assert r.status_code == 200
    assert r.json()["tutor"]["subject"] == "Физика"
    assert r.json()["tutor"]["fio"] == "Иван Петров"


def test_patch_missing_returns_404(client):
    r = client.patch("/api/tutors/9999", json={"subject": "X"})
    assert r.status_code == 404


def test_delete_tutor(client, tutor_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    r = client.delete(f"/api/tutors/{tid}")
    assert r.status_code == 202
    assert client.get(f"/api/tutors/{tid}").status_code == 404


def test_delete_missing_returns_404(client):
    assert client.delete("/api/tutors/9999").status_code == 404