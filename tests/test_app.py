import importlib, os
import pytest

def load_secure_app():
    os.environ["VULN_MODE"] = "0"
    import app as appmod
    importlib.reload(appmod)
    appmod.app.config.update(TESTING=True)
    return appmod.app

@pytest.fixture
def client():
    return load_secure_app().test_client()

def login(client, user="alice"):
    pw = "alicepw" if user == "alice" else "bobpw"
    return client.post("/login", data={"username": user, "password": pw})

def test_clickjacking_header_present(client):
    assert client.get("/").headers.get("X-Frame-Options") == "DENY"

def test_idor_own_profile_allowed(client):
    login(client, "alice")
    r = client.get("/profile?id=1")
    assert r.status_code == 200 and b"alice" in r.data

def test_idor_other_profile_blocked(client):
    login(client, "alice")
    assert client.get("/profile?id=2").status_code == 403

def test_command_injection_blocked(client):
    r = client.post("/ping", data={"target": "127.0.0.1; whoami"})
    assert b"uid=" not in r.data and b"Rejected" in r.data

def test_csrf_rejected_without_token(client):
    login(client, "alice")
    r = client.post("/transfer", data={"amount": "100", "recipient": "bob"})
    assert r.status_code == 403
