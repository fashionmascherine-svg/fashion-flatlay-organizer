"""
providers/huggingface.py
HuggingFace Inference API — text-to-image with FLUX.1-schnell.
Requires HF_TOKEN env var (free developer key — users never register).
Free tier: ~300 requests/hour. No credit card needed.
Get token: https://huggingface.co/settings/tokens
"""
import os
import requests


HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL = "black-forest-labs/FLUX.1-schnell"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL}"


async def generate(image_path: str, prompt: str, output_path: str) -> bool:
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not set in environment")

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4,
            "guidance_scale": 0.0,
        },
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    content_type = resp.headers.get("content-type", "")

    if "image" in content_type:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True

    if "json" in content_type:
        data = resp.json()
        error = data.get("error", str(data)[:200])
        raise ValueError(f"HuggingFace API error: {error}")

    resp.raise_for_status()
    return False
