"""
providers/gemini_pipeline.py — THE RECOMMENDED FREE STRATEGY

Two-step pipeline at zero cost:
  Step 1: Gemini 2.0 Flash (free: 1M tokens/day) → analyzes image → extracts item inventory
  Step 2: Pollinations.ai (free, no key, no limit) → generates organized flat-lay

This is the smartest approach: Gemini *sees* your actual photo and builds
a precise item list, then Pollinations generates a perfect flat-lay.

Get Gemini key (FREE): https://aistudio.google.com/app/apikey
"""
import os
import base64
import urllib.parse
import requests


GEMINI_KEY = os.getenv("GEMINI_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"


async def analyze_image_with_gemini(image_path: str) -> str:
    """Use Gemini Vision to extract a detailed inventory of clothing items."""
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "contents": [{
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64,
                    }
                },
                {
                    "text": (
                        "List EVERY clothing item, shoe, bag, and accessory visible in this image. "
                        "Keep each item description short and concise (max 8 words per item). "
                        "Format as a simple comma-separated list. "
                        "Example: orange wedge sandals, black leather handbag, pink chiffon blouse"
                    )
                }
            ]
        }]
    }

    resp = requests.post(
        f"{GEMINI_URL}?key={GEMINI_KEY}",
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    item_list = data["candidates"][0]["content"]["parts"][0]["text"]
    return item_list.strip()


async def generate(image_path: str, prompt: str, output_path: str) -> bool:
    """
    Pipeline:
    1. Gemini Vision → extract full item list from actual photo
    2. Build hyper-specific Pollinations prompt → generate organized flat-lay
    """
    if not GEMINI_KEY:
        raise ValueError("GEMINI_KEY not set — get a free key at https://aistudio.google.com/app/apikey")

    # Step 1: Analyze the actual image
    print("    [Gemini] Analyzing image to extract item inventory...")
    item_list = await analyze_image_with_gemini(image_path)
    print(f"    [Gemini] Detected: {item_list[:150]}...")

    # Step 2: Build enriched flat-lay prompt (truncate item list to avoid URL length issues)
    max_items_len = 400
    truncated_items = item_list if len(item_list) <= max_items_len else item_list[:max_items_len].rsplit(",", 1)[0] + "..."
    enriched_prompt = (
        "Professional overhead flat lay fashion photography on pristine white marble surface. "
        "All items neatly organized, clean and unwrinkled, with visible labels/details. "
        f"Include ALL of these items — nothing omitted: {truncated_items}. "
        "Layout: clothing items folded/flat in upper-left area, shoes paired neatly in lower-right, "
        "bags and accessories arranged center-right. Generous white space between items. "
        "Lighting: even soft studio lighting, no harsh shadows, slightly warm tone. "
        "Style: editorial fashion photography, high-end magazine quality, bird-eye view (90 degrees overhead). "
        "Image must show every single item from the list with equal visibility."
    )

    # Step 3: Generate with Pollinations (no key needed)
    encoded = urllib.parse.quote(enriched_prompt)
    poll_url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1344&height=768&model=flux&nologo=true"
    )

    print("    [Pollinations] Generating organized flat-lay with FLUX...")
    resp = requests.get(poll_url, timeout=120)
    resp.raise_for_status()

    if len(resp.content) < 5000:
        raise ValueError("Pollinations returned too small a file — error response")

    with open(output_path, "wb") as f:
        f.write(resp.content)

    return True
