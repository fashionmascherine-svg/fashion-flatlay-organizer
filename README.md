# 👗 Fashion Flat-Lay Organizer — Free API Benchmark

> **Benchmark tool** that compares multiple free AI APIs to transform a **messy clothing photo** into an organized, professional flat-lay composition — no user registration required.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Cost](https://img.shields.io/badge/cost-FREE-brightgreen)

---

## 🎯 Use Case

**Input:** Photo of messy clothing pile (sofa, floor, etc.)  
**Output:** AI-generated organized flat-lay or styled outfit image

| Items detected in demo image |
|---|
| 👠 3 pairs of shoes (orange wedge, nude wedge, gold heels) |
| 👜 3 bags (black structured, striped tote, red crossbody) |
| 👚 6+ clothing items (blazer, chiffon top, turquoise blouse, etc.) |

---

## 🆓 Supported Free APIs

| # | Service | Auth needed | Img2Img | Free limit | Cost |
|---|---|---|---|---|---|
| 1 | **Pollinations.ai** | ❌ None | ❌ (t2i prompt) | ♾️ Unlimited | $0 |
| 2 | **HuggingFace Inference** | ✅ Dev key only | ✅ | ~300 req/hr | $0 |
| 3 | **Cloudflare Workers AI** | ✅ Dev key only | ✅ `/edits` | 100k/day | $0 |
| 4 | **SiliconFlow** | ✅ Dev key only | ✅ | Credits on signup | $0 |
| 5 | **FASHN.ai** | ✅ Dev key only | ✅ Fashion-specific | Free tier | $0 |
| 6 | **Gemini Vision + Pollinations** | ✅ Dev key only | ✅ Pipeline | 1M tokens/day | $0 |

---

## 🚀 Quick Start

```bash
git clone https://github.com/fashionmascherine-svg/fashion-flatlay-organizer
cd fashion-flatlay-organizer
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env (only developer keys needed)
python benchmark.py --image your_clothes.jpg
```

---

## 📁 Project Structure

```
fashion-flatlay-organizer/
├── benchmark.py            # Main benchmark runner
├── providers/
│   ├── __init__.py
│   ├── pollinations.py     # Zero-auth, unlimited
│   ├── huggingface.py      # img2img with HF Inference API
│   ├── cloudflare.py       # img2img via Workers AI (100k/day)
│   ├── siliconflow.py      # img2img via SiliconFlow
│   ├── fashn.py            # Fashion virtual try-on API
│   └── gemini_pipeline.py  # Vision analysis + Pollinations (BEST FREE)
├── scorer.py               # Quality scoring engine (no AI needed)
├── report.py               # HTML report generator
├── requirements.txt
├── .env.example
└── .github/workflows/benchmark.yml
```

---

## 🧠 Best Free Strategy: Gemini Pipeline

The `gemini_pipeline` provider is the **smartest free approach**:

1. **Gemini 2.0 Flash** (free: 1M tokens/day via Google AI Studio) analyzes your messy photo and extracts a precise item-by-item inventory
2. Builds a hyper-detailed prompt with every detected item
3. **Pollinations.ai** (free, no limit, no key) generates the organized flat-lay

```
Your messy photo → Gemini Vision → item list → Pollinations FLUX → organized flat-lay
```

Zero cost. Zero user registration. Just two free developer API keys.

---

## 🧪 Benchmark Scoring

Each output is scored on 4 dimensions (0-10):

| Metric | Weight | Description |
|---|---|---|
| **Completeness** | 30% | All items from input present in output |
| **Organization** | 30% | Logical arrangement, clean background |
| **Visual Quality** | 20% | Resolution, color richness, sharpness |
| **Speed** | 20% | API response time |

```bash
# Run all providers in parallel
python benchmark.py --image clothes.jpg --providers all

# Waterfall mode (stop at first success)
python benchmark.py --image clothes.jpg --waterfall

# Test specific providers
python benchmark.py --image clothes.jpg --providers gemini_pipeline,pollinations
```

---

## 📊 Output

After running, you get:
- `results/` folder with all generated images per provider
- `results/report.html` — visual comparison with scores and rankings
- `results/benchmark_TIMESTAMP.json` — raw data for further analysis

---

## ⚙️ Configuration (`.env`)

```env
# Only developer-side keys — end users of your app never register
HF_TOKEN=hf_your_token
CF_ACCOUNT_ID=your_cf_account_id
CF_API_TOKEN=your_cf_token
SILICONFLOW_KEY=your_sf_key
FASHN_KEY=your_fashn_key
GEMINI_KEY=your_gemini_key

# Pollinations: NO KEY NEEDED — works instantly
```

---

## 🔧 Zero-Cost Tricks

| Trick | Description | Cost |
|---|---|---|
| **Provider waterfall** | Auto-fallback if quota exceeded | $0 |
| **Gemini + Pollinations pipeline** | Best quality free combo | $0 |
| **HF Spaces self-host** | Deploy your own Gradio app on HF free compute | $0 |
| **On-device WebGPU** | Run FLUX in user's browser via `transformers.js` | $0 |

---

## 📄 License

MIT — free for commercial use.
