def test_landing_page_ok(client):
    rv = client.get("/")
    assert rv.status_code == 200


def test_terms_page_ok(client):
    rv = client.get("/terms")
    assert rv.status_code == 200


def test_privacy_page_ok(client):
    rv = client.get("/privacy")
    assert rv.status_code == 200


def test_landing_contains_html(client):
    rv = client.get("/")
    assert b"<html" in rv.data.lower() or b"<!doctype" in rv.data.lower()
