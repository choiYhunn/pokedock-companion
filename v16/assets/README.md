# V16 asset content contract — signed offline packs
No Pokémon images, proprietary music, actual birthday letters, or other personal material are committed here.

## For a private gift
Create artwork you own or are authorized to use in an external asset folder. Package each character's idle/enter/exit/hop/dance/spin/celebrate sequence as frame files. Each animation needs a manifest timeline specifying frame durations; **the production MCU decoder/timeline renderer is not implemented yet.**
Prototype format suggestions: 256x256 RGBA frames / 24fps target; build level may require RGB565 conversion, PSRAM budget and SD streaming validation. The browser preview vector placeholders prove interaction flow only, not optical scene quality.

## Developer-only signing
Generate an offline Ed25519 key pair (keep private key outside repo).
- Sign: node v16/tools/assets.cjs sign /path/to/assets 1.0.0 /secure/private.pem
- Verify: node v16/tools/assets.cjs verify /path/to/assets /trusted/public.pem
- Verify should fail if an asset is changed, removed or swapped, or if the signature is invalid.
The device will eventually contain the pinned public key, never the private key.
- Do not put personal notes in a public asset archive.
- The signed pack can be staged on an SD card, **but device-side mounting, signature verification, atomic swap and rollback do not exist yet**.

A SHA256 list by itself is not authentication; the signature protects the manifest when the public key is trusted.

### GHF1 compressed animation frames
- User-supplied authorized GIF/PNG -> `python3 v16/tools/ghf_codec.py input.gif out/ --character gengar --width 256 --height 256`.
- Run `bash v16/scripts/test_host_codec.sh` (requires Pillow). The produced `.ghf` files and index JSON are accepted by the host Ed25519 signer after the 2026-10-21 extension allowlist fix.
- Native on-device safe pack staging/swap, soundtrack and screen renderer **remain unimplemented**; do not claim that the signed host pack installs over OTA yet.
