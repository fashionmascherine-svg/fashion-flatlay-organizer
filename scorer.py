"""
scorer.py — Quality scoring engine for generated flat-lay images.
Scores each output image without requiring any additional AI API.
Uses only Pillow + NumPy — pure local computation.

Scoring dimensions:
  - Completeness (30%): Are expected item color regions present?
  - Organization (30%): Is the background clean? Are items spread evenly?
  - Visual Quality (20%): Resolution, sharpness, color richness
  - Speed (20%): API response time
"""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np


EXPECTED_COLORS = {
    "orange": 1.0,
    "gold": 1.0,
    "black": 1.0,
    "red": 1.0,
    "teal_blue": 1.0,
    "pink": 0.9,
    "beige": 0.8,
    "stripes": 0.9,
    "nude_area": 0.8,
}


def _color_coverage(arr: np.ndarray) -> dict:
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    total = arr.shape[0] * arr.shape[1]
    return {
        "orange":    float(((r>180)&(g>80)&(g<170)&(b<80)).sum()) / total,
        "gold":      float(((r>180)&(g>140)&(b<80)).sum()) / total,
        "black":     float(((r<60)&(g<60)&(b<60)).sum()) / total,
        "red":       float(((r>160)&(g<80)&(b<80)).sum()) / total,
        "teal_blue": float(((r<120)&(g>150)&(b>150)).sum()) / total,
        "pink":      float(((r>180)&(g>120)&(b>140)&(np.abs(r-b)<60)).sum()) / total,
        "beige":     float(((r>150)&(g>130)&(b>110)&(np.abs(r-g)<40)&(np.abs(g-b)<40)).sum()) / total,
        "nude_area": float(((r>150)&(g>130)&(b>110)&(np.abs(r-g)<40)&(np.abs(g-b)<40)).sum()) / total,
        "stripes":   float(np.mean(np.std(arr[:,:,0], axis=1) > 30)),
    }


def score_completeness(arr: np.ndarray) -> float:
    cov = _color_coverage(arr)
    score, total_w = 0.0, sum(EXPECTED_COLORS.values())
    for item, weight in EXPECTED_COLORS.items():
        if cov.get(item, 0) >= 0.005:
            score += weight
    return min(10.0, score / total_w * 10.0)


def score_organization(arr: np.ndarray) -> float:
    h, w, _ = arr.shape
    gray = np.mean(arr, axis=2)
    white_ratio = float(np.mean(gray > 220))
    bg_score = 10.0 if 0.3 <= white_ratio <= 0.75 else (7.0 if white_ratio > 0.75 else white_ratio * 20)
    q_means = [np.mean(gray[hh:hh+h//2, ww:ww+w//2]) for hh in (0, h//2) for ww in (0, w//2)]
    dist_score = min(10.0, float(np.std(q_means)) / 15 * 10)
    edges = np.array(Image.fromarray(arr).filter(ImageFilter.FIND_EDGES))
    sharp_score = min(10.0, float(np.mean(edges)) / 20 * 10)
    return bg_score * 0.4 + dist_score * 0.3 + sharp_score * 0.3


def score_visual_quality(arr: np.ndarray) -> float:
    h, w, _ = arr.shape
    res_score = 10.0 if h*w >= 1024*768 else (7.0 if h*w >= 512*512 else 5.0)
    s = arr[::8, ::8, :]
    color_score = min(10.0, (np.std(s[:,:,0]) + np.std(s[:,:,1]) + np.std(s[:,:,2])) / 30)
    contrast = float(np.std(np.mean(s, axis=2)))
    contrast_score = 10.0 if 30 <= contrast <= 90 else (7.0 if contrast > 90 else contrast/30*10)
    return res_score * 0.3 + color_score * 0.4 + contrast_score * 0.3


def score_speed(elapsed: float) -> float:
    if elapsed <= 5: return 10.0
    elif elapsed <= 15: return 8.0
    elif elapsed <= 30: return 6.0
    elif elapsed <= 60: return 4.0
    elif elapsed <= 120: return 2.0
    return 1.0


def score_result(output_path: str, elapsed_sec: float) -> dict:
    """Main entry point. Returns per-metric scores + weighted total."""
    arr = np.array(Image.open(output_path).convert("RGB"))
    c = score_completeness(arr)
    o = score_organization(arr)
    q = score_visual_quality(arr)
    s = score_speed(elapsed_sec)
    total = c*0.30 + o*0.30 + q*0.20 + s*0.20
    return {
        "completeness": round(c, 2),
        "organization": round(o, 2),
        "quality": round(q, 2),
        "speed": round(s, 2),
        "total": round(total, 2),
    }
