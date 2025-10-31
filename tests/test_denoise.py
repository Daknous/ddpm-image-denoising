import io
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
def token(c):
    r = c.post("/auth/token", data={"username":"demo","password":"changeme"}); assert r.status_code==200
    return r.json()["access_token"]
def test_denoise():
    c = TestClient(app); t = token(c)
    img = Image.new("RGB",(32,32),(120,120,120)); b = io.BytesIO(); img.save(b, format="PNG"); b.seek(0)
    r = c.post("/denoise?strength=0.5&model_name=ddpm", headers={"Authorization":f"Bearer {t}"}, files={"file":("tiny.png", b.getvalue(), "image/png")})
    assert r.status_code==200 and r.headers["content-type"]=="image/png" and len(r.content)>0
