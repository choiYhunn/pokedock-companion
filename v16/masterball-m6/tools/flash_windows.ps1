# Flash helper for Windows PowerShell (esptool from pip). Nothing is erased unless asked.
#   Backup the factory image first (16 MB, ~3 min):  .\flash_windows.ps1 -Port COM5 -Backup
#   Official Waveshare factory demo:                 .\flash_windows.ps1 -Port COM5 -Image <...>\Firmware\ESP32-S3-Touch-AMOLED-1.43-factory.bin
#   M6 firmware (from idf_build_wsl.sh):             .\flash_windows.ps1 -Port COM5 -Image ..\firmware\out\pokedock_m6_merged.bin
#   Serial log for G1 (Ctrl+C to stop):              .\flash_windows.ps1 -Port COM5 -Monitor
param(
  [Parameter(Mandatory = $true)][string]$Port,
  [string]$Image,
  [switch]$Backup,
  [switch]$Monitor
)
python -m pip show esptool *> $null
if (-not $?) { python -m pip install --user "esptool>=4.7,<5" pyserial }
if ($Backup) {
  $name = "factory_backup_{0:yyyyMMdd_HHmm}.bin" -f (Get-Date)
  python -m esptool --chip esp32s3 --port $Port --baud 921600 read_flash 0 0x1000000 $name
  Get-FileHash $name -Algorithm SHA256
}
if ($Image) {
  python -m esptool --chip esp32s3 --port $Port --baud 921600 write_flash 0x0 $Image
}
if ($Monitor) {
  python -m serial.tools.miniterm $Port 115200 --raw
}
