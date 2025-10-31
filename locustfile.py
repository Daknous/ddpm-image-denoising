from locust import HttpUser, task, between
from io import BytesIO
from PIL import Image
class DenoiseUser(HttpUser):
    wait_time = between(0.5, 2)
    def on_start(self):
        r = self.client.post("/auth/token", data={"username":"demo","password":"changeme"})
        self.token = r.json()["access_token"]
    @task
    def denoise(self):
        hdrs = {"Authorization": f"Bearer {self.token}"}
        bio = BytesIO(); Image.new("RGB",(32,32),(120,120,120)).save(bio, format="PNG"); bio.seek(0)
        files = {"file": ("tiny.png", bio.getvalue(), "image/png")}
        self.client.post("/denoise?strength=0.5&model_name=ddpm", headers=hdrs, files=files)
