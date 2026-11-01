<#
PokeDock M6 gift-content flash tool (Windows PowerShell 5.1+). USB-C cable to the ball's REAR port only.

Every action first: checks the chip (ESP32-S3, 16 MB), takes a FULL 16 MiB backup (plus a separate NVS
copy), checks the partition table against firmware/partitions.csv and identifies the app on the ball.
Writes are app-only at 0x10000 (bootloader 0x0, partition table 0x8000 and settings NVS 0x9000-0xEFFF
are never written), then verified, then NVS / bootloader / table are re-read and must be unchanged.

  -Action Check           read-only: chip, table, which app is installed (normal or rotate180)
  -Action Backup          full 16 MiB backup only
  -Action InstallGift     gift app (0x10000) + pack (0x610000) [+ message slot 0xFFF000]   needs -PrivateOut
  -Action UpdateAssets    pack [+ message slot] only, app unchanged                          needs -PrivateOut
  -Action RemoveAssets    erase the assets partition (pack + message) -> neutral placeholder
  -Action RestoreMfgApp   manufacturing app m6-0.3.0 back at 0x10000 (settings kept)
  -Action RestoreNvs      write a settings backup (exactly 0x6000 B) back to 0x9000         needs -From
  -Action RestoreFull     write a full 16 MiB backup back to 0x0 (everything as it was)     needs -From
  -Action FirstInstall    ONLY for a board that still has the Waveshare factory layout (M7 self-build):
                          merged gift image at 0x0 (bootloader + table + app) [+ pack + slot, else the
                          assets partition is erased]. Refused when the ball already has the PokeDock
                          table (use InstallGift there: it keeps the settings).
  -Rotate180              the ball was built with the 180-degree image (the tool refuses a mismatch)

Example:  .\flash_gift_windows.ps1 -Port COM5 -Action InstallGift -PrivateOut C:\...\PokeDock_Private_Assets\out
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidatePattern('^COM\d+$')][string]$Port,
  [Parameter(Mandatory = $true)]
  [ValidateSet('Check', 'Backup', 'InstallGift', 'UpdateAssets', 'RemoveAssets', 'RestoreMfgApp', 'RestoreNvs', 'RestoreFull', 'FirstInstall')]
  [string]$Action,
  [switch]$Rotate180,
  [string]$PrivateOut,
  [string]$From,
  [string]$BackupDir,
  [switch]$Yes,
  [switch]$AllowUnknownApp,
  [string]$Python = 'python',
  [string[]]$Esptool = @(),   # default: python -m esptool ; the test harness passes a mock
  [string]$OutDir
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2

$Tools = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Tools
if (-not $OutDir) { $OutDir = Join-Path $Root 'firmware\out' }
$Checker = Join-Path $Tools 'gift_image_check.py'
$A = @{ Boot = '0x0'; BootLen = 0x8000; Table = '0x8000'; TableLen = 0xC00; Nvs = '0x9000'; NvsLen = 0x6000
        App = '0x10000'; AppLen = 0x600000; Assets = '0x610000'; AssetsLen = 0x9F0000; Slot = '0xFFF000'; Flash = 0x1000000 }
$suffix = ''
if ($Rotate180) { $suffix = '_rotate180' }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
if (-not $BackupDir) {
  if ($PrivateOut) { $BackupDir = Join-Path (Split-Path -Parent $PrivateOut) 'backups' }
  else { $BackupDir = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'PokeDock_Backups' }
}

function Invoke-Native {
  param([Parameter(Mandatory = $true)][string]$Exe, [Parameter(Mandatory = $true)][string[]]$ArgList)
  # stderr of a native tool must not become a terminating PowerShell error in 5.1
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    $lines = @(& $Exe @ArgList 2>&1 | ForEach-Object { "$_" })
    $code = $LASTEXITCODE
  } finally { $ErrorActionPreference = $prev }
  return @{ Code = $code; Lines = $lines }
}

function Invoke-Esp {
  param([Parameter(Mandatory = $true)][string[]]$EspArgs, [switch]$Reset)
  $after = 'no_reset'
  if ($Reset) { $after = 'hard_reset' }
  $argList = @()
  if ($Esptool.Count -gt 1) { $argList += $Esptool[1..($Esptool.Count - 1)] }
  $argList += @('--chip', 'esp32s3', '--port', $Port, '--baud', '460800', '--before', 'default_reset', '--after', $after)
  $argList += $EspArgs
  Write-Host ('  > esptool ' + ($EspArgs -join ' '))
  $r = Invoke-Native -Exe $Esptool[0] -ArgList $argList
  if ($r.Code -ne 0) {
    $r.Lines | Select-Object -Last 8 | ForEach-Object { Write-Host "    $_" }
    throw "esptool failed (exit $($r.Code)) during: $($EspArgs -join ' ')"
  }
  return $r.Lines
}

function Invoke-Check {
  param([Parameter(Mandatory = $true)][string[]]$CheckArgs)
  $r = Invoke-Native -Exe $Python -ArgList (@('-X', 'utf8', $Checker) + $CheckArgs)
  $text = ($r.Lines -join "`n").Trim()
  if ($r.Code -ne 0) { throw "check refused: $text" }
  return ($text | ConvertFrom-Json)
}

if ($Esptool.Count -eq 0) {
  $Esptool = @($Python, '-m', 'esptool')
  $v = Invoke-Native -Exe $Python -ArgList @('-m', 'esptool', 'version')
  if ($v.Code -ne 0) { throw 'esptool is not installed. Run once:  python -m pip install --user "esptool>=4.7,<5"' }
  if (-not (($v.Lines | Select-Object -Last 1) -match '^4\.')) { throw "esptool $($v.Lines | Select-Object -Last 1) found; this tool uses the 4.x commands: python -m pip install --user `"esptool>=4.7,<5`"" }
}

function Get-Sha([string]$Path) { return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLower() }

function Save-Slice([string]$Src, [long]$Offset, [long]$Length, [string]$Dst) {
  $fs = [System.IO.File]::OpenRead($Src)
  try {
    $buf = New-Object byte[] $Length
    [void]$fs.Seek($Offset, 'Begin')
    $read = 0
    while ($read -lt $Length) {
      $n = $fs.Read($buf, $read, $Length - $read)
      if ($n -le 0) { throw "short read from $Src" }
      $read += $n
    }
    [System.IO.File]::WriteAllBytes($Dst, $buf)
  } finally { $fs.Close() }
}

function Require-File([string]$Path, [string]$What) {
  if (-not $Path -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "$What not found: $Path" }
  return (Resolve-Path -LiteralPath $Path).Path
}

# ---------------------------------------------------------------- 1. local files (nothing touches the ball yet)
$writes = @()   # ordered list of @{ Addr; File; What }
$sums = Join-Path $OutDir 'SHA256SUMS.txt'
switch ($Action) {
  'InstallGift' {
    $app = Require-File (Join-Path $OutDir "pokedock_m6_gift_app$suffix.bin") 'gift app image (run tools\make_app_images.py)'
    [void](Invoke-Check -CheckArgs @('app', $app, '--sums', $sums))
    $writes += @{ Addr = $A.App; File = $app; What = "gift app m6-0.4.0-gift$suffix" }
  }
  'RestoreMfgApp' {
    $app = Require-File (Join-Path $OutDir "pokedock_m6_mfg_app$suffix.bin") 'manufacturing app image (run tools\make_app_images.py)'
    [void](Invoke-Check -CheckArgs @('app', $app, '--sums', $sums))
    $writes += @{ Addr = $A.App; File = $app; What = "manufacturing app m6-0.3.0$suffix" }
  }
  'RestoreNvs' {
    $nvsFile = Require-File $From 'settings backup (-From)'
    [void](Invoke-Check -CheckArgs @('nvs', $nvsFile))
    $writes += @{ Addr = $A.Nvs; File = $nvsFile; What = 'settings (NVS) backup' }
  }
  'RestoreFull' {
    $fullFile = Require-File $From 'full backup (-From)'
    [void](Invoke-Check -CheckArgs @('full', $fullFile))
    $writes += @{ Addr = '0x0'; File = $fullFile; What = 'FULL 16 MiB backup' }
  }
  'FirstInstall' {
    $merged = Require-File (Join-Path $OutDir "pokedock_m6_gift$suffix.bin") 'merged gift image (tools\idf_build_wsl.sh)'
    $mchk = Invoke-Check -CheckArgs @('merged', $merged, '--sums', $sums)
    if ($mchk.app_name -ne "pokedock_m6_gift_app$suffix.bin") {
      throw "the merged image carries $($mchk.app_name), expected pokedock_m6_gift_app$suffix.bin (check -Rotate180)"
    }
    $writes += @{ Addr = '0x0'; File = $merged; What = "gift firmware m6-0.4.0-gift$suffix, merged (bootloader + table + app)" }
  }
}
$eraseAssets = $Action -eq 'RemoveAssets' -or ($Action -eq 'FirstInstall' -and -not $PrivateOut)
if ($Action -eq 'InstallGift' -or $Action -eq 'UpdateAssets' -or ($Action -eq 'FirstInstall' -and $PrivateOut)) {
  if (-not $PrivateOut) { throw "-PrivateOut <folder with assets_pack.bin> is required for $Action" }
  $pack = Require-File (Join-Path $PrivateOut 'assets_pack.bin') 'sprite pack'
  [void](Invoke-Check -CheckArgs @('pack', $pack))
  $writes += @{ Addr = $A.Assets; File = $pack; What = 'private sprite pack' }
  $slotFile = Join-Path $PrivateOut 'message_slot.bin'
  if (Test-Path -LiteralPath $slotFile) {
    [void](Invoke-Check -CheckArgs @('slot', $slotFile))
    $writes += @{ Addr = $A.Slot; File = (Resolve-Path -LiteralPath $slotFile).Path; What = 'private message slot' }
  }
}

# ---------------------------------------------------------------- 2. the ball: chip, full backup, table, app
Write-Host "[1/5] checking the ball on $Port"
$id = Invoke-Esp -EspArgs @('flash_id')
if (-not ($id -match 'ESP32-S3')) { throw 'this port is not an ESP32-S3 (wrong COM port?)' }
if (-not ($id -match 'Detected flash size: 16MB')) { throw 'flash is not 16 MB (not a PokeDock M6 board?)' }

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$full = Join-Path $BackupDir "pokedock_full_$stamp.bin"
Write-Host "[2/5] full backup (16 MiB, about 1-3 minutes): $full"
[void](Invoke-Esp -EspArgs @('read_flash', '0x0', ('0x{0:X}' -f $A.Flash), $full))
if ((Get-Item -LiteralPath $full).Length -ne $A.Flash) { throw 'full backup has the wrong size' }
$tableFile = Join-Path $BackupDir "pokedock_table_$stamp.bin"
$nvsBackup = Join-Path $BackupDir "pokedock_nvs_$stamp.bin"
$bootFile = Join-Path $BackupDir "pokedock_boot_$stamp.bin"
$appHead = Join-Path $BackupDir "pokedock_apphead_$stamp.bin"
Save-Slice $full 0x8000 $A.TableLen $tableFile
Save-Slice $full 0x9000 $A.NvsLen $nvsBackup
Save-Slice $full 0x0 $A.BootLen $bootFile
Save-Slice $full 0x10000 0x1000 $appHead
$sameLayout = $true
$layoutMsg = ''
try { [void](Invoke-Check -CheckArgs @('ptable', $tableFile)) } catch { $sameLayout = $false; $layoutMsg = $_.Exception.Message }
if ($Action -eq 'FirstInstall') {
  if ($sameLayout) { throw 'this ball already has the PokeDock partition table: use -Action InstallGift (it keeps the settings); FirstInstall would erase them' }
  Write-Host '  factory (non-PokeDock) layout found: FirstInstall replaces bootloader, table and app; the backup keeps the factory firmware'
} elseif ($Action -eq 'RestoreFull') {
  if (-not $sameLayout) { Write-Host "  note: $layoutMsg - RestoreFull rewrites it" }
} elseif (-not $sameLayout) {
  throw $layoutMsg
}
$current = Invoke-Check -CheckArgs @('identify', $full, '--sums', $sums)
$manifest = @{ created = $stamp; port = $Port; action = $Action; full = (Split-Path -Leaf $full); full_sha256 = (Get-Sha $full)
               nvs = (Split-Path -Leaf $nvsBackup); nvs_sha256 = (Get-Sha $nvsBackup); app_on_ball = $current.name; app_sha256 = $current.sha256 }
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $BackupDir "pokedock_backup_$stamp.json") -Encoding UTF8
if ($current.name -eq 'broken') { Write-Host "  app on the ball is BROKEN: $($current.reason)"; Write-Host '  -> recommended: -Action RestoreFull -From <the full backup taken BEFORE the failed write>' }
else { Write-Host "  app on the ball: $($current.name) (built $($current.date) $($current.time))" }
Write-Host "  backups (PRIVATE: may contain your message and sprites): $BackupDir"
if ($Action -eq 'Check' -or $Action -eq 'Backup') { Write-Host 'done (read-only).'; return }

# ---------------------------------------------------------------- 3. compatibility and orientation
$touchesApp = $Action -eq 'InstallGift' -or $Action -eq 'RestoreMfgApp'
if ($touchesApp) {
  $known = $current.name -ne 'unknown' -and $current.name -ne 'broken'
  if (-not $known -and -not $AllowUnknownApp) {
    throw "the app on the ball is $($current.name), not one of the listed images; refusing. Prefer -Action RestoreFull; use -AllowUnknownApp only with the right -Rotate180 choice"
  }
  if ($known) {
    $ballRot = $current.name -like '*rotate180*'
    if ($ballRot -ne [bool]$Rotate180) { throw "orientation mismatch: the ball runs $($current.name) but -Rotate180 is $([bool]$Rotate180)" }
    [void](Invoke-Check -CheckArgs @('compat', $appHead, $writes[0].File))
  }
}

# ---------------------------------------------------------------- 4. confirm and write
Write-Host '[3/5] planned writes:'
foreach ($w in $writes) { Write-Host ('  {0,-9} <- {1} ({2})' -f $w.Addr, $w.What, (Split-Path -Leaf $w.File)) }
if ($eraseAssets) { Write-Host ('  erase {0} + 0x{1:X} (pack and message)' -f $A.Assets, $A.AssetsLen) }
if ($Action -eq 'FirstInstall') { Write-Host '  note: settings NVS 0x9000-0xEFFF is reset (a factory board has no PokeDock settings)' }
if ($Action -eq 'UpdateAssets') { Write-Host '  note: without the gift app (m6-0.4.0-gift) moods, sleep, alarm partner and the message are NOT active' }
if (-not $Yes) {
  $answer = Read-Host 'type YES to write'
  if ($answer -ne 'YES') { Write-Host 'cancelled, nothing written.'; return }
}
$pairs = @()
foreach ($w in $writes) { $pairs += @($w.Addr, $w.File) }
Write-Host '[4/5] writing (keep the cable connected)'
try {
  if ($pairs.Count -gt 0) {
    [void](Invoke-Esp -EspArgs (@('write_flash') + $pairs))
    [void](Invoke-Esp -EspArgs (@('verify_flash') + $pairs))
  }
  if ($eraseAssets) {
    [void](Invoke-Esp -EspArgs @('erase_region', $A.Assets, ('0x{0:X}' -f $A.AssetsLen)))
  }
} catch {
  Write-Host ''
  if ($Action -eq 'RestoreFull') {
    Write-Host 'RESTORE DID NOT FINISH. Run the SAME command again with the SAME -From file'
    Write-Host "  (not $full : that copy was read from the ball just before this attempt)."
  } else {
    Write-Host 'WRITE DID NOT FINISH. Nothing is lost: the full backup was taken first.'
    Write-Host "  put everything back as it was:  .\flash_gift_windows.ps1 -Port $Port -Action RestoreFull -From `"$full`""
    if ($Action -eq 'FirstInstall') { Write-Host '  (restore first: the new table may already be written, so FirstInstall would refuse a second time)' }
    elseif ($touchesApp) { Write-Host '  (the same command again will refuse: the half-written app counts as broken)' }
    else { Write-Host '  or run the SAME command again (the app was not touched)' }
  }
  Write-Host '  If the PC no longer finds the port, unplug/replug the cable and try again (the ROM download mode does not need the app).'
  throw
}

# ---------------------------------------------------------------- 5. what must not have changed
Write-Host '[5/5] checking that bootloader, partition table and settings are unchanged'
$afterDir = Join-Path $BackupDir "after_$stamp"
New-Item -ItemType Directory -Force -Path $afterDir | Out-Null
if ($Action -eq 'FirstInstall') {
  $f = Join-Path $afterDir 'table.bin'
  [void](Invoke-Esp -EspArgs @('read_flash', $A.Table, ('0x{0:X}' -f $A.TableLen), $f))
  [void](Invoke-Check -CheckArgs @('ptable', $f))
  Write-Host '  partition table is now the PokeDock layout (next time use InstallGift / UpdateAssets)'
} elseif ($Action -ne 'RestoreFull') {
  $chk = @(@('boot', '0x0', $A.BootLen, $bootFile), @('table', $A.Table, $A.TableLen, $tableFile))
  if ($Action -ne 'RestoreNvs') { $chk += , @('nvs', $A.Nvs, $A.NvsLen, $nvsBackup) }
  foreach ($c in $chk) {
    $f = Join-Path $afterDir "$($c[0]).bin"
    [void](Invoke-Esp -EspArgs @('read_flash', $c[1], ('0x{0:X}' -f $c[2]), $f))
    if ((Get-Sha $f) -ne (Get-Sha $c[3])) { throw "$($c[0]) region CHANGED - restore with -Action RestoreFull -From `"$full`"" }
    Write-Host "  $($c[0]) unchanged"
  }
}
[void](Invoke-Esp -EspArgs @('chip_id') -Reset)
Write-Host "done: $Action. The ball restarts now. Full backup kept at $full"
