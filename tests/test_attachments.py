def _mk_lesson_and_hw(client, tutor_payload, student_payload):
    tid = client.post("/api/tutors", json=tutor_payload).json()["tutor"]["id"]
    student_payload["tutor_id"] = tid
    sid = client.post("/api/students", json=student_payload).json()["student"]["id"]
    lid = client.post(
        "/api/lessons",
        json={
            "title": "L",
            "subject": "S",
            "start_at": "2025-12-01T15:00:00",
            "duration_min": 60,
            "tutor_id": tid,
            "student_id": sid,
        },
    ).json()["lesson"]["id"]
    hwid = client.post(
        "/api/homework",
        json={
            "title": "H",
            "due_date": "2025-12-05",
            "lesson_id": lid,
        },
    ).json()["homework"]["id"]
    return lid, hwid


def test_create_attachment_for_lesson(client, tutor_payload, student_payload):
    lid, _ = _mk_lesson_and_hw(client, tutor_payload, student_payload)
    r = client.post(
        "/api/attachments",
        json={
            "kind": "link",
            "name": "Zoom",
            "url": "https://zoom.us/j/123",
            "lesson_id": lid,
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["attachment"]["kind"] == "link"


def test_create_attachment_for_homework(client, tutor_payload, student_payload):
    _, hwid = _mk_lesson_and_hw(client, tutor_payload, student_payload)
    r = client.post(
        "/api/attachments",
        json={
            "kind": "file",
            "name": "solution.pdf",
            "url": "https://cloud/solution.pdf",
            "homework_id": hwid,
        },
    )
    assert r.status_code == 200


def test_attachment_needs_exactly_one_owner(client, tutor_payload, student_payload):
    lid, hwid = _mk_lesson_and_hw(client, tutor_payload, student_payload)

    r = client.post(
        "/api/attachments",
        json={"kind": "link", "name": "x", "url": "https://x"},
    )
    assert r.status_code == 400

    r = client.post(
        "/api/attachments",
        json={
            "kind": "link",
            "name": "x",
            "url": "https://x",
            "lesson_id": lid,
            "homework_id": hwid,
        },
    )
    assert r.status_code == 400


def test_list_lesson_attachments(client, tutor_payload, student_payload):
    lid, _ = _mk_lesson_and_hw(client, tutor_payload, student_payload)
    for i in range(3):
        client.post(
            "/api/attachments",
            json={
                "kind": "material",
                "name": f"m{i}",
                "url": f"https://m/{i}",
                "lesson_id": lid,
            },
        )
    r = client.get(f"/api/lessons/{lid}/attachments")
    assert r.status_code == 200
    assert len(r.json()["list"]) == 3


def test_patch_attachment(client, tutor_payload, student_payload):
    lid, _ = _mk_lesson_and_hw(client, tutor_payload, student_payload)
    aid = client.post(
        "/api/attachments",
        json={"kind": "link", "name": "x", "url": "https://x", "lesson_id": lid},
    ).json()["attachment"]["id"]
    r = client.patch(f"/api/attachments/{aid}", json={"name": "renamed"})
    assert r.status_code == 200
    assert r.json()["attachment"]["name"] == "renamed"


def test_delete_attachment(client, tutor_payload, student_payload):
    lid, _ = _mk_lesson_and_hw(client, tutor_payload, student_payload)
    aid = client.post(
        "/api/attachments",
        json={"kind": "link", "name": "x", "url": "https://x", "lesson_id": lid},
    ).json()["attachment"]["id"]
    assert client.delete(f"/api/attachments/{aid}").status_code == 202
    assert client.get(f"/api/attachments/{aid}").status_code == 404