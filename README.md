# Pokémon All-22 Draft

A single-page drafting game. Pick a pool (Gen 1, 2, 3, 4, or all of Gens 1–4), then fill all 22 football starting spots. Each round the board lands on a random open position and deals three random Pokémon. Pick one. Base stats, type and size decide how well each Pokémon plays that spot.

- Open `index.html` in any browser. No install needed.
- `pokemon-data.json`: names, generation, types, base stats, height and weight for #1–493, built from the PokeAPI CSV data.
- Edit the game in `src/index.template.html`, then run `python3 build.py` to rebuild `index.html` with the data inlined.
