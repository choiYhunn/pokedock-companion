"""Public TEST pack: original geometric stand-ins (no Pokémon art) with the real partner frame sizes,
so the whole placeholder -> character pipeline can be tested in public CI-free runs.

usage: python tests/make_test_pack.py <out_dir>
Writes <out_dir>/test_pack.bin (+ test_message_slot.bin). The shapes are a rounded blob with two
dots and the letters T/E/S/T are NOT drawn; colours are neutral so nobody mistakes it for a partner.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
import make_assets as M  # noqa: E402

# Gen-V canvas sizes of the 8 partners (w, h) - only the size is borrowed, not any pixels.
SIZES = {94: (74, 63), 393: (30, 41), 468: (86, 52), 448: (47, 63), 195: (67, 58), 175: (40, 38), 417: (53, 55), 385: (55, 47)}
PAL = [(0, 0, 0, 0), (150, 160, 175, 255), (95, 105, 120, 255), (40, 44, 52, 255), (235, 238, 242, 255)]


def blob_frames(w, h, n):
    frames = []
    for k in range(n):
        squash = [0, 1, 2, 1][k % 4]
        cx, cy = w / 2, h / 2 + squash
        rx, ry = w * 0.42, h * 0.40 - squash
        f = []
        for y in range(h):
            for x in range(w):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d > 1:
                    f.append(0)
                elif d > 0.8:
                    f.append(2)  # outline
                elif abs(y - (cy - ry * 0.2)) < max(1.5, h * 0.05) and (abs(x - (cx - rx * 0.35)) < max(1.5, w * 0.05) or abs(x - (cx + rx * 0.35)) < max(1.5, w * 0.05)):
                    f.append(3)  # two dot eyes
                elif y < cy - ry * 0.45:
                    f.append(4)  # highlight
                else:
                    f.append(1)
        frames.append(f)
    return frames


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    for dex, (w, h) in SIZES.items():
        entries.append((dex, 0, w, h, 120, PAL, blob_frames(w, h, 4)))  # idle only, like real Gen-V sprites
    entries.append((94, 1, 74, 63, 200, PAL, blob_frames(74, 63, 2)))  # one per-mood clip (sleep) to test overrides
    data = M.build(entries)
    (out / "test_pack.bin").write_bytes(data)
    (out / "test_message_slot.bin").write_bytes(M.message_slot("테스트 메시지 (공개 저장소용)"))
    print(f"test pack {len(data)} bytes, {len(entries)} clips")


if __name__ == "__main__":
    main()
