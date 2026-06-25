"""
providers/cloudflare.py
Cloudflare Workers AI — 100,000 requests/day FREE on Workers free plan.
OpenAI-compatible. Supports img2img via /images/edits endpoint.
Get keys: https://dash.cloudflare.com → My Profile → API Tokens
"""
import os
import base64
import requests


CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "")
MODEL = "@cf/black-forest-labs/flux-1-schnell"

# Other models available:
# "@cf/stabilityai/stable-diffusion-xl-base-1.0"
# "@cf/runwayml/stable-diffusion-v1-5"
# "@cf/lykon/dreamshaper-8-lcm"  — fast


async def generate(image_path: str, prompt: str, output_path: str) -> bool:
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        raise ValueError("CF_ACCOUNT_ID or CF_API_TOKEN not set")

    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{MODEL}"
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}

    # Try img2img first (multipart form)
    try:
        with open(image_path, "rb") as img_file:
            files = {"image": ("input.jpg", img_file, "image/jpeg")}
            data = {"prompt": prompt, "num_steps": 20, "strength": 0.8}
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)

        if resp.ok:
            result = resp.json()
            if result.get("success") and result.get("result", {}).get("image"):
                img_bytes = base64.b64decode(result["result"]["image"])
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                return True
    except Exception:
        pass

    # Fallback: pure text-to-image
    payload = {
        "prompt": prompt,
        "num_steps": 20,
        "guidance": 7.5,
        "width": 1344,
        "height": 768,
    }
    resp2 = requests.post(url, headers=headers, json=payload, timeout=120)
    resp2.raise_for_status()
    result2 = resp2.json()

    if result2.get("success") and result2.get("result", {}).get("image"):
        img_bytes = base64.b64decode(result2["result"]["image"])
        with open(output_path, "wb") as f:
            f.write(img_bytes)
        return True

    raise ValueError(f"Cloudflare failed: {result2}")
