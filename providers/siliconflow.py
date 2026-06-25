"""
providers/siliconflow.py
SiliconFlow — Chinese AI platform, OpenAI-compatible, 200+ models.
Free credits on signup. img2img + t2i supported.
Get key: https://siliconflow.cn → Console → API Keys
"""
import os
import base64
import requests


SF_KEY = os.getenv("SILICONFLOW_KEY", "")
BASE_URL = "https://api.siliconflow.com/v1"
MODEL_IMG2IMG = "stabilityai/stable-diffusion-xl-base-1.0"
MODEL_T2I = "black-forest-labs/FLUX.1-schnell"


async def generate(image_path: str, prompt: str, output_path: str) -> bool:
    if not SF_KEY:
        raise ValueError("SILICONFLOW_KEY not set")

    headers = {
        "Authorization": f"Bearer {SF_KEY}",
        "Content-Type": "application/json",
    }

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data_url = f"data:image/jpeg;base64,{img_b64}"

    # Try img2img first
    try:
        payload_i2i = {
            "model": MODEL_IMG2IMG,
            "prompt": prompt,
            "image": img_data_url,
            "strength": 0.75,
            "image_size": "1344x768",
            "num_inference_steps": 25,
            "guidance_scale": 7.5,
            "batch_size": 1,
        }
        resp = requests.post(f"{BASE_URL}/image-to-image", headers=headers, json=payload_i2i, timeout=120)
        if resp.ok:
            data = resp.json()
            if data.get("images"):
                img_url = data["images"][0].get("url")
                if img_url:
                    img_resp = requests.get(img_url, timeout=30)
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    return True
    except Exception:
        pass

    # Fallback: text-to-image with FLUX (higher quality)
    payload_t2i = {
        "model": MODEL_T2I,
        "prompt": prompt,
        "image_size": "1344x768",
        "num_inference_steps": 20,
        "batch_size": 1,
    }
    resp2 = requests.post(f"{BASE_URL}/images/generations", headers=headers, json=payload_t2i, timeout=120)
    resp2.raise_for_status()
    data2 = resp2.json()

    if data2.get("images"):
        img_url = data2["images"][0].get("url")
        img_resp = requests.get(img_url, timeout=30)
        with open(output_path, "wb") as f:
            f.write(img_resp.content)
        return True

    raise ValueError(f"SiliconFlow failed: {data2}")
