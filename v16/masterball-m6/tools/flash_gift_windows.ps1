# Gift content flash helper (Windows PowerShell, esptool from pip). USB-C cable only, no tools inside the ball.
# Run it AFTER the manufacturer's acceptance (FAT). It always backs up the assets partition first.
#
#   Partner pack (+ private message) only, keeps the manufacturer's m6-0.3.0 app:
#     .\flash_gift_windows.ps1 -Port COM5 -PrivateOut C:\...\PokeDock_Private_Assets\out
#   Also install the gift firmware m6-0.4.0-gift (moods, sleep, partner on the alarm screen):
#     .\flash_gift_windows.ps1 -Port COM5 -PrivateOut C:\...\out -GiftFirmware ..\firmware\out\pokedock_m6_gift.bin
#   Back to the neutral placeholder (erase the pack and the message):
#     .\flash_gift_windows.ps1 -Port COM5 -RemoveAssets
#   Back to the manufacturer's firmware (settings in NVS are kept):
#     .\flash_gift_windows.ps1 -Port COM5 -RestoreFirmware <vendor zip>\firmware\pokedock_m6_merged.bin
# Addresses come from firmware/partitions.csv: app 0x10000 (image written at 0x0), assets 0x610000 + 0x9F0000,
# message slot = last 4 KiB of assets = 0xFFF000. NVS (0x9000) is never written by this script.
param(
  [Parameter(Mandatory = $true)][string]$Port,
  [string]$PrivateOut,
  [string]$GiftFirmware,
  [string]$RestoreFirmware,
  [switch]$RemoveAssets
)
$ErrorActionPreference = "Stop"
python -m pip show esptool *> $null
if (-not $?) { python -m pip install --user "esptool>=4.7,<5" pyserial }
function Esp([string[]]$ArgsList) {
  python -m esptool --chip esp32s3 --port $Port --baud 460800 @ArgsList
  if ($LASTEXITCODE -ne 0) { throw "esptool failed: $($ArgsList -join ' ')" }
}

# 1. always keep what is there now (about 1 minute)
$backup = "assets_backup_{0:yyyyMMdd_HHmm}.bin" -f (Get-Date)
Esp @("read_flash", "0x610000", "0x9F0000", $backup)
Write-Host "assets partition backed up to $backup (restore: write_flash 0x610000 $backup)"

if ($RemoveAssets) {
  Esp @("erase_region", "0x610000", "0x9F0000")
  Write-Host "pack and message removed: the ball shows the neutral placeholder again"
}
if ($PrivateOut) {
  $pack = Join-Path $PrivateOut "assets_pack.bin"
  if (-not (Test-Path $pack)) { throw "no $pack (run tools\make_assets.py first)" }
  $files = @("0x610000", $pack)
  $msg = Join-Path $PrivateOut "message_slot.bin"
  if (Test-Path $msg) { $files += @("0xFFF000", $msg) }
  Esp (@("write_flash") + $files)
  Esp (@("verify_flash") + $files)
  Write-Host "partner pack written$(if (Test-Path $msg) { ' with the private message' })"
}
if ($GiftFirmware) {
  Esp @("write_flash", "0x0", $GiftFirmware)
  Esp @("verify_flash", "0x0", $GiftFirmware)
  Write-Host "gift firmware written. Restore the manufacturer's image with -RestoreFirmware if needed."
}
if ($RestoreFirmware) {
  Esp @("write_flash", "0x0", $RestoreFirmware)
  Esp @("verify_flash", "0x0", $RestoreFirmware)
  Write-Host "manufacturer firmware restored"
}
