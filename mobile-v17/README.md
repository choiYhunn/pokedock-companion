# PokéDock Mobile V17.1 · GitHub Pages

Open `https://choiyhunn.github.io/pokedock-companion/mobile-v17/` in iPhone Safari. Wait for **오프라인 준비 완료**, then use Share → Add to Home Screen → Open as Web App → Add. Open the Home Screen icon once while online before testing airplane mode.

## Included

- Portrait companion: clock, Focus 15/25/45 minutes, local note and partner selection.
- Landscape play: eight partners, integer scaled pixel sprites, four motions, and a five round silhouette quiz.
- Up to eight editable alarms with weekday, time, title and three original PokéDock chiptune sounds.
- Browser state is stored on each device. There is no account, cross-device sync, hardware connection or private message delivery.

## Offline and alarm limits

The Pages repository contains no Pokémon PNG/GIF files. On the first online visit the app downloads 16 images from PokeAPI's GitHub sprite repository and caches them on that device. The app shell, original sounds and icons are also cached. The **오프라인 준비 완료** badge reports when those 16 images are cached. Safari can later evict website storage; revisit the URL online if that happens. The first visit and updates require internet, but the user's Windows notebook does not need to stay on because GitHub Pages hosts the site.

Web alarms are checked only while the page is open. iOS may restrict audio playback, and a closed or locked iPhone will not run this JavaScript as a dependable wake alarm. The Android debug APK prepared privately uses native local notifications; it is not distributed in this public repository. A native iOS app still needs Xcode and Apple signing for lock screen local notifications.

Pokémon artwork belongs to its rights holders. Referencing PokeAPI images here does not grant redistribution or commercial rights. The three included WAV melodies are original PokéDock tones.

## Verification

- Local Chromium test: after first online cache completion, network disabled, all 16 remote images and 3 local sounds loaded, silhouette quiz opened, zero page errors.
- iPhone Safari installation, cache retention and alarm timing remain to be tested on a physical phone.
- The V16/V18 physical Master Ball is a separate prototype, not connected to this web app.
