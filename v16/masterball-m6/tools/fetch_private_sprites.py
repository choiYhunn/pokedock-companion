"""Download the 8 partners' Gen-V animated pixel sprites into a PRIVATE folder for a personal pack.

usage: python tools/fetch_private_sprites.py <private_dir_outside_the_repo> --personal-use

The files are Nintendo / Creatures / GAME FREAK artwork mirrored by the PokeAPI sprites project.
Nobody grants us redistribution rights: this tool only copies them to YOUR PC for a single personal,
non-commercial gift device. It refuses to write inside this repository or any git repository that has a remote, and nothing it writes may
be committed, uploaded, sent to the manufacturer or shared. See docs/GIFT_CONTENT_KO.md.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import urllib.request

DEX = {94: "gengar", 393: "piplup", 468: "togekiss", 448: "lucario", 195: "quagsire", 175: "togepi", 417: "pachirisu", 385: "jirachi"}
URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{}.gif"


def publish_risk(path):
    """None if the folder cannot end up on a remote; otherwise the reason to refuse."""
    def git(*a):
        return subprocess.run(["git", "-C", str(path), *a], capture_output=True, text=True)
    top = git("rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return None
    root = pathlib.Path(top.stdout.strip()).resolve()
    ours = subprocess.run(["git", "-C", str(pathlib.Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    if ours and root == pathlib.Path(ours).resolve():
        return f"{path} is inside the PokéDock repository ({root})"
    if git("remote").stdout.strip():
        return f"{path} is inside {root}, a git repository with a remote (it could be pushed)"
    print(f"note: {path} is inside the local-only repository {root} (no remote). Do not add these files to it.")
    return None


def main():
    if len(sys.argv) < 3 or sys.argv[2] != "--personal-use":
        print(__doc__)
        sys.exit(2)
    out = pathlib.Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    risk = publish_risk(out)
    if risk:
        sys.exit(f"refusing: {risk}. Use a private folder outside any published repository.")
    record = []
    for dex, name in DEX.items():
        target = out / f"{dex}.gif"
        if not target.exists():
            req = urllib.request.Request(URL.format(dex), headers={"User-Agent": "PokeDock-private-gift/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read(2_000_001)
            if not data.startswith((b"GIF87a", b"GIF89a")) or len(data) > 2_000_000:
                sys.exit(f"{dex}: not a GIF")
            target.write_bytes(data)
        data = target.read_bytes()
        record.append({"dex": dex, "name": name, "file": target.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        print(f"{dex:3d} {name:10s} {len(data):6d} B")
    (out / "PRIVATE_DO_NOT_SHARE.txt").write_text(
        "Pokémon sprites (c) Nintendo / Creatures / GAME FREAK, mirrored by PokeAPI. Personal gift use only.\n"
        "Do not commit, upload, send to a manufacturer or share. message.txt here is private too.\n", encoding="utf-8")
    (out / "sources.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(f"saved to {out} (private). Next: python tools/make_assets.py {out} <private_out_dir>")


if __name__ == "__main__":
    main()
