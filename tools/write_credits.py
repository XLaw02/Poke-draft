"""Write CREDITS.md from art/credits.json."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
c = json.loads((ROOT / "art" / "credits.json").read_text(encoding="utf-8"))
dex = {f"{d[0]:03d}": d[1] for d in json.loads((ROOT / "pokemon-data.json").read_text(encoding="utf-8"))}
packs = {}
for v in c.values(): packs.setdefault((v["pack"], v["license"], v["url"], v["credit"] if v["pack"] not in ("Tuxemon Set 1", "Tuxemon") else "see each entry"), 0)
lines = ["# Art credits", "",
         "Every creature sprite in `sprites/` comes from a free, openly licensed pack. Sprites are cropped or scaled to 64x64; nothing else is changed.", "",
         "| Pack | Artist | License | Source |", "|---|---|---|---|"]
for (pack, lic, url, credit) in sorted(packs):
    lines.append(f"| {pack} | {credit} | {lic} | {url} |")
lines += ["", "DawnLike uses the DawnBringer 16-color palette; credit to DawnBringer is required by the artist.",
          "Sprites under CC BY-SA stay under that license: https://creativecommons.org/licenses/by-sa/4.0/", "",
          "| # | Slot | Sprite | Credit | License |", "|---|---|---|---|---|"]
for k, v in c.items():
    lines.append(f"| {k} | {dex[k]} | {v['name']} ({v['pack']}) | {v['credit'].replace('|', '/')} | {v['license']} |")
(ROOT / "CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote CREDITS.md")
