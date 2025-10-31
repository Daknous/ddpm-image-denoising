from fastapi.testclient import TestClient
from app.main import app
def token(c):
    r = c.post("/auth/token", data={"username":"demo","password":"changeme"}); assert r.status_code==200
    return r.json()["access_token"]
def test_auth():
    c = TestClient(app); t = token(c); assert isinstance(t,str) and len(t)>10
