"""
providers/huggingface.py
HuggingFace Inference API — img2img with stable diffusion.
Requires HF_TOKEN env var (free developer key — users never register).
Free tier: ~300 requests/hour. No credit card needed.
Get token: https://huggingface.co/settings/tokens
"""
import os
import base64
import requests


HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL = "stabilityai/stable-diffusion-xl-refiner-1.0"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL}"

# Alternative high-quality models:
# "black-forest-labs/FLUX.1-dev"   — best quality
# "Kwai-Kolors/Kolors"              — Chinese model, very good
# "runwayml/stable-diffusion-v1-5" — classic, fast


async def generate(image_path: str, prompt: str, output_path: str) -> bool:
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not set in environment")

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "image": img_b64,
            "strength": 0.75,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        },
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    content_type = resp.headers.get("content-type", "")

    if "image" in content_type:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True
    elif "json" in content_type:
        data = resp.json()
        if isinstance(data, list) and data:
            img_bytes = base64.b64decode(data[0].get("image", data[0]))
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            return True

    resp.raise_for_status()
    return False
