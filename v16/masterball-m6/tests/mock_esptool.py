"""Mock of `python -m esptool` (v4 syntax) backed by a 16 MiB file, for tests/flash_gift_test.ps1.

env: MOCK_FLASH (device image file), MOCK_LOG (JSON lines of argv), MOCK_CHIP (default "ESP32-S3"),
     MOCK_FLASH_MB (16), MOCK_FAIL_WRITE_AFTER (bytes: simulate a cable pull / power cut mid-write).
Like esptool, write_flash erases whole 4 KiB sectors before writing; erase_region needs 4 KiB alignment.
"""
import json
import os
import sys

argv = sys.argv[1:]
with open(os.environ["MOCK_LOG"], "a", encoding="utf8") as log:
    log.write(json.dumps(argv) + "\n")
opts, rest, i = {}, [], 0
while i < len(argv):
    a = argv[i]
    if a in ("--chip", "--port", "-p", "--baud", "-b", "--before", "--after"):
        opts[a] = argv[i + 1]
        i += 2
    else:
        rest.append(a)
        i += 1
if not rest:
    sys.exit("mock: no command")
cmd, args = rest[0], rest[1:]
chip = os.environ.get("MOCK_CHIP", "ESP32-S3")
mb = int(os.environ.get("MOCK_FLASH_MB", "16"))
img = os.environ["MOCK_FLASH"]
print(f"esptool.py v4.8.1 (mock)\nSerial port {opts.get('--port')}\nConnecting....\nChip is {chip} (QFN56) (revision v0.2)")
if opts.get("--chip") != "esp32s3" or chip != "ESP32-S3":
    print("A fatal error occurred: This chip is " + chip + ", not ESP32-S3. Wrong --chip argument?")
    sys.exit(2)
num = lambda s: int(s, 0)  # noqa: E731
with open(img, "r+b") as f:
    if cmd in ("flash_id", "chip_id"):
        print(f"Detected flash size: {mb}MB")
    elif cmd == "read_flash":
        off, size, out = num(args[0]), num(args[1]), args[2]
        f.seek(off)
        open(out, "wb").write(f.read(size))
        print(f"Read {size} bytes at {hex(off)}")
    elif cmd in ("write_flash", "verify_flash"):
        pairs = [(num(args[k]), args[k + 1]) for k in range(0, len(args), 2)]
        budget = int(os.environ.get("MOCK_FAIL_WRITE_AFTER", "-1"))
        for off, path in pairs:
            data = open(path, "rb").read()
            if cmd == "verify_flash":
                f.seek(off)
                if f.read(len(data)) != data:
                    print(f"A fatal error occurred: Verification failed at {hex(off)}")
                    sys.exit(2)
                print(f"-- verify OK {hex(off)}")
                continue
            if off % 4096:
                sys.exit("mock: unaligned write")
            f.seek(off)
            f.write(b"\xff" * (((len(data) + 4095) // 4096) * 4096))  # sector erase
            if budget >= 0 and len(data) > budget:
                f.seek(off)
                f.write(data[:budget])
                print("A fatal error occurred: Serial data stream stopped: Possible serial noise or corruption.")
                sys.exit(2)
            f.seek(off)
            f.write(data)
            budget = budget - len(data) if budget >= 0 else budget
            print(f"Wrote {len(data)} bytes at {hex(off)}")
    elif cmd == "erase_region":
        off, size = num(args[0]), num(args[1])
        if off % 4096 or size % 4096:
            sys.exit("mock: unaligned erase")
        f.seek(off)
        f.write(b"\xff" * size)
        print(f"Erased {hex(size)} at {hex(off)}")
    else:
        sys.exit(f"mock: unknown command {cmd}")
