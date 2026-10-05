# Visual Design Review

Open `site/index.html` and review these before more firmware work.

## A. Physical direction
- [ ] White/cream premium appliance is right
- [ ] Screen should be landscape 4.3 inch
- [ ] Qi phone pad on right is right
- [ ] NFC pad on left is right
- [ ] Ambient underglow is desirable
- [ ] Commercial stand is acceptable for V1

## B. UI direction
- [ ] Large clock deserves the main area
- [ ] Pokémon artwork should be larger/smaller
- [ ] Utility cards on the right are useful
- [ ] Bottom navigation is useful
- [ ] UI should be more game-like
- [ ] UI should be more minimal/product-like

## C. Character behavior
Current mapping:
- Togepi → Morning
- Pachirisu → Charging
- Lucario → Focus
- Gengar → Night
- Togekiss → Calm evening
- Jirachi → Birthday

Write replacements/additions below.

## D. Romance level
Current policy: normal home screen contains no couple photo and almost no overt romance.

Choose:
1. **Low** — secret birthday/NFC only
2. **Medium** — occasional one-line personal messages
3. **High** — memories/photos become a core screen

Current recommendation: **Medium-low**.

## E. Next implementation choices
After design approval:
1. Convert product UI into LVGL component map.
2. Add DEX persistence.
3. Add NFC enrollment UI.
4. Add birthday sequence.
5. Add real Dock Node simulator and ESP-NOW packet monitor.