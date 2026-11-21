def test_create_assigns_sequential_numbers(new_ticket) -> None:
    first = new_ticket()
    second = new_ticket(short_description="Outlook keeps asking for password")
    assert first["number"] == "INC0010001"
    assert second["number"] == "INC0010002"
    assert first["status"] == "new"
    assert first["priority"] == "3-moderate"


def test_create_validates_input(client) -> None:
    res = client.post("/tickets", json={"short_description": "hi", "description": "", "caller": ""})
    assert res.status_code == 422


def test_get_ticket(client, new_ticket) -> None:
    created = new_ticket()
    res = client.get(f"/tickets/{created['number']}")
    assert res.status_code == 200
    assert res.json()["short_description"] == created["short_description"]


def test_get_missing_ticket_is_404(client) -> None:
    assert client.get("/tickets/INC0099999").status_code == 404


def test_get_rejects_malformed_number(client) -> None:
    assert client.get("/tickets/not-a-ticket").status_code == 422


def test_list_newest_first_with_paging(client, new_ticket) -> None:
    for i in range(3):
        new_ticket(short_description=f"Printer jam on floor {i}")
    res = client.get("/tickets", params={"limit": 2})
    body = res.json()
    assert body["total"] == 3
    assert [t["number"] for t in body["items"]] == ["INC0010003", "INC0010002"]

    page2 = client.get("/tickets", params={"limit": 2, "skip": 2}).json()
    assert [t["number"] for t in page2["items"]] == ["INC0010001"]


def test_list_filters(client, new_ticket) -> None:
    new_ticket(priority="1-critical")
    new_ticket(short_description="Laptop screen flickers", description="Dell XPS display")
    crit = client.get("/tickets", params={"priority": "1-critical"}).json()
    assert crit["total"] == 1

    search = client.get("/tickets", params={"q": "flicker"}).json()
    assert [t["short_description"] for t in search["items"]] == ["Laptop screen flickers"]

    assert client.get("/tickets", params={"status": "new"}).json()["total"] == 2
    assert client.get("/tickets", params={"status": "resolved"}).json()["total"] == 0


def test_update_only_changes_sent_fields(client, new_ticket) -> None:
    t = new_ticket()
    res = client.patch(
        f"/tickets/{t['number']}",
        json={"status": "in_progress", "assignment_group": "Network Ops"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "in_progress"
    assert body["assignment_group"] == "Network Ops"
    assert body["short_description"] == t["short_description"]
    assert body["updated_at"] > t["updated_at"]


def test_update_cannot_resolve_directly(client, new_ticket) -> None:
    t = new_ticket()
    res = client.patch(f"/tickets/{t['number']}", json={"status": "resolved"})
    assert res.status_code == 422


def test_update_resolved_ticket_keeps_status(client, new_ticket) -> None:
    # The edit form sends the current status back; that must not count as "resolving".
    t = new_ticket()
    client.post(
        f"/tickets/{t['number']}/resolve",
        json={"resolution_notes": "Replaced the network cable.", "resolved_by": "asmith"},
    )
    res = client.patch(f"/tickets/{t['number']}", json={"status": "resolved", "priority": "4-low"})
    assert res.status_code == 200
    assert res.json()["priority"] == "4-low"


def test_add_work_note(client, new_ticket) -> None:
    t = new_ticket()
    res = client.post(
        f"/tickets/{t['number']}/work-notes",
        json={"author": "asmith", "body": "Checked VPN logs, client is on version 6.1."},
    )
    assert res.status_code == 201
    notes = res.json()["work_notes"]
    assert len(notes) == 1
    assert notes[0]["author"] == "asmith"


def test_resolve(client, new_ticket) -> None:
    t = new_ticket()
    res = client.post(
        f"/tickets/{t['number']}/resolve",
        json={"resolution_notes": "Upgraded GlobalProtect to 6.2.", "resolved_by": "asmith"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "resolved"
    assert body["resolved_at"] is not None

    again = client.post(
        f"/tickets/{t['number']}/resolve",
        json={"resolution_notes": "Upgraded GlobalProtect to 6.2.", "resolved_by": "asmith"},
    )
    assert again.status_code == 409


def test_resolve_needs_real_notes(client, new_ticket) -> None:
    t = new_ticket()
    res = client.post(
        f"/tickets/{t['number']}/resolve", json={"resolution_notes": "fixed", "resolved_by": "a"}
    )
    assert res.status_code == 422


def test_closed_ticket_is_read_only(client, new_ticket) -> None:
    t = new_ticket()
    client.patch(f"/tickets/{t['number']}", json={"status": "closed"})
    note = client.post(f"/tickets/{t['number']}/work-notes", json={"author": "a", "body": "x"})
    assert note.status_code == 409
    assert client.patch(f"/tickets/{t['number']}", json={"priority": "4-low"}).status_code == 409


def test_actions_on_missing_ticket_are_404(client) -> None:
    assert client.patch("/tickets/INC0099999", json={"priority": "4-low"}).status_code == 404
    note = client.post("/tickets/INC0099999/work-notes", json={"author": "a", "body": "x"})
    assert note.status_code == 404
