"""Generate creature art with the OpenAI image API and save it as sprites/NNN.png.

Needs OPENAI_API_KEY in the environment and network access to api.openai.com.
Safe to re-run: creatures that already have an image are skipped unless --redo is given.

  python3 tools/generate_sprites.py --ids 1-10          # small test batch
  python3 tools/generate_sprites.py                     # everything still missing
  python3 tools/generate_sprites.py --redo --ids 25,76  # regenerate specific ones
"""
import argparse, base64, concurrent.futures as cf, io, json, os, pathlib, sys, time
import requests
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "sprites"
API = "https://api.openai.com/v1/images/generations"


def parse_ids(spec, all_ids):
    if not spec:
        return all_ids
    ids = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-"); ids.update(range(int(a), int(b) + 1))
        else:
            ids.add(int(part))
    return [i for i in all_ids if i in ids]


def generate(pid, prompt, args, key):
    body = {"model": args.model, "prompt": prompt, "size": "1024x1024", "n": 1,
            "quality": args.quality, "background": "transparent", "output_format": "png"}
    for attempt in range(5):
        r = requests.post(API, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=180)
        if r.status_code == 200:
            img = Image.open(io.BytesIO(base64.b64decode(r.json()["data"][0]["b64_json"]))).convert("RGBA")
            img = img.resize((args.size, args.size), Image.LANCZOS)
            img.save(OUT / f"{pid:03d}.png", optimize=True)
            return pid, "ok"
        if r.status_code in (429, 500, 502, 503):
            time.sleep(2 ** attempt * 3); continue
        return pid, f"error {r.status_code}: {r.text[:200]}"
    return pid, "gave up after retries"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="e.g. 1-10 or 25,76,150")
    ap.add_argument("--redo", action="store_true", help="regenerate even if the image exists")
    ap.add_argument("--model", default="gpt-image-1")
    ap.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--size", type=int, default=256, help="saved image size in pixels")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY is not set. Add it in the environment settings, then start a new session.")
    prompts = json.loads((OUT / "prompts.json").read_text(encoding="utf-8"))
    ids = parse_ids(args.ids, sorted(int(k) for k in prompts))
    todo = [i for i in ids if args.redo or not (OUT / f"{i:03d}.png").exists()]
    print(f"{len(todo)} to generate ({len(ids) - len(todo)} already done)")
    done = 0
    with cf.ThreadPoolExecutor(args.workers) as ex:
        futs = [ex.submit(generate, i, prompts[f"{i:03d}"]["prompt"], args, key) for i in todo]
        for f in cf.as_completed(futs):
            pid, status = f.result(); done += 1
            print(f"[{done}/{len(todo)}] #{pid:03d} {status}", flush=True)


if __name__ == "__main__":
    main()
