"""Write sprites/prompts.json: one image prompt per creature, built from its game traits.

Prompts describe original creatures only. They never include Pokémon names, the franchise,
or any character's signature design, so the generated art is new.
"""
import json, math, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

STYLE = ("Original fantasy creature for a monster-drafting game. 16-bit pixel art sprite, "
         "crisp 1px dark outline, limited 16-color palette with clean shading, light from the top left, "
         "three-quarter view facing right, full body centered, plain transparent background, "
         "no text, no border, no shadow box. Original design, not based on any existing character, "
         "franchise or video game.")

BODY = {
    1: "a round, ball-shaped creature with tiny stubby feet",
    2: "a long, snake-like creature with no legs, coiled in a loose S-shape",
    3: "a fish-like swimming creature with a tail fin and side fins",
    4: "a floating creature that is mostly a large head, with two arms and no legs",
    5: "a soft, amorphous blob creature",
    6: "an upright, two-legged creature with short arms and a tail",
    7: "a creature whose round head is its whole body, standing on two legs",
    8: "a four-legged creature",
    9: "a bird-like creature with one pair of feathered wings and two thin legs",
    10: "a floating creature with a dome-shaped body and dangling tentacles",
    11: "a creature with several small heads on one body",
    12: "a humanoid creature standing on two legs, with two arms",
    13: "an insect with a segmented body, thin legs and translucent wings",
    14: "an armored insect with a segmented shell and several legs",
}
COLOR = {1: "black", 2: "blue", 3: "brown", 4: "gray", 5: "green", 6: "pink", 7: "purple", 8: "red", 9: "white", 10: "yellow"}
TYPE = {
    "normal": "soft fur", "fire": "warm glowing embers drifting around it", "water": "smooth wet scales",
    "electric": "small sparks crackling around its body", "grass": "leafy sprouts growing from its head",
    "ice": "frosty crystal spikes", "fighting": "a cloth headband and a strong stance",
    "poison": "toxic purple blotches on its skin", "ground": "dusty, earth-toned speckled hide",
    "flying": "light feathers", "psychic": "a small glowing gem on its forehead",
    "bug": "segmented banded plates", "rock": "cracked stone plates on its back",
    "ghost": "a faintly translucent, wispy edge", "dragon": "a ridge of small back spikes and scales",
    "dark": "a shadowy mask-like marking over its eyes", "steel": "riveted metal plating",
    "fairy": "a tiny sparkling star near its head",
}
SIG = {
    "gem": "a glowing faceted gem set in its chest", "runes": "three glowing rune marks along its body",
    "mane": "a fluffy mane around its head", "scarf": "a scarf tied around its neck",
    "antlers": "small branching crystal antlers", "freckles": "glowing freckles on its cheeks",
    "shell": "a domed shell on its back", "ribbon": "a ribbon bow tied near its tail",
    "orbit": "a small glowing orb circling its body on a thin ring", "lantern": "a glowing lantern orb hanging on a stalk above its head",
    "paint": "chevron face paint on its cheeks",
}
SIG_ORDER = ["gem", "runes", "mane", "scarf", "antlers", "freckles", "shell", "ribbon", "orbit", "lantern", "paint"]
SIG_COLOR = ["gold", "teal", "pink", "lavender", "lime green", "orange"]


def rng32(seed):
    """Same generator as the game (mulberry32), so prompts match each creature's in-game trait."""
    s = seed & 0xFFFFFFFF
    def nxt():
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF
        t = ((s ^ (s >> 15)) * (1 | s)) & 0xFFFFFFFF
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return nxt


def signature(pid, shape):
    r = rng32(pid * 104729 + 7)
    sig = SIG_ORDER[math.floor(r() * len(SIG_ORDER))]
    col = SIG_COLOR[math.floor(r() * 6)]
    if sig == "shell" and shape not in (8, 9, 11, 13, 14):
        sig = "gem"
    return sig, col


def describe(d):
    pid, _name, _gen, types, st, _h, wt, leg, shape, color, stage, max_stage, baby = d
    hp, atk, de, spa, spd, spe = st
    lb = wt * 0.2205
    size = "tiny" if lb < 15 else "small" if lb < 60 else "medium-sized" if lb < 250 else "large" if lb < 700 else "huge"
    if max_stage == 1 and not baby:
        age = "fully grown"
    elif baby or (max_stage > 1 and stage == 1):
        age = "young and round-eyed, with soft proportions"
    elif max_stage > 1 and stage == max_stage:
        age = "fully grown and imposing"
    else:
        age = "adolescent and sturdy"
    build = []
    if hp + de > 200: build.append("bulky and heavy-set")
    if spe >= 100: build.append("lean and quick-looking")
    if atk >= 100: build.append("with horns and sharp claws")
    elif atk >= 75: build.append("with a single small horn")
    if de >= 110: build.append("with a thick, armored hide")
    if spa >= 100: build.append("with large, intelligent eyes")
    if not build: build.append("with a friendly, balanced build")
    accent = " and ".join(types)
    feats = [TYPE[t] for t in types if t in TYPE]
    sig, sig_col = signature(pid, shape)
    parts = [
        f"A {size} {COLOR.get(color, 'gray')} {BODY.get(shape, BODY[6]).split(' ', 1)[1]}.",
        f"It is {age}, {', '.join(build)}.",
        f"Accent colors inspired by {accent} elements; it has {' and '.join(feats)}.",
        f"Signature detail: {SIG[sig].replace('glowing', sig_col + ' glowing', 1) if 'glowing' in SIG[sig] else SIG[sig] + ' in ' + sig_col}.",
    ]
    if leg:
        parts.append("It looks rare and majestic, with a subtle aura of power.")
    return " ".join(parts)


def main():
    data = json.loads((ROOT / "pokemon-data.json").read_text(encoding="utf-8"))
    out = {f"{d[0]:03d}": {"description": describe(d), "prompt": STYLE + " " + describe(d)} for d in data}
    (ROOT / "sprites").mkdir(exist_ok=True)
    (ROOT / "sprites" / "prompts.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(out)} prompts to sprites/prompts.json")


if __name__ == "__main__":
    main()
