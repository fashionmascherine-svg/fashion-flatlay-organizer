"""
providers/pollinations.py
Zero auth, zero cost, unlimited — text-to-image only (no true img2img).
Strategy: build a rich textual prompt describing ALL garments, generate flat-lay.
NO API KEY REQUIRED. Works out of the box.
"""
import urllib.parse
import requests


async def generate(image_path: str, prompt: str, output_path: str) -> bool:
    """Call Pollinations image API — NO API KEY REQUIRED."""
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1344&height=768&model=flux&nologo=true&seed={hash(prompt) % 99999}"
    )
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    if len(resp.content) < 5000:
        raise ValueError("Response too small — likely an error page, not an image")

    with open(output_path, "wb") as f:
        f.write(resp.content)
    return True
