<#
  Copies a PokeDock sound pack onto the DFRobot DFR0534 (its 8 MB flash appears as a USB drive when
  the module's own micro-USB is plugged into the PC). Windows PowerShell 5.1.

  The module numbers tracks in COPY ORDER, so files go one at a time in 01..16 order onto a drive
  that holds no other audio. Safety: refuses any drive that is not removable or is larger than 16 MB
  (a normal USB stick is never touched); deletes old files only with -ClearDrive and a typed "yes".

  .\copy_sounds_windows.ps1 -Drive E: -Pack ..\build\audio_test_pack                 # TEST tones
  .\copy_sounds_windows.ps1 -Drive E: -Pack "$env:USERPROFILE\Documents\프로젝트\PokeDock_Private_Assets\audio\out" -ClearDrive
#>
param(
  [Parameter(Mandatory = $true)][string]$Drive,
  [Parameter(Mandatory = $true)][string]$Pack,
  [switch]$ClearDrive,
  [switch]$Yes,
  [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'
$Drive = $Drive.TrimEnd('\').ToUpper()
if ($Drive -notmatch '^[A-Z]:$') { throw "Drive must look like E:" }

$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='$Drive'"
if ($null -eq $disk) { throw "Drive $Drive not found. Plug the DFR0534 micro-USB into the PC first." }
if ($disk.DriveType -ne 2) { throw "Drive $Drive is not removable (type $($disk.DriveType)): refusing." }
if ([int64]$disk.Size -gt 16MB) { throw "Drive $Drive is $([math]::Round($disk.Size / 1MB)) MB: the DFR0534 has 8 MB. Refusing (wrong drive?)." }

$files = @(Get-ChildItem -LiteralPath $Pack -File | Where-Object { $_.Name -match '^\d\d_.+\.(wav|mp3)$' } | Sort-Object Name)
if ($files.Count -ne 16) { throw "Pack $Pack has $($files.Count) files named NN_*.wav|mp3; expected 16 (sound_manifest.json)." }
for ($i = 0; $i -lt 16; $i++) {
  $want = '{0:D2}_' -f ($i + 1)
  if (-not $files[$i].Name.StartsWith($want)) { throw "Track $($i + 1) missing: expected a file starting with $want" }
}
$bytes = ($files | Measure-Object Length -Sum).Sum
if ($bytes -gt [int64]$disk.FreeSpace -and -not $ClearDrive) { throw "Pack is $bytes bytes, free space $($disk.FreeSpace)." }

$old = @(Get-ChildItem -LiteralPath "$Drive\" -Recurse -File -Force -ErrorAction SilentlyContinue |
         Where-Object { $_.Name -notmatch '^(System Volume Information|desktop\.ini)$' -and $_.FullName -notmatch 'System Volume Information' })
if ($old.Count -gt 0) {
  Write-Host "Drive $Drive already holds $($old.Count) file(s):"
  $old | ForEach-Object { Write-Host "  $($_.FullName)" }
  if (-not $ClearDrive) { throw "Track numbers would shift. Run again with -ClearDrive to delete them first." }
  if (-not $Yes) {
    $a = Read-Host "Delete these files on $Drive (the DFR0534)? Type yes"
    if ($a -ne 'yes') { throw "Cancelled." }
  }
  if (-not $WhatIf) { $old | Remove-Item -Force }
}

foreach ($f in $files) {
  Write-Host ("copy {0,-24} {1,8} bytes" -f $f.Name, $f.Length)
  if (-not $WhatIf) {
    Copy-Item -LiteralPath $f.FullName -Destination "$Drive\$($f.Name)"
    Start-Sleep -Milliseconds 200   # one directory entry at a time = the module's track order
  }
}
if ($WhatIf) { Write-Host "WhatIf: nothing written."; exit 0 }

# FAT directory order (dir without a sort switch) must equal 01..16
$order = @(cmd /c "dir /b $Drive\" | Where-Object { $_ -match '^\d\d_' })
$expect = @($files | ForEach-Object { $_.Name })
if (($order -join '|') -ne ($expect -join '|')) {
  Write-Host "Directory order on the drive:"; $order | ForEach-Object { Write-Host "  $_" }
  throw "Order on the drive differs from 01..16: run again with -ClearDrive."
}
Write-Host "PASS: 16 tracks copied in order ($bytes bytes). Eject the drive, unplug the module's micro-USB."
Write-Host "Check on the ball: power on (track 1), open the lid (2, then the partner cry), BLE audio_test 0..8."
