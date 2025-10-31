import io, time
from typing import Dict
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse, PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import structlog
from .logging_config import configure_logging
from .metrics import REQUEST_COUNT, REQUEST_LATENCY
from .auth import issue_token
from .deps import require_user, validate_image
from .models import DenoiseQuery
from .inference import Denoiser
from .middleware import RequestIdMiddleware

configure_logging(); log = structlog.get_logger()
app = FastAPI(title="DDPM Denoiser API", version="0.1.0")
app.add_middleware(RequestIdMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - start
    endpoint = request.url.path
    REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=response.status_code).inc()
    return response

@app.get("/health", tags=["meta"])
async def health()->Dict[str,str]: return {"status":"ok"}
@app.get("/livez", tags=["meta"])
async def livez(): return {"status":"live"}
@app.get("/readyz", tags=["meta"])
async def readyz(): return {"status":"ready"}

@app.post("/auth/token", tags=["auth"])
async def login(form_data=Depends(issue_token)): return form_data

@app.get("/metrics", tags=["meta"])
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

denoiser = Denoiser()

@app.post("/denoise", tags=["denoise"])
async def denoise_image(query: DenoiseQuery = Depends(), _user=Depends(require_user), file: UploadFile = File(...)):
    file = await validate_image(file)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large (>10MB).")
    from PIL import Image
    img = Image.open(io.BytesIO(content))
    out = denoiser.denoise(img, strength=query.strength, model_name=query.model_name)
    buf = io.BytesIO(); out.save(buf, format="PNG"); buf.seek(0)
    log.info("denoise_done", size=len(content), model=query.model_name, strength=query.strength)
    return StreamingResponse(buf, media_type="image/png")
