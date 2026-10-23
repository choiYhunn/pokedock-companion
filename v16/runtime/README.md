# V16 portable hologram compositor

This is genuine executable C++17 integration code for the 600×450 RGB565 render pipeline, **not native Waveshare V2 firmware**.

Given a decompressed (or preloaded) GHF1 animation frame from microSD, `compose_frame` calls the validated RGB565+alpha decoder, clears the optical background to real black, draws only opaque character pixels and optionally flips X for the 45° beamsplitter. Size checks, clipping, x1–x3 pixel nearest-neighbour scaling and per-frame animation timing are implemented.

Run `bash test_host.sh`. The GitHub build uses the existing canonical `../firmware/ghf_decoder.h` directly; the conversation ZIP includes a test-only portable decoder copy. To flash, still need: Waveshare V2 RM690B0 official driver init, FATFS/microSD read/stream, PSRAM allocation, QSPI `flush`, optional front SSD1309 clock renderer and verified signed manual OTA. Do not treat the host benchmark as hardware playback speed.

Scratch memory for 256×256: RGB565 128KiB + alpha 64KiB. Full AMOLED 600×450 RGB565 527.3KiB. Together ~719KiB, within nominal 8MiB PSRAM, but real heap fragmentation and DMA constraints need measurement on board. Overlay area fits 600×450 only after framing, 2D virtual sprite ≠ free-space 3D hologram.
