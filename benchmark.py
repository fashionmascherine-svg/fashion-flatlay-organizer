#!/usr/bin/env python3
"""
benchmark.py — Fashion Flat-Lay Organizer: Free API Benchmark Runner
Compares multiple free AI APIs for organizing messy clothing photos.

Usage:
    python benchmark.py --image path/to/clothes.jpg [--providers all] [--output results/]

Author: Lorenzo Nardi
"""

import argparse
import asyncio
import json
import os
import time
from pathlib import Path
from datetime import datetime

# Load .env BEFORE importing providers so env vars are available
from dotenv import load_dotenv
load_dotenv()

from providers import pollinations, huggingface, cloudflare, siliconflow, fashn, gemini_pipeline
from scorer import score_result
from report import generate_html_report

PROVIDERS = {
    "pollinations": pollinations.generate,
    "huggingface": huggingface.generate,
    "cloudflare": cloudflare.generate,
    "siliconflow": siliconflow.generate,
    "fashn": fashn.generate,
    "gemini_pipeline": gemini_pipeline.generate,
}

BASE_PROMPT = (
    "Professional fashion flat lay photo. "
    "Organize ALL these items neatly on a clean white marble surface: "
    "- 3 pairs of shoes: orange wedge sandals, nude beige wedge sandals, gold metallic strappy heels. "
    "- 3 bags: black structured handbag, striped canvas tote (orange/white/green), small red crossbody clutch. "
    "- 6 clothing items: beige camel blazer, pink chiffon sheer scarf/top, turquoise aqua blouse, red coral jacket (folded), additional garments. "
    "Arrangement: clothing laid flat top-left, shoes paired bottom-right, bags center-right. "
    "Style: editorial fashion photography, overhead shot (bird-eye view), even soft lighting, no shadows. "
    "DO NOT omit any item. All items must be visible."
)

WATERFALL_ORDER = ["gemini_pipeline", "cloudflare", "huggingface", "siliconflow", "fashn", "pollinations"]


def parse_args():
    p = argparse.ArgumentParser(description="Fashion Flat-Lay Free API Benchmark")
    p.add_argument("--image", required=True, help="Path to input messy clothing image")
    p.add_argument("--providers", default="all", help="Comma-separated providers or 'all'")
    p.add_argument("--output", default="results", help="Output directory")
    p.add_argument("--waterfall", action="store_true", help="Stop at first successful provider")
    p.add_argument("--prompt", default=BASE_PROMPT, help="Custom prompt override")
    return p.parse_args()


async def run_provider(name: str, fn, image_path: str, prompt: str, out_dir: Path) -> dict:
    """Run a single provider and return result dict."""
    print(f"\n⏳  [{name.upper()}] Starting...")
    start = time.time()
    result = {
        "provider": name,
        "status": "error",
        "output_path": None,
        "elapsed_sec": None,
        "error": None,
        "scores": {},
        "total_score": 0,
    }
    try:
        output_path = out_dir / f"{name}_output.jpg"
        success = await fn(
            image_path=image_path,
            prompt=prompt,
            output_path=str(output_path),
        )
        elapsed = round(time.time() - start, 2)
        result["elapsed_sec"] = elapsed

        if success and output_path.exists():
            result["status"] = "success"
            result["output_path"] = str(output_path)
            scores = score_result(str(output_path), elapsed)
            result["scores"] = scores
            result["total_score"] = scores["total"]
            print(f"  ✅  [{name.upper()}] Done in {elapsed}s — score: {scores['total']:.1f}/10")
        else:
            result["error"] = "No output file generated"
            print(f"  ❌  [{name.upper()}] Failed — no output")

    except Exception as e:
        result["elapsed_sec"] = round(time.time() - start, 2)
        result["error"] = str(e)
        print(f"  ❌  [{name.upper()}] Error: {e}")

    return result


async def main():
    args = parse_args()
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.providers == "all":
        selected = WATERFALL_ORDER if args.waterfall else list(PROVIDERS.keys())
    else:
        selected = [p.strip() for p in args.providers.split(",")]

    print(f"\n🎯 Fashion Flat-Lay Benchmark")
    print(f"   Input: {image_path}")
    print(f"   Providers: {selected}")
    print(f"   Output dir: {out_dir}")
    print(f"   Mode: {'waterfall' if args.waterfall else 'parallel'}")
    print("=" * 60)

    results = []

    if args.waterfall:
        for name in selected:
            if name not in PROVIDERS:
                continue
            r = await run_provider(name, PROVIDERS[name], str(image_path), args.prompt, out_dir)
            results.append(r)
            if r["status"] == "success":
                print(f"\n🏆 Waterfall: {name} succeeded, stopping.")
                break
    else:
        tasks = [
            run_provider(name, PROVIDERS[name], str(image_path), args.prompt, out_dir)
            for name in selected if name in PROVIDERS
        ]
        results = await asyncio.gather(*tasks)

    results = sorted(results, key=lambda x: x["total_score"], reverse=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"benchmark_{ts}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved: {json_path}")

    report_path = out_dir / "report.html"
    generate_html_report(results, str(image_path), str(report_path))
    print(f"📊 Report generated: {report_path}")

    print("\n" + "=" * 60)
    print("📋 FINAL RANKING")
    print("=" * 60)
    for i, r in enumerate(results, 1):
        status = "✅" if r["status"] == "success" else "❌"
        print(f"  {i}. {status} [{r['provider'].upper():<20}] Score: {r['total_score']:5.1f}/10  Time: {r['elapsed_sec'] or 'N/A'}s")

    winner = next((r for r in results if r["status"] == "success"), None)
    if winner:
        print(f"\n🥇 WINNER: {winner['provider'].upper()} (score: {winner['total_score']:.1f}/10)")


if __name__ == "__main__":
    asyncio.run(main())
