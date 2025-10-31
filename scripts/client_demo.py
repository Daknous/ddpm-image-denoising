import sys, requests
HOST="http://127.0.0.1:8000"
def tok():
    r=requests.post(f"{HOST}/auth/token", data={"username":"demo","password":"changeme"}); r.raise_for_status()
    return r.json()["access_token"]
def denoise(p, strength=0.6):
    t=tok()
    with open(p,"rb") as f:
        files={"file":(p,f,"image/png")}
        r=requests.post(f"{HOST}/denoise?strength={strength}&model_name=ddpm", headers={"Authorization":f"Bearer {t}"}, files=files)
    r.raise_for_status(); out=p.replace(".","_denoised.")
    with open(out,"wb") as g: g.write(r.content); print("Saved",out)
if __name__=="__main__": denoise(sys.argv[1], float(sys.argv[2]) if len(sys.argv)>2 else 0.6)
