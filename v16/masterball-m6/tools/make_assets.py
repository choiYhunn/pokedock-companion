"""Build the private PDK1 sprite pack for the "assets" flash partition.

usage: python make_assets.py <private_dir> <out.bin>
<private_dir> holds files named <dex>_<anim>.gif (anim = idle, sleep, greet, jump, dance, touch,
cheer, celebrate, alarm, egg), e.g. 94_idle.gif. A plain <dex>.gif is used as the idle animation.
The pack stays on the owner's PC and is flashed with:
  esptool.py --chip esp32s3 write_flash 0x610000 out.bin
Never commit the GIFs or the .bin to the public repository (Pokémon artwork is not ours).
"""
import os
import struct
import sys

ANIMS = ["idle", "sleep", "greet", "jump", "dance", "touch", "cheer", "celebrate", "alarm", "egg"]
DEX = [94, 393, 468, 448, 195, 175, 417, 385]
MAX_W = 128
PARTITION_BYTES = 0x9F0000


def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def rle(indices):
    out = bytearray()
    i = 0
    while i < len(indices):
        v, run = indices[i], 1
        while i + run < len(indices) and indices[i + run] == v and run < 255:
            run += 1
        out += bytes((run, v))
        i += run
    return bytes(out)


def frames_from_gif(path):
    from PIL import Image, ImageSequence  # Pillow only needed for real GIFs

    im = Image.open(path)
    frames, durations = [], []
    for fr in ImageSequence.Iterator(im):
        rgba = fr.convert("RGBA")
        if rgba.width > MAX_W or rgba.height > MAX_W:
            raise SystemExit(f"{path}: {rgba.width}x{rgba.height} exceeds {MAX_W}px; integer-scale on device instead")
        frames.append(rgba)
        durations.append(fr.info.get("duration", im.info.get("duration", 100)) or 100)
    return frames, int(sum(durations) / len(durations))


def quantise(frames):
    """Shared palette per animation: index 0 = transparent, up to 255 opaque colours."""
    palette = {(0, 0, 0, 0): 0}
    idx_frames = []
    for fr in frames:
        idx = []
        for r, g, b, a in fr.getdata():
            key = (0, 0, 0, 0) if a < 128 else (r, g, b, 255)
            if key not in palette:
                if len(palette) >= 256:
                    raise SystemExit("more than 255 colours in one animation; reduce colours first")
                palette[key] = len(palette)
            idx.append(palette[key])
        idx_frames.append(idx)
    pal = sorted(palette.items(), key=lambda kv: kv[1])
    return [k for k, _ in pal], idx_frames


def build(entries):
    """entries: list of (dex, anim_id, w, h, frame_ms, palette[(r,g,b,a)], [index lists])."""
    head = bytearray(b"PDK1") + struct.pack("<HH", 1, len(entries))
    table_len = 20 * len(entries)
    blob = bytearray()
    rows = []
    for dex, anim, w, h, ms, pal, frames in entries:
        pal_off = 8 + table_len + len(blob)
        for r, g, b, a in pal:
            blob += struct.pack("<HB", rgb565(r, g, b), a)
        fr_off = 8 + table_len + len(blob)
        for f in frames:
            assert len(f) == w * h
            data = rle(f)
            blob += struct.pack("<I", len(data)) + data
        rows.append(struct.pack("<HBBHHHHII", dex, anim, len(frames), w, h, ms, len(pal), pal_off, fr_off))
    out = bytes(head) + b"".join(rows) + bytes(blob)
    if len(out) > PARTITION_BYTES:
        raise SystemExit(f"pack {len(out)} B exceeds assets partition {PARTITION_BYTES} B")
    return out


def main():
    src, dst = sys.argv[1:3]
    entries = []
    for dex in DEX:
        for anim_id, anim in enumerate(ANIMS):
            path = os.path.join(src, f"{dex}_{anim}.gif")
            if not os.path.exists(path) and anim == "idle":
                path = os.path.join(src, f"{dex}.gif")
            if not os.path.exists(path):
                continue
            frames, ms = frames_from_gif(path)
            pal, idx = quantise(frames)
            entries.append((dex, anim_id, frames[0].width, frames[0].height, ms, pal, idx))
            print(f"{dex:3d} {anim:9s} {len(frames):3d} frames {frames[0].width}x{frames[0].height} {len(pal)} colours")
    missing = [d for d in DEX if not any(e[0] == d for e in entries)]
    if missing:
        print("WARNING: no idle animation for", missing, "- the device shows a neutral placeholder for them")
    data = build(entries)
    open(dst, "wb").write(data)
    print(f"wrote {dst}: {len(data)} bytes, {len(entries)} animations")


if __name__ == "__main__":
    main()
