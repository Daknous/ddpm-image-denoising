import argparse
from pathlib import Path
from PIL import Image
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
def load_rgb(p: Path) -> np.ndarray: return np.array(Image.open(p).convert("RGB"))
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean_dir", required=True); ap.add_argument("--denoised_dir", required=True)
    ap.add_argument("--out_csv", default="eval_psnr_ssim.csv")
    a = ap.parse_args()
    cd, dd = Path(a.clean_dir), Path(a.denoised_dir)
    rows, P, S = [], [], []
    for p in sorted(cd.iterdir()):
        if not p.is_file(): continue
        q = dd / p.name
        if not q.exists(): continue
        gt, de = load_rgb(p), load_rgb(q)
        P.append(psnr(gt,de,data_range=255)); S.append(ssim(gt,de,channel_axis=2,data_range=255))
        rows.append((p.name, P[-1], S[-1]))
    import csv; 
    with open(a.out_csv,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["file","psnr","ssim"]); w.writerows(rows)
    if P: print(f"AVG PSNR {sum(P)/len(P):.2f} dB | AVG SSIM {sum(S)/len(S):.4f}")
    else: print("No matches found.")
if __name__=="__main__": main()
