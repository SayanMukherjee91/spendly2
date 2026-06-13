class TestDashboard:
    def test_unauthenticated_redirects_to_login(self, client):
        rv = client.get("/dashboard")
        assert rv.status_code == 302
        assert "/login" in rv.location

    def test_authenticated_returns_200(self, auth_client):
        rv = auth_client.get("/dashboard")
        assert rv.status_code == 200

    def test_shows_user_name(self, auth_client):
        rv = auth_client.get("/dashboard")
        assert b"Alice" in rv.data

    def test_empty_user_no_expenses(self, auth_client):
        rv = auth_client.get("/dashboard")
        assert rv.status_code == 200

    def test_seeded_user_with_expenses(self, seeded_client):
        rv = seeded_client.get("/dashboard")
        assert rv.status_code == 200

    def test_dashboard_contains_html(self, auth_client):
        rv = auth_client.get("/dashboard")
        assert b"<" in rv.data
