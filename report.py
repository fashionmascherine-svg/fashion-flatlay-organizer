"""
report.py — HTML report generator for benchmark results.
Generates a beautiful dark-mode visual comparison page.
"""
import base64
from pathlib import Path
from datetime import datetime


def img_to_data_url(path: str) -> str:
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = Path(path).suffix.lower().replace(".", "")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
        return f"data:image/{mime};base64,{data}"
    except Exception:
        return ""


def generate_html_report(results: list, input_image: str, output_path: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    input_du = img_to_data_url(input_image)
    winner = results[0]["provider"].upper() if results else "N/A"

    cards = ""
    for i, r in enumerate(results, 1):
        rank = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣"][min(i-1,5)]
        sc = r.get("scores", {})
        total = r.get("total_score", 0)
        img_html = (f'<img src="{img_to_data_url(r["output_path"])}" alt="output" loading="lazy" />'
                    if r.get("output_path") else '<div class="noimg">❌ No output</div>')
        metrics = "".join([
            f'<div class="m"><span>{lbl}</span>'
            f'<div class="bar"><div class="fill" style="width:{int(sc.get(k,0)*10)}%;background:'
            f'{"#22c55e" if sc.get(k,0)>=7 else "#eab308" if sc.get(k,0)>=4 else "#ef4444"}"></div></div>'
            f'<b>{sc.get(k,0):.1f}</b></div>'
            for k, lbl in [("completeness","Completeness"),("organization","Organization"),("quality","Quality"),("speed","Speed")]
        ])
        st = "ok" if r["status"]=="success" else "err"
        elapsed = f"{r['elapsed_sec']}s" if r.get("elapsed_sec") else "N/A"
        err_html = f'<div class="err-msg">{r["error"]}</div>' if r.get("error") else ""
        cards += f"""
        <div class="card {st}">
          <div class="ch"><span class="rk">{rank}</span><h2>{r["provider"].replace("_"," ").upper()}</h2>
            <span class="badge {st}">{r["status"].upper()}</span></div>
          <div class="ci">{img_html}</div>
          <div class="cs">
            <div class="tot"><span>Total Score</span><big>{total:.1f}<small>/10</small></big></div>
            {metrics}
          </div>
          <div class="meta">⏱️ {elapsed}{err_html}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fashion Flat-Lay Benchmark</title>
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Satoshi',sans-serif;background:#0f0e0d;color:#e8e6e3;line-height:1.5}}
.wrap{{max-width:1400px;margin:0 auto;padding:2rem}}
header{{background:#1a1917;border-radius:12px;padding:2rem;text-align:center;margin-bottom:2rem}}
header h1{{font-size:1.8rem;color:#4f98a3;margin-bottom:.5rem}}
.meta{{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin-top:1rem}}
.meta span{{background:#222;padding:.25rem .75rem;border-radius:999px;font-size:.8rem}}
.input{{margin-bottom:2rem}}.input h2{{color:#7a7876;margin-bottom:.5rem;font-size:.9rem}}
.input img{{max-width:400px;border-radius:10px;border:1px solid #333}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:1.5rem}}
.card{{background:#1a1917;border-radius:12px;overflow:hidden;border:1px solid #2a2927}}
.card.ok{{border-color:#1a3a2a}}.card.err{{border-color:#3a1a1a;opacity:.7}}
.ch{{display:flex;align-items:center;gap:.75rem;padding:1rem 1.25rem;background:#222120}}
.rk{{font-size:1.4rem}}.ch h2{{flex:1;font-size:.85rem;letter-spacing:.05em}}
.badge{{padding:.15rem .5rem;border-radius:999px;font-size:.65rem;font-weight:700}}
.badge.ok{{background:#1a3a2a;color:#22c55e}}.badge.err{{background:#3a1a1a;color:#ef4444}}
.ci{{background:#111;aspect-ratio:16/9;overflow:hidden}}
.ci img{{width:100%;height:100%;object-fit:cover}}
.noimg{{display:flex;align-items:center;justify-content:center;height:200px;color:#555;font-size:2rem}}
.cs{{padding:1.25rem}}
.tot{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1rem}}
.tot span{{color:#7a7876;font-size:.85rem}}
.tot big{{font-size:2rem;font-weight:700;color:#4f98a3}}
.tot big small{{font-size:1rem;color:#7a7876}}
.m{{display:grid;grid-template-columns:90px 1fr 36px;gap:.4rem;align-items:center;margin-bottom:.4rem}}
.m span{{font-size:.75rem;color:#7a7876}}
.bar{{background:#2a2927;border-radius:999px;height:5px;overflow:hidden}}
.fill{{height:100%;border-radius:999px}}
.m b{{font-size:.75rem;text-align:right}}
.meta{{padding:.75rem 1.25rem;border-top:1px solid #222;font-size:.78rem;color:#7a7876}}
.err-msg{{color:#ef4444;margin-top:.25rem;word-break:break-all}}
footer{{text-align:center;padding:2rem;color:#555;font-size:.8rem}}
footer a{{color:#4f98a3}}
@media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>👗 Fashion Flat-Lay Benchmark Report</h1>
  <p>Free AI APIs comparison — messy clothes → organized flat-lay</p>
  <div class="meta">
    <span>📅 {ts}</span>
    <span>🆓 All free tier</span>
    <span>📊 {len(results)} providers</span>
    <span>🥇 {winner}</span>
  </div>
</header>
<div class="input">
  <h2>📸 INPUT: Messy clothes photo</h2>
  <img src="{input_du}" alt="Input" loading="lazy" />
</div>
<div class="grid">{cards}</div>
<footer>Generated by <a href="https://github.com/fashionmascherine-svg/fashion-flatlay-organizer" target="_blank">fashion-flatlay-organizer</a></footer>
</div></body></html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
