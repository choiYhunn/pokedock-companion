#!/usr/bin/env python3
"""Prepare a Capacitor (Android/iOS) project's www/ from mobile-v18 for a PRIVATE device build.

usage: python prepare_native_www.py <capacitor project dir>

- copies the V18 app (not tests/native) into <project>/www, keeping an existing assets/sprites cache
- marks <html data-bundled-sprites="1"> so the app reads assets/sprites/{id}_art.png / _pixel.gif
- downloads the 48 sprite files into www/assets/sprites (private build only; never commit them)
- patches android/app/src/main/AndroidManifest.xml with BLE + notification permissions if present
Pokémon cries are NOT bundled; the native app streams them like the web app.
Rights to Pokémon artwork stay with their owners; this script does not grant redistribution rights.
"""
import hashlib
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
IDS = [94, 393, 468, 448, 195, 175, 417, 385, 25, 133, 54, 143, 37, 39, 196, 197, 258, 280, 447, 492, 570, 700, 702, 778]
ROOT = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/'
PERMS = [
    '<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />',
    '<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />',
    '<uses-permission android:name="android.permission.VIBRATE" />',
    '<uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation" />',
    '<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />',
    '<uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30" />',
    '<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" android:maxSdkVersion="30" />',
    '<uses-feature android:name="android.hardware.bluetooth_le" android:required="false" />',
    # bluetooth-le 7.x declares location without a limit; BLE scans only need it up to Android 11.
    '<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" android:maxSdkVersion="30" />',
    '<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" android:maxSdkVersion="30" />',
]


def valid(data: bytes, ext: str) -> bool:
    if not 64 <= len(data) <= 5_000_000:
        return False
    return data.startswith(b'\x89PNG\r\n\x1a\n') if ext == 'png' else data.startswith((b'GIF87a', b'GIF89a'))


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'PokeDock-private-native-build/1.8'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read(5_000_001)


def main(project: Path) -> int:
    www = project / 'www'
    sprites = www / 'assets' / 'sprites'
    keep = None
    if sprites.exists():
        keep = project / '.sprites_keep'
        shutil.rmtree(keep, ignore_errors=True)
        shutil.copytree(sprites, keep)
    shutil.rmtree(www, ignore_errors=True)
    shutil.copytree(SRC, www, ignore=shutil.ignore_patterns('tests', 'native', '*.md', '__pycache__'))
    if keep:
        shutil.copytree(keep, sprites, dirs_exist_ok=True)
        shutil.rmtree(keep)
    sprites.mkdir(parents=True, exist_ok=True)
    html = www / 'index.html'
    text = html.read_text(encoding='utf-8')
    html.write_text(text.replace('<html lang="ko">', '<html lang="ko" data-bundled-sprites="1">', 1), encoding='utf-8')

    record, failed = [], []
    for i in IDS:
        for kind, parts, ext in (('art', [f'other/official-artwork/{i}.png'], 'png'),
                                 ('pixel', [f'versions/generation-v/black-white/animated/{i}.gif', f'other/showdown/{i}.gif'], 'gif')):
            target = sprites / f'{i}_{kind}.{ext}'
            data = target.read_bytes() if target.exists() else b''
            if not valid(data, ext):
                for part in parts:
                    try:
                        data = fetch(ROOT + part)
                        if valid(data, ext):
                            target.write_bytes(data)
                            break
                    except Exception as exc:  # network or HTTP error: try the fallback URL
                        print('retry', part, exc)
                else:
                    failed.append(target.name)
                    continue
            record.append({'name': target.name, 'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)})
    (sprites / 'manifest.private.json').write_text(json.dumps(record, indent=1), encoding='utf-8')
    print(f'sprites ready: {len(record)}/{len(IDS) * 2}', 'missing: ' + ', '.join(failed) if failed else '')

    manifest = project / 'android' / 'app' / 'src' / 'main' / 'AndroidManifest.xml'
    if manifest.exists():
        s = manifest.read_text(encoding='utf-8')
        for p in PERMS:
            name = re.search(r'android:name="([^"]+)"', p).group(1)
            if name not in s:
                s = s.replace('<application', p + '\n    <application', 1)
        manifest.write_text(s, encoding='utf-8')
        print('AndroidManifest: notification + BLE permissions present')
    else:
        print('no android/ project yet: run `npx cap add android`, then this script again')
    print('next: npm i @capacitor-community/bluetooth-le@^7 && npx cap sync android')
    return 1 if failed else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1]).resolve()))
