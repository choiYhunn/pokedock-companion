# PokéDock Mobile — EXACT original UI V10 source (not redesigned)
**This version copies the entire original** root /simulator.html (68,036 bytes) into mobile/index.html, preserving original functional subviews, partner selection, existing Pokémon art URLs, game/quest logic, original alarm settings, Easter eggs and secret home drawer. Only route paths, standalone PWA shell, landscape-phone layout and foreground alarm persistence are changed.

## Proof against the repo (2026-10-23)
- Original source: [simulator.html](../simulator.html)
- Original animations: [ui/party-game.js](../ui/party-game.js) and [ui/party-game.css](../ui/party-game.css).
- V9/10 party roster: Gengar 94, Piplup 393, Togekiss 468, Lucario 448, Quagsire 195, Togepi 175, Pachirisu 417, Jirachi 385.
- Easter eggs preserved: five taps on Gengar or pet opens Our Space. Birthday demo, love note, anniversary and egg hatching all remain.
- Alarm UI offers 07:30 weekdays, 08:10 Tuesday/Thursday and 22:20 night prep. This mobile version saves toggles locally and triggers a visible/vibrating foreground notification when running, never an OS-level guaranteed wake-up.
- The full original panel uses 800×480. Android PWA requests landscape mode; iOS requires physically rotating the phone. Portrait screen shows a rotation instruction rather than a tiny illegible 800×480 UI.

## Install
Publish repo main root through GitHub Pages (Settings -> Pages -> deploy from main/(root)), then https://choiyhunn.github.io/pokedock-companion/mobile/.
iPhone: Safari -> Share -> Add to Home Screen -> Open as Web App -> Add.
Android: Chrome -> menu -> Install App or Add to Home Screen.
**GitHub Pages isn't verified active yet**; source being committed does not prove live deploy.
Network is required for PokeAPI Pokémon artwork/GIF. Offline SW caches same-origin UI shell and party game code only. Test external images after airplane mode before promising full offline.
PWA !== a signed Android APK or App Store iOS app. No OS background alarm guarantees.

## Native packaging (optional follow-on)
Capacitor Android/iOS wrapper config and a source bundle builder are included. Android APK requires Android Studio SDK and installed dependencies; iOS IPA/TestFlight requires macOS Xcode, signing and Apple distribution. This session did not have Android SDK/Xcode, so no actual APK/IPA was compiled.
