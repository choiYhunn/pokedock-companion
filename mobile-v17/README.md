# PokéDock Mobile V17 · responsive NEW mobile app (2026-10-23)
This is a **new layout** rather than a landscape-only copy of the original V10 at /simulator.html.
- Portrait everyday: large clock, current Pokémon, date and greeting, 15/25/45 Focus, daily alarms, custom local love note, 5-tap Gengar Easter egg.
- Landscape game: eight real Pokémon forms, classic BW animated pixel GIF or high-res official-artwork (live PokeAPI images), partner actions hop/dance/peek/celebrate, Nintendo-inspired visual hierarchy. Not arbitrary made-up ghost sprites.
- Saved local state, wall-clock deadline focus, KST alarms checked only while open; NOT guaranteed background/wake alarm.
- Inline /mobile-v17/index.html is a bundled version of the complete source archived in the ChatGPT 2026-10-23 generated artifact ZIP. Separate readable source: `new-app/{index.html,styles.css,core.js,app.js,sw.js}` in the conversation archive. The source ZIP is **not** stored in GitHub; this published HTML is the live built artifact.
- PNG/GIF copyrighted Pokémon graphics **not** redistributed in repo; they load dynamically from PokeAPI GitHub. Verify personal/commercial rights before any public store release.
- Actual APK/IPA NOT compiled. PWA is installable on supported browsers over HTTPS. Neither iOS native notifications nor Android reliable lock-screen alarms implemented.
- Host tests: Node 6/6 core; Chromium set_content 390px portrait layout 390px width, no script errors; full mobile real-device E2E not claimed.
- V16 hologram is a separate physical hardware project; its PC optical geometry tests and firmware skeleton do not constitute live display/OTA signoff. See /v16/revD/VERIFICATION_REPORT.md and /v16/REVC_CRITICAL_AUDIT.md.
