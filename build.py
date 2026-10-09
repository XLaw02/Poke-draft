"""Inline pokemon-data.json and sprite art into src/index.template.html -> index.html (single-file game).
sprites/NNN.png files are embedded as data URIs; art/credits.json supplies their credits."""
import base64, json, pathlib
root = pathlib.Path(__file__).parent
tpl = (root / "src/index.template.html").read_text(encoding="utf-8")
data = (root / "pokemon-data.json").read_text(encoding="utf-8").strip()
art = {int(p.stem): "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
       for p in sorted((root / "sprites").glob("[0-9][0-9][0-9].png"))}
cred_file = root / "art" / "credits.json"
credits = {int(k): v for k, v in json.loads(cred_file.read_text(encoding="utf-8")).items()} if cred_file.exists() else {}
html = (tpl.replace("/*DATA*/[]", data)
           .replace("/*ART*/{}", json.dumps(art, separators=(",", ":")))
           .replace("/*CREDITS*/{}", json.dumps(credits, separators=(",", ":"), ensure_ascii=False)))
(root / "index.html").write_text(html, encoding="utf-8")
print(f"wrote index.html ({len(art)} sprite images, {len(credits)} credits, {len(html)//1024} KB)")
