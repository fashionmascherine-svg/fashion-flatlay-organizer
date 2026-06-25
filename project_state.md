# 🗂️ Project State — Fashion Flat-Lay Organizer

> Last updated: 2026-06-25

---

## ✅ Working Features

### 3 of 6 providers functional

| # | Provider | Status | Score | Notes |
|---|---|---|---|---|
| 1 | **HuggingFace** | ✅ Working | 8.8/10 | FLUX.1-schnell via HF Inference API, ~0.3s response |
| 2 | **Pollinations** | ✅ Working | 7.8/10 | FLUX model, no key needed, ~0.7s |
| 3 | **Gemini Pipeline** | ✅ Working | 6.9/10 | Gemini 3.1 Flash Lite analyzes → Pollinations generates, ~37s |
| 4 | **Cloudflare** | ❌ Broken | — | Needs valid `CF_ACCOUNT_ID` and `CF_API_TOKEN` |
| 5 | **SiliconFlow** | ❌ Broken | — | Needs valid `SILICONFLOW_KEY` |
| 6 | **FASHN** | ❌ Broken | — | Needs valid `FASHN_KEY` |

---

## 🔧 Bugs Fixed

| # | Bug | File(s) | Fix |
|---|---|---|---|
| 1 | **API keys not loaded** — `load_dotenv()` ran after provider imports, so `os.getenv()` returned empty | [`benchmark.py`](benchmark.py) | Moved `load_dotenv()` before all provider imports |
| 2 | **Pollinations 404** — Default prompt contained `\n` characters causing malformed URLs | [`benchmark.py`](benchmark.py) | Replaced multiline string with single-line concatenation |
| 3 | **Gemini 429 (quota exceeded)** — Model `gemini-2.0-flash` had zero free-tier quota for this API key | [`providers/gemini_pipeline.py`](providers/gemini_pipeline.py) | Switched to `gemini-3.1-flash-lite` |
| 4 | **Gemini Pipeline 404** — Gemini-generated item list was too verbose, creating URLs exceeding HTTP limits | [`providers/gemini_pipeline.py`](providers/gemini_pipeline.py) | Made Gemini prompt request concise output + truncate item list to 400 chars |
| 5 | **HuggingFace 400** — Model `stabilityai/stable-diffusion-xl-refiner-1.0` not supported by HF router `hf-inference` | [`providers/huggingface.py`](providers/huggingface.py) | Changed to `black-forest-labs/FLUX.1-schnell` with text-to-image mode |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `pillow` | >=10.0.0 | Image processing |
| `numpy` | >=1.24.0 | Array operations for scoring |
| `requests` | >=2.31.0 | HTTP API calls |
| `python-dotenv` | >=1.0.0 | Load `.env` file |
| `aiohttp` | >=3.9.0 | Async HTTP (future use) |

---

## 🗄️ File Overview

| File | Purpose | Status |
|---|---|---|
| [`benchmark.py`](benchmark.py) | Main runner: CLI args, parallel execution, orchestration | ✅ Stable |
| [`providers/pollinations.py`](providers/pollinations.py) | Pollinations.ai text-to-image (no key) | ✅ Stable |
| [`providers/huggingface.py`](providers/huggingface.py) | HuggingFace Inference API (FLUX.1-schnell) | ✅ Fixed |
| [`providers/cloudflare.py`](providers/cloudflare.py) | Cloudflare Workers AI | ⚠️ Needs keys |
| [`providers/siliconflow.py`](providers/siliconflow.py) | SiliconFlow API | ⚠️ Needs keys |
| [`providers/fashn.py`](providers/fashn.py) | FASHN.ai virtual try-on | ⚠️ Needs keys |
| [`providers/gemini_pipeline.py`](providers/gemini_pipeline.py) | Gemini 3.1 Flash Lite + Pollinations pipeline | ✅ Fixed |
| [`scorer.py`](scorer.py) | Local quality scoring (Pillow + NumPy) | ✅ Stable |
| [`report.py`](report.py) | HTML report generator | ✅ Stable |
| [`.env`](.env) | API keys (excluded from git) | ⚠️ Partially configured |
| [`.env.example`](.env.example) | Template for local config | ✅ Stable |
| [`.gitignore`](.gitignore) | Ignored files for version control | ✅ New |
| [`requirements.txt`](requirements.txt) | Python dependencies | ✅ Stable |
| [`README.md`](README.md) | Documentation | ✅ Updated |

---

## 🚀 How to Run

```bash
# Activate virtual environment
source venv/bin/activate

# Full benchmark
python benchmark.py --image your_photo.jpg --providers all

# Specific providers
python benchmark.py --image your_photo.jpg --providers huggingface,gemini_pipeline

# Waterfall mode
python benchmark.py --image your_photo.jpg --waterfall

# Custom output directory
python benchmark.py --image your_photo.jpg --output ./my_results
```

---

## 🔑 Required API Keys

| Key | Provider | Where to get |
|---|---|---|
| `HF_TOKEN` | HuggingFace | https://huggingface.co/settings/tokens |
| `CF_ACCOUNT_ID` + `CF_API_TOKEN` | Cloudflare | https://dash.cloudflare.com → API Tokens |
| `SILICONFLOW_KEY` | SiliconFlow | https://siliconflow.cn → Console → API Keys |
| `FASHN_KEY` | FASHN.ai | https://fashn.ai/products/api |
| `GEMINI_KEY` | Google Gemini | https://aistudio.google.com/app/apikey |
| *(none)* | Pollinations | Works out of the box |

---

## 📋 To Do

- [ ] Configure Cloudflare, SiliconFlow, FASHN keys for full 6-provider comparison
- [ ] Add image preprocessing (resize, optimize before sending to APIs)
- [ ] Implement result caching to avoid re-generating images
- [ ] Add more scoring dimensions (e.g., color harmony, item separation)
- [ ] Create a Gradio web UI for easy testing
