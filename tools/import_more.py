"""Slice extra openly licensed creature packs into 64x64 sprites for import_art.py.

Usage: python3 tools/import_more.py DOWNLOAD_DIR
DOWNLOAD_DIR holds the unzipped packs (folder names below). Writes art/extra/*.png and art/extra.json.
Only creature sprites are kept; effects, props and people are left out by the curated lists.
"""
import json, os, pathlib, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OGA = "https://opengameart.org/content/"
PACKS = {
    "mrpg2": {"pack": "Monster RPG 2", "credit": "By troutsneeze (Nooskewl)", "license": "CC0 1.0", "url": OGA + "main-art-from-monster-rpg-2"},
    "c3": {"pack": "Assorted 32x32 creatures", "credit": "By AndHeGames", "license": "CC0 1.0", "url": OGA + "assorted-32x32-creatures"},
    "tl": {"pack": "Various Creatures", "credit": "By GrafxKid", "license": "CC0 1.0", "url": OGA + "various-creatures"},
    "nh2": {"pack": "Nighthawking 2 Battlers", "credit": "By Teo/Saorlaith (@mnaago), commissioned and shared by benamas", "license": "CC BY-SA 4.0", "url": OGA + "nighthawking-2-battlers"},
    "dawn": {"pack": "DawnLike", "credit": "By DragonDePlatino, palette by DawnBringer", "license": "CC BY 4.0", "url": OGA + "dawnlike-16x16-universal-rogue-like-tileset-v181"},
    "flame": {"pack": "Flamelings", "credit": "By Surt, shared by leeor_net", "license": "CC BY 3.0", "url": OGA + "flamelings-sprites"},
}
MRPG2 = ["Beast", "BigBlue", "Chomper", "Coyote", "Cub", "Daisy", "Devil", "Efreet", "Envy", "FireAnt",
         "Flamer", "Fungus", "Gator", "Glace", "Goo", "Grinner", "Harpy", "Hornet", "Husk", "Larva", "Leech",
         "Macrocat", "Magmod", "Meatball", "Millipede", "Nanner", "Octopus", "Possessed", "Rage", "Rocky",
         "Seeker", "Shadow", "Shroom", "Slime", "Sludge", "Spider", "Statue", "Stomp", "Stomper", "Thornster", "Toad", "Treant",
         "Twister", "Vinester", "Viper", "Vulture", "Wasp", "Wolf", "Lava", "Bud", "Troll"]
NH2 = ["angry crow", "angry goose", "brain jar", "candle knight", "cerby", "ghost", "hellhound", "kraken", "lich", "mimic chest",
       "mimic door", "mimic spellbook", "owl", "reaper", "robe boy", "skeleton default", "skeleton fire", "skeleton shield",
       "skeleton sword", "stray dog"]

# DawnLike creature sheets (people sheets left out) and how many sprites to take from each
DAWN = {"Aquatic": 10, "Avian": 12, "Cat": 6, "Demon": 10, "Dog": 8, "Elemental": 10, "Misc": 6, "Pest": 12,
        "Plant": 8, "Quadraped": 12, "Reptile": 12, "Rodent": 5, "Slime": 6, "Undead": 8}
DAWN_SKIP = {"Reptile 11", "Reptile 12", "Pest 1", "Pest 3", "Pest 5", "Plant 7", "Elemental 8"}  # tiles that are not creatures

# props and labels on the assorted sheet, not creatures
C3_SKIP = {28, 30, 40, 49, 53, 57, 63, 64, 65, 66}


def first_frame(im):
    """Animation strips: keep the first block of columns that contain pixels."""
    a = im.getchannel("A"); w, h = im.size
    cols = [any(a.getpixel((x, y)) > 0 for y in range(h)) for x in range(w)]
    if not any(cols): return im
    x0 = cols.index(True); x1 = x0
    while x1 < w and cols[x1]: x1 += 1
    # small gaps inside one creature are common; only split on a clear gap of 3+ empty columns
    while True:
        gap = 0; j = x1
        while j < w and not cols[j] and gap < 3: gap += 1; j += 1
        if gap < 3 and j < w and cols[j]:
            x1 = j
            while x1 < w and cols[x1]: x1 += 1
        else: break
    return im.crop((x0, 0, x1, h))


def knock_out(im, colors):
    im = im.convert("RGBA"); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][:3] in colors: px[x, y] = (0, 0, 0, 0)
    return im


def fit64(im):
    bb = im.getchannel("A").getbbox()
    if not bb: return None
    im = im.crop(bb); w, h = im.size; k = 60 / max(w, h)
    if k >= 1: k = max(1, int(k))  # whole-number upscale keeps pixels square
    im = im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.NEAREST if k >= 1 else Image.LANCZOS)
    out = Image.new("RGBA", (64, 64), (0, 0, 0, 0)); out.paste(im, ((64 - im.width) // 2, 62 - im.height), im)
    return out


def main(src):
    items = []
    d = os.path.join(src, "mrpg2", "combat_media")
    for n in MRPG2:
        f = os.path.join(d, n + ".png")
        if os.path.exists(f): items.append(("mrpg2", n, first_frame(Image.open(f).convert("RGBA"))))
    for n in NH2:
        f = os.path.join(src, "nh2", n + ".png")
        if os.path.exists(f): items.append(("nh2", n.title(), Image.open(f).convert("RGBA")))
    sheet = Image.open(os.path.join(src, "misc", "creatures_3.png")).convert("RGBA")
    k = 0
    for r in range(9):
        for c in range(9):
            cell = sheet.crop((c * 32, r * 32, c * 32 + 32, r * 32 + 32))
            if cell.getchannel("A").getbbox() and not (r == 7 and c == 8) and r < 8:
                k += 1
                if k not in C3_SKIP: items.append(("c3", f"Creature {k}", cell))
    tl = Image.open(os.path.join(src, "misc", "TL_Creatures.png")).convert("RGBA")
    for r in range(1, 10):
        cell = tl.crop((64, r * 32, 96, r * 32 + 32))
        corners = {cell.getpixel(p)[:3] for p in [(0, 0), (31, 0), (0, 31), (31, 31), (1, 1), (30, 30)]}
        items.append(("tl", f"Creature {r}", knock_out(cell, corners)))
    fl = Image.open(os.path.join(src, "misc", "flamelings_sprites.png")).convert("RGBA")
    for i, nm in enumerate(["Flameling", "Flamerider", "Flamelord"]):
        cell = fl.crop((i * 128, 0, i * 128 + 128, 128)); bg = cell.getpixel((0, 0))[:3]
        items.append(("flame", nm, knock_out(cell, {bg})))
    for sheet_name, quota in DAWN.items():
        f = os.path.join(src, "dawn", "Characters", sheet_name + "0.png")
        if not os.path.exists(f): continue
        im = Image.open(f).convert("RGBA"); cells = []
        for y in range(0, im.height, 16):
            for x in range(0, im.width, 16):
                cell = im.crop((x, y, x + 16, y + 16))
                if cell.getchannel("A").getbbox(): cells.append(cell)
        step = max(1, len(cells) // quota)
        for j, cell in enumerate(cells[::step][:quota]):
            nm = f"{sheet_name} {j + 1}"
            if nm not in DAWN_SKIP: items.append(("dawn", nm, cell))
    out = ROOT / "art" / "extra"; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"): f.unlink()
    meta = []
    for i, (key, name, im) in enumerate(items):
        im = fit64(im)
        if im is None: continue
        fn = f"{key}_{i:03d}.png"; im.save(out / fn, optimize=True)
        meta.append({"file": fn, "name": name, **PACKS[key]})
    (ROOT / "art" / "extra.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote {len(meta)} extra sprites")


if __name__ == "__main__":
    main(sys.argv[1])
