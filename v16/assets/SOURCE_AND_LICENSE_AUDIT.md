# V16 animation source inventory & rights gate
The five exact PokéAPI paths were verified against the PokeAPI/sprites Git tree, not downloaded into the public project. Metadata is in [asset_sources.json](asset_sources.json).
- Gengar 94: Showdown animated GIF ~50KB, home/official static PNG.
- Piplup 393: animated GIF ~86KB.
- Togekiss 468: animated GIF ~32KB.
- Lucario 448: animated GIF ~62KB.
- Quagsire 195: animated GIF ~52KB.
These GIF files are SMALL PIXEL-ART REFERENCES, **not** a premium 24fps high-resolution delivery package. Individual frame counts, transparency/disposal and final viewing performance are NOT validated. Static artwork is useful to design custom timing and poses, but a still image doesn't deliver expressive animation alone.

## Legal quality boundary
Official Pokémon support currently requests that Pokémon IP not be used in associated projects. Public PokeAPI files are not permission to redistribute copyrighted character frames. Do not commit any Pokémon GIF/PNG, copyrighted voice/game audio, or private birthday data. Use custom authorized assets for distribution/hosting; any private-device use must comply with applicable rights. Repository scripts operate on files supplied locally by the user, without scraping.

## High-quality production
For each Pokémon (Gengar first), obtain a coherent original layered source and export:
- idle loop, enter, exit, jump, dance, a distinctive pose; preserve a stable anchor point.
- limited 2D motions that read at real apparent size ~35–50mm from 60cm.
- avoid fake photorealistic fur on tiny reflective images; clarity and contours matter more than microtexture.
- alpha edges should be inspected after RGB565+binary alpha conversion (low alpha clipped; dark background helps).
- gamma/contrast test on actual reflector; record ~150/300/500lux results at normal eye height.

## Converter, verifier
Requires Pillow: python3 -m pip install Pillow
Convert individual authorized animation file:
python3 v16/tools/ghf_codec.py ./my_authorized_idle.gif ./private_pack --character gengar --width 256 --height 256 --fps 12
Run validation: bash v16/scripts/test_host_codec.sh
Output .ghf per frame + *_index.json; then sign with v16/tools/assets.cjs. Decoder is in v16/firmware/ghf_decoder.h.

IMPORTANT: This is the **portable frame decoder**, not native RM690B0 streaming/SD renderer. Do not call GIF integration DONE until frames appear on V2 physical hardware at a measured cadence and transparency/background match the optical scene.
