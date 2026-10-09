"""Inline pokemon-data.json into src/index.template.html -> index.html (single-file game)."""
import pathlib
root = pathlib.Path(__file__).parent
tpl = (root / "src/index.template.html").read_text(encoding="utf-8")
data = (root / "pokemon-data.json").read_text(encoding="utf-8").strip()
(root / "index.html").write_text(tpl.replace("/*DATA*/[]", data), encoding="utf-8")
print("wrote index.html")
