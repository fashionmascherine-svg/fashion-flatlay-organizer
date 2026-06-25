"""
providers/fashn.py
FASHN.ai — Fashion-specific virtual try-on API. Best quality for clothing.
Async job-based API with polling.
Get free key: https://fashn.ai/products/api
"""
import os
import time
import base64
import requests


FASHN_KEY = os.getenv("FASHN_KEY", "")
BASE_URL = "https://api.fashn.ai/v1"


async def generate(image_path: str, prompt: str, output_path: str) -> bool:
    if not FASHN_KEY:
        raise ValueError("FASHN_KEY not set")

    headers = {
        "Authorization": f"Bearer {FASHN_KEY}",
        "Content-Type": "application/json",
    }

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
        img_data_url = f"data:image/jpeg;base64,{img_b64}"

    payload = {
        "model_image": img_data_url,
        "category": "full-body",
        "mode": "quality",
    }

    resp = requests.post(f"{BASE_URL}/run", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    job_data = resp.json()
    job_id = job_data.get("id")

    if not job_id:
        raise ValueError(f"No job ID returned: {job_data}")

    # Poll for result (max 3 minutes)
    for _ in range(36):
        time.sleep(5)
        status_resp = requests.get(f"{BASE_URL}/status/{job_id}", headers=headers, timeout=30)
        status_data = status_resp.json()
        status = status_data.get("status")

        if status == "completed":
            output_url = status_data.get("output", [None])[0]
            if output_url:
                img_resp = requests.get(output_url, timeout=60)
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                return True
            break
        elif status in ("failed", "cancelled"):
            raise ValueError(f"FASHN job failed: {status_data}")

    raise ValueError("FASHN timeout after 3 minutes")
