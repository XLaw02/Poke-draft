"""Write sprites/review.html: a contact sheet of every generated image, to spot rejects fast."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = {f"{d[0]:03d}": d[1] for d in json.loads((ROOT / "pokemon-data.json").read_text(encoding="utf-8"))}
imgs = sorted(p.stem for p in (ROOT / "sprites").glob("[0-9][0-9][0-9].png"))
cells = "".join(
    f'<label class="c"><img src="{i}.png" alt=""><span>#{i} {data[i]}</span><input type="checkbox" value="{int(i)}"> redo</label>'
    for i in imgs)
html = f"""<title>Sprite Review</title>
<style>
:root{{--bg:#0d2a1c;--fg:#eef3ea;--dim:#9fb5a6;--cell:#123825;--gold:#f2c14e;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font:14px system-ui,sans-serif;padding-inline:16px;padding-block:16px}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px}}
.c{{background:var(--cell);border-radius:8px;padding:6px;display:flex;flex-direction:column;align-items:center;gap:4px;font-size:12px;cursor:pointer}}
.c img{{width:110px;height:110px;image-rendering:pixelated}} .c span{{color:var(--dim)}}
button{{background:var(--gold);border:0;border-radius:6px;padding:8px 14px;font-weight:700}}
#out{{width:100%;margin-top:8px;background:var(--cell);color:var(--fg);border:1px solid var(--dim)}}
</style>
<h1>Sprite Review ({len(imgs)} images)</h1>
<p>Tick any image that looks wrong or resembles an existing character, then press the button and send me the list.</p>
<p><button id="b">Show redo list</button></p><textarea id="out" rows="2" readonly></textarea>
<div class="g">{cells}</div>
<script>
document.getElementById("b").onclick=()=>{{const v=[...document.querySelectorAll("input:checked")].map(i=>i.value).join(",");
const o=document.getElementById("out");o.value=v||"(none ticked)";o.select();try{{navigator.clipboard.writeText(v)}}catch(e){{}}}};
</script>"""
(ROOT / "sprites" / "review.html").write_text(html, encoding="utf-8")
print(f"wrote sprites/review.html with {len(imgs)} images")
