"""Inline pokemon-data.json into src/index.template.html -> index.html (single-file game).
Also lists any generated art in sprites/NNN.png so the game shows it instead of the pixel sprite."""
import json, pathlib
root = pathlib.Path(__file__).parent
tpl = (root / "src/index.template.html").read_text(encoding="utf-8")
data = (root / "pokemon-data.json").read_text(encoding="utf-8").strip()
art = sorted(int(p.stem) for p in (root / "sprites").glob("[0-9][0-9][0-9].png"))
html = tpl.replace("/*DATA*/[]", data).replace("/*ART*/[]", json.dumps(art))
(root / "index.html").write_text(html, encoding="utf-8")
print(f"wrote index.html ({len(art)} generated images)")
