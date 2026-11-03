"""Checks that sound_manifest.json, the firmware cue table and the partner list agree.

usage: python check_sound_manifest.py
  firmware:  v16/masterball-m6/core/audio_director.hpp   kCueTracks {track, priority, max_ms, loop}
  partners:  v16/masterball-m6/core/pokedock_core.hpp    kPokemonIds (cry track = 9 + index)
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
CORE = HERE.parent.parent / "masterball-m6" / "core"
man = json.loads((HERE / "sound_manifest.json").read_text(encoding="utf8"))
hpp = (CORE / "audio_director.hpp").read_text(encoding="utf8")
core = (CORE / "pokedock_core.hpp").read_text(encoding="utf8")
fails, n = [], 0


def check(name, cond, detail=""):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        fails.append(name)


body = re.search(r"kCueTracks\{\{(.*?)\}\};", hpp, re.S).group(1)
rows = [(int(a), int(b), int(c), d == "true", e) for a, b, c, d, e in
        re.findall(r"\{(\d+),\s*(\d+),\s*(\d+),\s*(true|false)\},\s*//\s*(k\w+)", body)]
enum = re.search(r"enum class Cue : uint8_t \{([^}]*)\}", hpp).group(1).replace(" ", "").split(",")
ids = [int(x) for x in re.search(r"kPokemonIds\{\{([^}]*)\}\}", core).group(1).split(",")]
check("cue table has one row per Cue (kCount excluded)", len(rows) == len(enum) - 1, (len(rows), enum))
check("cue rows in enum order", [r[4] for r in rows] == enum[:-1], [r[4] for r in rows])
tracks = man["tracks"]
check("manifest has 8 cues + one cry per partner", len(tracks) == 8 + len(ids), len(tracks))
check("tracks numbered 1..N without gaps", [t["track"] for t in tracks] == list(range(1, len(tracks) + 1)))
names = {"kBoot": "boot", "kLidOpen": "lid_open", "kLidClose": "lid_close", "kTap": "tap", "kConfirm": "confirm",
         "kPair": "pair", "kTimerDone": "timer_done", "kAlarm": "alarm", "kCry": "cry"}
for track, _prio, max_ms, loop, cue in rows:
    t = tracks[track - 1]
    check(f"{cue}: track {track} = '{names[cue]}', max {max_ms} ms, loop {loop}",
          t["cue"] == names[cue] and t["max_ms"] == max_ms and bool(t.get("loop", False)) == loop, t)
cry0 = [r for r in rows if r[4] == "kCry"][0][0]
cries = [t for t in tracks if t["cue"] == "cry"]
check("cry tracks follow kPokemonIds order", [t["partner"] for t in cries] == ids and cries[0]["track"] == cry0,
      ([t["partner"] for t in cries], ids))
check("firmware kCryTracks = number of partners", f"kCryTracks = {len(ids)};" in hpp)
print(f"{'FAIL' if fails else 'PASS'}: {n - len(fails)}/{n} sound manifest checks")
sys.exit(1 if fails else 0)
