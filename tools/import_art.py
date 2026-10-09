"""Import free, openly licensed monster sprites and assign them to creature slots.

Sources (download them first; paths are arguments):
  --tux-set1 DIR   Tuxemon Set 1 (CC BY-SA 4.0): the unzipped folder holding "Set 1 - Tuxepedia.html"
                   https://opengameart.org/content/tuxemon-set-1-154-monsters-front-and-back-sprites-and-menu-animations
  --tux-repo DIR   A clone of https://github.com/Tuxemon/Tuxemon (for licensed monsters not in Set 1)
  --m50 DIR        "50+ Monsters Pack 2D" by isaiah658 (CC0), unzipped
                   https://opengameart.org/content/50-monsters-pack-2d

Writes sprites/NNN.png (64x64 front sprite for creature NNN) and art/credits.json.
Each source sprite is used once. Creatures with no match keep their generated pixel sprite.
"""
import argparse, colorsys, glob, hashlib, html, json, os, pathlib, re
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ELEMENT_TYPES = {"fire": {"fire", "dragon"}, "water": {"water", "ice"}, "wood": {"grass", "bug", "poison"},
                 "earth": {"ground", "rock", "fighting"}, "metal": {"steel", "electric"}}
COLOR_IDS = {"black": 1, "blue": 2, "brown": 3, "gray": 4, "green": 5, "pink": 6, "purple": 7, "red": 8, "white": 9, "yellow": 10}
EXTRA_TUX = ["fruitera", "axolightl", "ferricran", "merlicun", "firomenis", "snowrilla", "selket",
             "selmatek", "spycozeus", "pilthropus", "teddisun"]


def color_category(img):
    """Dominant Pokédex-style color of a sprite, ignoring outlines and transparent pixels."""
    votes = {}
    for r, g, b, a in img.get_flattened_data():
        if a < 200: continue
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if l < .12: continue
        if s < .18 or l > .9:
            c = "white" if l > .75 else "gray" if l > .3 else "black"
        else:
            hd = h * 360
            if hd < 15 or hd >= 345: c = "pink" if l > .65 else "red"
            elif hd < 45: c = "brown" if l < .55 else "yellow" if hd > 38 else "brown"
            elif hd < 70: c = "yellow"
            elif hd < 170: c = "green"
            elif hd < 255: c = "blue"
            elif hd < 290: c = "purple"
            else: c = "pink"
        votes[c] = votes.get(c, 0) + 1
    return COLOR_IDS[max(votes, key=votes.get)] if votes else 4


def load_set1(d):
    page = open(os.path.join(d, "Set 1 - Tuxepedia.html"), encoding="utf-8", errors="replace").read()
    out = []
    for row in re.findall(r'<tr class="row-(?:even|odd)"[^>]*>(.*?)</tr>', page, re.S):
        def cell(cls):
            m = re.search(r'<td class="[^"]*\b' + cls + r'\b[^"]*"[^>]*>(.*?)</td>', row, re.S)
            return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1)))).strip() if m else ""
        name = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<td[^>]*>(.*?)</td>", row, re.S).group(1))).strip()
        src = re.search(r'class="Default64px[^"]*"[^>]*><img[^>]*src="\./Set%201%20-%20Tuxepedia_files/([^"]+)"', row)
        if not src: continue
        img = Image.open(os.path.join(d, "Set 1 - Tuxepedia_files", src.group(1).replace("%20", " "))).convert("RGBA")
        out.append({"img": img, "name": name, "elements": cell("TXMN-Type").lower().split(), "pack": "Tuxemon Set 1",
                    "credit": cell("Source-Explanation"), "license": "CC BY-SA 4.0",
                    "url": "https://opengameart.org/content/tuxemon-set-1-154-monsters-front-and-back-sprites-and-menu-animations"})
    return out


def load_repo(d):
    att = open(os.path.join(d, "ATTRIBUTIONS.md"), encoding="utf-8").read()
    out = []
    for slug in EXTRA_TUX:
        sheet = os.path.join(d, "mods/tuxemon/gfx/sprites/battle", f"{slug}-sheet.png")
        if not os.path.exists(sheet): continue
        entry = next((e for e in re.split(r"\n\* ", att) if re.sub(r"[^a-z]", "", e.split('"]')[0].lower()) == slug), "")
        lic = re.search(r"\[(CC[- ]?BY[- A-Z0-9.]*?|Public Domain)\]", entry)
        if not lic: continue
        meta = os.path.join(d, "mods/tuxemon/db/monster", f"{slug}.yaml")
        types = re.findall(r"^- (\w+)$", open(meta).read().split("types:")[1].split("\n\n")[0], re.M) if os.path.exists(meta) and "types:" in open(meta).read() else []
        credit = html.unescape(re.sub(r"\]\([^)]*\)", "", re.sub(r"\s+", " ", entry)).replace("[", "")).strip()
        out.append({"img": Image.open(sheet).convert("RGBA").crop((0, 0, 64, 64)), "name": slug.capitalize(),
                    "elements": [t.lower() for t in types], "pack": "Tuxemon", "credit": credit,
                    "license": lic.group(1).replace("-", " ").replace("CC BY SA", "CC BY-SA"), "url": "https://github.com/Tuxemon/Tuxemon"})
    return out


def load_m50(d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, "**", "*Front*.png"), recursive=True)):
        m = re.search(r"Monster #(\d+) Front (Normal|Alternative)", f)
        if not m: continue
        out.append({"img": Image.open(f).convert("RGBA"), "name": f"Monster #{m.group(1)}" + (" (alt colors)" if m.group(2) == "Alternative" else ""),
                    "elements": [], "pack": "50+ Monsters Pack 2D", "credit": "By isaiah658", "license": "CC0 1.0",
                    "url": "https://opengameart.org/content/50-monsters-pack-2d"})
    return out


def load_extra():
    """Sprites sliced by tools/import_more.py (art/extra.json)."""
    f = ROOT / "art" / "extra.json"
    if not f.exists(): return []
    return [{"img": Image.open(ROOT / "art" / "extra" / e["file"]).convert("RGBA"), "elements": [],
             **{k: e[k] for k in ("name", "pack", "credit", "license", "url")}} for e in json.loads(f.read_text(encoding="utf-8"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tux-set1"); ap.add_argument("--tux-repo"); ap.add_argument("--m50")
    a = ap.parse_args()
    art = (load_set1(a.tux_set1) if a.tux_set1 else []) + (load_repo(a.tux_repo) if a.tux_repo else []) + (load_m50(a.m50) if a.m50 else []) + load_extra()
    for s in art:
        s["color"] = color_category(s["img"])
        s["key"] = hashlib.md5(s["img"].tobytes()).hexdigest()
    seen, uniq = set(), []
    for s in art:
        if s["key"] not in seen: seen.add(s["key"]); uniq.append(s)
    dex = json.loads((ROOT / "pokemon-data.json").read_text(encoding="utf-8"))
    pairs = []
    for i, s in enumerate(uniq):
        types = set().union(*[ELEMENT_TYPES.get(e, set()) for e in s["elements"]]) if s["elements"] else set()
        for d in dex:
            score = (3 if types & set(d[3]) else 0) + (2 if s["color"] == d[9] else 0)
            tie = int(hashlib.md5(f"{i}-{d[0]}".encode()).hexdigest()[:6], 16) / 16 ** 6
            pairs.append((score + tie, i, d[0]))
    pairs.sort(reverse=True)
    used_s, used_p, credits = set(), set(), {}
    out_dir = ROOT / "sprites"; out_dir.mkdir(exist_ok=True)
    for f in out_dir.glob("[0-9][0-9][0-9].png"): f.unlink()
    for score, i, pid in pairs:
        if i in used_s or pid in used_p: continue
        used_s.add(i); used_p.add(pid); s = uniq[i]
        s["img"].save(out_dir / f"{pid:03d}.png", optimize=True)
        credits[pid] = {k: s[k] for k in ("name", "pack", "credit", "license", "url")}
    (ROOT / "art").mkdir(exist_ok=True)
    (ROOT / "art" / "credits.json").write_text(json.dumps({f"{k:03d}": v for k, v in sorted(credits.items())}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(uniq)} unique sprites assigned to {len(credits)} of {len(dex)} creatures")
    from collections import Counter; print(Counter(c["pack"] for c in credits.values()))


if __name__ == "__main__":
    main()
