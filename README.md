# Pokémon All-22 Draft

A single-page drafting game. Pick a pool (Gen 1, 2, 3, 4, or all of Gens 1–4), then fill all 22 football starting spots. Each round the board lands on a random open position and deals three random Pokémon. Pick one. Base stats, type and size decide how well each Pokémon plays that spot.

- Every Pokémon is shown as an original creature generated from its own Pokédex data: body type (four-legged, upright, humanoid, bird, fish, snake, insect, tentacled and more), color category, evolution stage, types, stats and weight. Seeded style choices (ears, tail, markings, crest, eyes) make each one distinct, and each gets one original signature trait (chest gem, runes, mane, scarf, crystal antlers, glow freckles, back shell, tail ribbon, orbit ring, lantern orb or face paint).
- Creatures are shown as 64×64 pixel-art sprites: the browser rasterizes each creature, reduces it to a 12-color palette with ordered dithering, then adds a 1px outline, rim light and shading. Draft cards play a 2-frame idle animation.
- Open `index.html` in any browser. No install needed.
- `pokemon-data.json`: names, generation, types, base stats, height and weight for #1–493, built from the PokeAPI CSV data.
- Edit the game in `src/index.template.html`, then run `python3 build.py` to rebuild `index.html` with the data inlined.
