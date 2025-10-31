# DDPM Denoiser API
This starter serves an image denoiser **DDPM** via FastAPI

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="replace-with-strong-secret"
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/docs
```
Get a token:
```bash
curl -X POST http://127.0.0.1:8000/auth/token -d "username=demo&password=changeme"
```
Call the API (replace TOKEN):
```bash
curl -H "Authorization: Bearer TOKEN" -F "file=@/path/to/image.png" \
"http://127.0.0.1:8000/denoise?strength=0.6&model_name=ddpm" --output output.png
```
Metrics:
```bash
curl http://127.0.0.1:8000/metrics
```

## Wire in your DDPM
Implement real inference in `app/inference.py::_torch_denoise`. Optionally export to TorchScript and set `MODEL_PATH`.

## Observability stack (Prometheus + Grafana)
```bash
docker compose -f docker-compose.prom.yml up --build
# Prometheus http://localhost:9090, Grafana http://localhost:3000 (admin/admin)
```

## Evaluation (PSNR/SSIM)
Organize two folders:
```
clean/      # ground-truth images
denoised/   # outputs from /denoise
```
Run:
```bash
python scripts/eval_psnr_ssim.py --clean_dir clean --denoised_dir denoised
```

## Tests
```bash
pytest -q
```

## Load test (Locust)
```bash
pip install locust
locust -f locustfile.py --host http://127.0.0.1:8000
```

## Endpoints
- `/health`, `/livez`, `/readyz`: Health checks
- `/auth/token`: Get an auth token
- `/denoise`: Upload an image for denoising (requires auth)

## Model Checkpoint
Place your model checkpoint in `model_MNIST_checkpoint/` or set `MODEL_PATH` env variable.

---
MIT License