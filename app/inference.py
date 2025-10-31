import os, time, io, numpy as np
from typing import Optional
from PIL import Image
import cv2
import torch
from .metrics import INFERENCE_COUNT, INFERENCE_LATENCY

class Denoiser:
    def __init__(self, model_path: Optional[str]=None, device: Optional[str]=None):
        self.model_path = model_path or os.getenv("MODEL_PATH","")
        self.device = device or ("cuda" if (torch and torch.cuda.is_available()) else "cpu")
        self.model=None
        if torch and self.model_path and os.path.exists(self.model_path):
            try:
                self.model = torch.jit.load(self.model_path, map_location=self.device); self.model.eval()
            except Exception: self.model=None

    def _torch_denoise(self, img: np.ndarray) -> np.ndarray:
        assert torch is not None
        with torch.no_grad():
            x = torch.from_numpy(img).float().permute(2,0,1).unsqueeze(0)/255.0
            x = x.to(self.device)
            y = x  # TODO: replace with real DDPM inference
            out = (y.squeeze(0).permute(1,2,0).clamp(0,1).cpu().numpy()*255).astype(np.uint8)
        return out

    def _opencv_denoise(self, img: np.ndarray, strength: float) -> np.ndarray:
        if cv2 is None: return img
        h = 10 + int(20*strength); hc = 10 + int(20*strength)
        return cv2.fastNlMeansDenoisingColored(img,None,h,hc,7,21)

    def denoise(self, pil_img: Image.Image, strength: float=0.6, model_name: str="ddpm")->Image.Image:
        start=time.perf_counter()
        arr=np.array(pil_img.convert("RGB"))
        out = self._torch_denoise(arr) if (self.model is not None and torch is not None) else self._opencv_denoise(arr,strength)
        INFERENCE_COUNT.labels(model=model_name).inc()
        INFERENCE_LATENCY.labels(model=model_name).observe(time.perf_counter()-start)
        return Image.fromarray(out)
