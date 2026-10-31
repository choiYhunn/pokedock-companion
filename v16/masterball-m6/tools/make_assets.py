"""Build the PRIVATE PDK1 sprite pack (and optional private message) for the "assets" partition.

usage: python tools/make_assets.py <private_dir> <out_dir_or_pack.bin>

<private_dir> (outside the repository, e.g. Documents/프로젝트/PokeDock_Private_Assets/src) holds
  <dex>_<anim>.gif   anim = idle, sleep, greet, jump, dance, touch, cheer, celebrate, alarm, egg
  <dex>.gif          used as the idle clip (Gen-V style pixel sprite, <= 128 px)
  message.txt        optional gift message, UTF-8, <= 90 bytes (about 30 Hangul syllables)
Only "idle" is required: the m6-0.4.0-gift firmware animates every mood from the idle frames
(motion + original overlays) and uses a per-mood clip when the pack has one.

Writes assets_pack.bin (flash at 0x610000) and, with message.txt, message_slot.bin (flash at
0xFFF000 = last 4 KiB of the assets partition). See docs/GIFT_CONTENT_KO.md.
Never commit the GIFs, message.txt or the .bin files: the artwork is not ours and the message is private.
"""
import os
import struct
import sys

ANIMS = ["idle", "sleep", "greet", "jump", "dance", "touch", "cheer", "celebrate", "alarm", "egg"]
DEX = [94, 393, 468, 448, 195, 175, 417, 385]
MAX_W = 128
PARTITION_BYTES = 0x9F0000
ASSETS_OFFSET = 0x610000
PDM_SLOT_BYTES, PDM_MAX_BYTES = 4096, 90


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


def message_slot(text):
    data = text.strip().encode("utf-8")
    if not data:
        raise SystemExit("message.txt is empty")
    if len(data) > PDM_MAX_BYTES:
        raise SystemExit(f"message is {len(data)} bytes; the device keeps at most {PDM_MAX_BYTES} (~30 Hangul syllables)")
    if any(c < 0x20 and c != 0x0A for c in data):
        raise SystemExit("message contains control characters")
    return b"PDM1" + struct.pack("<H", len(data)) + data + bytes([0xFF]) * (PDM_SLOT_BYTES - 6 - len(data))


def main():
    src, dst = sys.argv[1:3]
    if dst.lower().endswith(".bin"):
        pack_path = dst
        msg_path = dst[:-4] + "_message.bin"
    else:
        os.makedirs(dst, exist_ok=True)
        pack_path = os.path.join(dst, "assets_pack.bin")
        msg_path = os.path.join(dst, "message_slot.bin")
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
            print(f"{dex:3d} {anim:9s} {len(frames):3d} frames {frames[0].width}x{frames[0].height} {ms:3d} ms {len(pal):3d} colours")
    missing = [d for d in DEX if not any(e[0] == d and e[1] == 0 for e in entries)]
    if missing:
        print("NOTE: no idle clip for", missing, "- the device keeps the neutral placeholder for them")
    data = build(entries)
    with open(pack_path, "wb") as f:
        f.write(data)
    print(f"wrote {pack_path}: {len(data)} bytes ({100 * len(data) / PARTITION_BYTES:.1f} % of the assets partition), "
          f"{len(entries)} clips for {len(DEX) - len(missing)} partners")
    flash = f"write_flash 0x{ASSETS_OFFSET:X} {os.path.basename(pack_path)}"
    msg_file = os.path.join(src, "message.txt")
    if os.path.exists(msg_file):
        with open(msg_file, encoding="utf-8") as f:
            slot = message_slot(f.read())
        with open(msg_path, "wb") as f:
            f.write(slot)
        print(f"wrote {msg_path}: private message slot ({slot[4] | slot[5] << 8} bytes of text)")
        flash += f" 0x{ASSETS_OFFSET + PARTITION_BYTES - PDM_SLOT_BYTES:X} {os.path.basename(msg_path)}"
    print("flash (assets only, the app firmware is untouched):")
    print(f"  python -m esptool --chip esp32s3 -p <PORT> -b 460800 {flash}")


if __name__ == "__main__":
    main()
