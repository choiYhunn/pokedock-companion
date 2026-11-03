# Windows PowerShell 5.1 test of tools/flash_gift_windows.ps1 against tests/mock_esptool.py (no real ball).
# Run: powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests\flash_gift_test.ps1
# Checks the exact esptool argument lists, addresses, refusals before any write, NVS/bootloader/table
# preservation, orientation guard, a simulated cable pull mid-write and every restore path.
$ErrorActionPreference = 'Stop'
$Tests = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $Tests
$Tool = Join-Path $Root 'tools\flash_gift_windows.ps1'
$Check = Join-Path $Root 'tools\gift_image_check.py'
$Util = Join-Path $Tests 'flash_test_util.py'
$Mock = Join-Path $Tests 'mock_esptool.py'
$W = Join-Path $env:TEMP ('pd_flash_test_' + [guid]::NewGuid().ToString('N').Substring(0, 8))
$Out = Join-Path $W 'out'; $Priv = Join-Path $W 'priv'; $Bk = Join-Path $W 'bk'
New-Item -ItemType Directory -Force -Path $Out, $Priv, $Bk | Out-Null
$results = New-Object System.Collections.ArrayList
function Py([string[]]$a) { $r = & python -X utf8 @a; if ($LASTEXITCODE -ne 0) { throw "python failed: $($a -join ' ')" }; return $r }
function Ok([string]$name, [bool]$cond, [string]$detail = '') {
  [void]$results.Add([pscustomobject]@{ Name = $name; Pass = $cond; Detail = $detail })
  if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name $detail" }
}
Write-Host "PowerShell $($PSVersionTable.PSVersion) ($($PSVersionTable.PSEdition))"

# ---- synthetic images (real formats, made by the same checker the tool uses)
foreach ($n in @('mfg', 'mfg_rot', 'gift', 'gift_rot', 'other')) { Py @($Check, 'make-test-app', (Join-Path $W "$n.bin"), $n) | Out-Null }
Py @($Check, 'make-test-app', (Join-Path $W 'factory.bin'), 'demo', 'waveshare_demo') | Out-Null   # foreign factory app
Copy-Item (Join-Path $W 'mfg.bin') (Join-Path $Out 'pokedock_m6_mfg_app.bin')
Copy-Item (Join-Path $W 'mfg_rot.bin') (Join-Path $Out 'pokedock_m6_mfg_app_rotate180.bin')
Copy-Item (Join-Path $W 'gift.bin') (Join-Path $Out 'pokedock_m6_gift_app.bin')
Copy-Item (Join-Path $W 'gift_rot.bin') (Join-Path $Out 'pokedock_m6_gift_app_rotate180.bin')
$lines = foreach ($f in Get-ChildItem $Out -Filter '*.bin') { '{0}  {1}' -f (Get-FileHash -Algorithm SHA256 $f.FullName).Hash.ToLower(), $f.Name }
Set-Content -Path (Join-Path $Out 'SHA256SUMS.txt') -Value $lines -Encoding ASCII
Py @($Check, 'make-merged', (Join-Path $Out 'pokedock_m6_gift.bin'), (Join-Path $Out 'pokedock_m6_gift_app.bin')) | Out-Null
Py @($Check, 'make-merged', (Join-Path $Out 'pokedock_m6_gift_rotate180.bin'), (Join-Path $Out 'pokedock_m6_gift_app_rotate180.bin')) | Out-Null
Py @((Join-Path $Tests 'make_test_pack.py'), $Priv) | Out-Null
Move-Item (Join-Path $Priv 'test_pack.bin') (Join-Path $Priv 'assets_pack.bin')
Move-Item (Join-Path $Priv 'test_message_slot.bin') (Join-Path $Priv 'message_slot.bin')
$Dev = Join-Path $W 'device.bin'; $Log = Join-Path $W 'esptool.log'
$env:MOCK_FLASH = $Dev; $env:MOCK_LOG = $Log

function New-Ball([string]$app, [string]$layout = '') {
  $a = @($Util, 'make-device', $Dev, (Join-Path $W "$app.bin"))
  if ($layout) { $a += $layout }
  Py $a | Out-Null
  if (Test-Path $Log) { Remove-Item $Log }
  Remove-Item Env:\MOCK_CHIP, Env:\MOCK_FAIL_WRITE_AFTER -ErrorAction SilentlyContinue
}
function Run-Tool([hashtable]$p) {
  $base = @{ Port = 'COM9'; OutDir = $Out; BackupDir = $Bk; Esptool = @('python', $Mock); Yes = $true }
  foreach ($k in $p.Keys) { $base[$k] = $p[$k] }
  try { & $Tool @base *> $null; return 'ok' } catch { return "error: $($_.Exception.Message)" }
}
# same, but also returns what the tool printed (for the recovery instructions)
function Run-ToolText([hashtable]$p) {
  $base = @{ Port = 'COM9'; OutDir = $Out; BackupDir = $Bk; Esptool = @('python', $Mock); Yes = $true }
  foreach ($k in $p.Keys) { $base[$k] = $p[$k] }
  $buf = New-Object System.Collections.Generic.List[string]   # filled line by line, so it survives a throw
  try { & $Tool @base *>&1 | ForEach-Object { $buf.Add("$_") }; return @{ R = 'ok'; Text = ($buf -join "`n") } }
  catch { return @{ R = "error: $($_.Exception.Message)"; Text = ($buf -join "`n") } }
}
# each command is one string 'cmd|arg1|arg2...' so a missing split or a merged argument shows up exactly
function Cmds { if (Test-Path $Log) { return @(Py @($Util, 'cmds', $Log)) } else { return @() } }
function Writes { return @(Cmds | Where-Object { $_ -like 'write_flash|*' -or $_ -like 'erase_region|*' }) }
function Sha([string]$off, [string]$len) { return (Py @($Util, 'sha', $Dev, $off, $len)) }
function Same([string]$off, [string]$file) { return (Py @($Util, 'same', $Dev, $off, $file)) -eq 'OK' }
function Latest([string]$pattern) { return (Get-ChildItem $Bk -Filter $pattern | Sort-Object LastWriteTime | Select-Object -Last 1).FullName }

# 1. read-only check
New-Ball 'mfg'
$r = Run-Tool @{ Action = 'Check' }
Ok 'Check: succeeds' ($r -eq 'ok') $r
Ok 'Check: never writes' ((Writes).Count -eq 0)
Ok 'Check: 16 MiB full backup' ((Get-Item (Latest 'pokedock_full_*.bin')).Length -eq 16MB)
Ok 'Check: separate 0x6000 NVS copy' ((Get-Item (Latest 'pokedock_nvs_*.bin')).Length -eq 0x6000)

# 2. install gift: exact argv, addresses, untouched regions
New-Ball 'mfg'
$nvs0 = Sha '0x9000' '0x6000'; $boot0 = Sha '0x0' '0x8000'; $tab0 = Sha '0x8000' '0xC00'; $phy0 = Sha '0xF000' '0x1000'
$r = Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv }
Ok 'InstallGift: succeeds' ($r -eq 'ok') $r
$wr = @(Writes)
Ok 'InstallGift: exactly one write_flash' ($wr.Count -eq 1) ($wr -join ' || ')
$expect = @('write_flash', '0x10000', (Join-Path $Out 'pokedock_m6_gift_app.bin'), '0x610000', (Join-Path $Priv 'assets_pack.bin'), '0xFFF000', (Join-Path $Priv 'message_slot.bin'))
Ok 'InstallGift: argv passed element by element (PS 5.1)' ($wr[0] -eq ($expect -join '|')) $wr[0]
$first = (@(Cmds) | Select-Object -First 2 | ForEach-Object { ($_ -split '\|')[0] }) -join ','
Ok 'InstallGift: chip check and full backup come first' ($first -eq 'flash_id,read_flash') $first
Ok 'InstallGift: app at 0x10000' (Same '0x10000' (Join-Path $Out 'pokedock_m6_gift_app.bin'))
Ok 'InstallGift: pack at 0x610000' (Same '0x610000' (Join-Path $Priv 'assets_pack.bin'))
Ok 'InstallGift: message slot at 0xFFF000' (Same '0xFFF000' (Join-Path $Priv 'message_slot.bin'))
Ok 'InstallGift: settings NVS 0x9000-0xEFFF unchanged' ((Sha '0x9000' '0x6000') -eq $nvs0)
Ok 'InstallGift: bootloader, table, phy unchanged' (((Sha '0x0' '0x8000') -eq $boot0) -and ((Sha '0x8000' '0xC00') -eq $tab0) -and ((Sha '0xF000' '0x1000') -eq $phy0))
Ok 'InstallGift: verify_flash after write' (@(Cmds | Where-Object { $_ -like 'verify_flash|*' }).Count -eq 1)
$ArgvDump = Join-Path $Root 'build'; New-Item -ItemType Directory -Force -Path $ArgvDump | Out-Null
Copy-Item $Log (Join-Path $ArgvDump 'flash_argv_installgift.log') -Force   # replayed against the real esptool
Ok 'InstallGift: nothing below 0x10000 is written' (@($wr | Where-Object { [Convert]::ToInt64((($_ -split '\|')[1]).Substring(2), 16) -lt 0x10000 }).Count -eq 0)

# 3. orientation guard
New-Ball 'gift'
$r = Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv; Rotate180 = $true }
Ok 'Rotate180 on a normal ball: refused before writing' (($r -like '*orientation mismatch*') -and (Writes).Count -eq 0) $r
New-Ball 'mfg_rot'
$r = Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv; Rotate180 = $true }
Ok 'Rotate180 ball + -Rotate180: rotate180 gift app written' (($r -eq 'ok') -and (Same '0x10000' (Join-Path $Out 'pokedock_m6_gift_app_rotate180.bin'))) $r

# 4. wrong files: refused before any write
$cases = @(
  @{ Name = 'merged image given as app'; Prep = { Copy-Item (Join-Path $W 'merged_like.bin') (Join-Path $Out 'pokedock_m6_gift_app.bin') -Force }; Expect = '*MERGED*' },
  @{ Name = 'app changed after SHA256SUMS'; Prep = { Py @($Util, 'poke', (Join-Path $Out 'pokedock_m6_gift_app.bin'), '0x500', 'deadbeef') | Out-Null }; Expect = '*refused*' },
  @{ Name = 'sprite pack is really an app'; Prep = { Copy-Item (Join-Path $W 'gift.bin') (Join-Path $Priv 'assets_pack.bin') -Force }; Expect = '*PDK1*' },
  @{ Name = 'message slot wrong size'; Prep = { Set-Content -Path (Join-Path $Priv 'message_slot.bin') -Value 'PDM1' -Encoding ASCII }; Expect = '*PDM1*' }
)
[IO.File]::WriteAllBytes((Join-Path $W 'merged_like.bin'), [IO.File]::ReadAllBytes($Dev)[0..0x9FFF])
foreach ($c in $cases) {
  New-Ball 'mfg'
  Copy-Item (Join-Path $W 'gift.bin') (Join-Path $Out 'pokedock_m6_gift_app.bin') -Force
  Py @((Join-Path $Tests 'make_test_pack.py'), $Priv) | Out-Null
  Move-Item (Join-Path $Priv 'test_pack.bin') (Join-Path $Priv 'assets_pack.bin') -Force
  Move-Item (Join-Path $Priv 'test_message_slot.bin') (Join-Path $Priv 'message_slot.bin') -Force
  & $c.Prep
  $r = Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv }
  Ok "wrong file ($($c.Name)): refused, nothing sent to the ball" (($r -like $c.Expect) -and ((Cmds).Count -eq 0)) $r
}
Copy-Item (Join-Path $W 'gift.bin') (Join-Path $Out 'pokedock_m6_gift_app.bin') -Force
Py @((Join-Path $Tests 'make_test_pack.py'), $Priv) | Out-Null
Move-Item (Join-Path $Priv 'test_pack.bin') (Join-Path $Priv 'assets_pack.bin') -Force
Move-Item (Join-Path $Priv 'test_message_slot.bin') (Join-Path $Priv 'message_slot.bin') -Force

# 5. wrong device / wrong port
New-Ball 'mfg'; $env:MOCK_CHIP = 'ESP32'
$r = Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv }
Ok 'wrong chip: refused, nothing written' (($r -like 'error*') -and (Writes).Count -eq 0) $r
New-Ball 'mfg'; Py @($Util, 'poke', $Dev, '0x8046', '02') | Out-Null   # factory offset 0x10000 -> 0x20000
$r = Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv }
Ok 'different partition table on the ball: refused' (($r -like '*partition table*') -and (Writes).Count -eq 0) $r
New-Ball 'other'
$r = Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv }
Ok 'unknown app on the ball: refused' (($r -like '*not one of the listed images*') -and (Writes).Count -eq 0) $r

# 6. cable pulled mid-write -> RestoreFull brings back the exact original flash
New-Ball 'mfg'
$orig = Sha '0x0' '0x1000000'
$env:MOCK_FAIL_WRITE_AFTER = '2000'   # the synthetic app is ~3 KB: the cable 'drops' inside it
$t = Run-ToolText @{ Action = 'InstallGift'; PrivateOut = $Priv }
Remove-Item Env:\MOCK_FAIL_WRITE_AFTER
$r = $t.R
Ok 'power cut mid-write: tool stops with an error' ($r -like 'error*') $r
Ok 'power cut mid-write: app slot is now broken (as on a real ball)' ((Sha '0x0' '0x1000000') -ne $orig)
Ok 'power cut mid-write: settings were not touched' (Same '0x9000' (Latest 'pokedock_nvs_*.bin'))
$full = (Get-ChildItem $Bk -Filter 'pokedock_full_*.bin' | Sort-Object LastWriteTime | Select-Object -Last 1).FullName  # taken BEFORE the failed write
Ok 'power cut mid-write: prints RestoreFull with that pre-write backup' ($t.Text -like "*-Action RestoreFull -From `"$full`"*") $t.Text
$r = Run-Tool @{ Action = 'RestoreMfgApp' }
Ok 'broken app: RestoreMfgApp refused without -AllowUnknownApp' (($r -like '*broken*') -and (Writes).Count -eq 1) $r
$r = Run-Tool @{ Action = 'RestoreFull'; From = $full }
Ok 'RestoreFull: whole 16 MiB identical to before' (($r -eq 'ok') -and ((Sha '0x0' '0x1000000') -eq $orig)) $r

# 7. remove assets / restore manufacturing app / restore settings / assets only
New-Ball 'mfg'
[void](Run-Tool @{ Action = 'InstallGift'; PrivateOut = $Priv })
$nvs1 = Sha '0x9000' '0x6000'
Remove-Item $Log
$r = Run-Tool @{ Action = 'RemoveAssets' }
Ok 'RemoveAssets: assets partition erased' (($r -eq 'ok') -and ((Py @($Util, 'allff', $Dev, '0x610000', '0x9F0000')) -eq 'OK')) $r
Ok 'RemoveAssets: gift app and settings kept' ((Same '0x10000' (Join-Path $Out 'pokedock_m6_gift_app.bin')) -and ((Sha '0x9000' '0x6000') -eq $nvs1))
Copy-Item $Log (Join-Path $ArgvDump 'flash_argv_removeassets.log') -Force
Ok 'RemoveAssets: argv' (@(Writes)[0] -eq 'erase_region|0x610000|0x9F0000') (@(Writes)[0])
$r = Run-Tool @{ Action = 'RestoreMfgApp' }
Ok 'RestoreMfgApp: m6-0.3.0 app back at 0x10000, settings kept' (($r -eq 'ok') -and (Same '0x10000' (Join-Path $Out 'pokedock_m6_mfg_app.bin')) -and ((Sha '0x9000' '0x6000') -eq $nvs1)) $r
$nvsCopy = Latest 'pokedock_nvs_*.bin'
Py @($Util, 'poke', $Dev, '0x9100', '0102030405') | Out-Null
$r = Run-Tool @{ Action = 'RestoreNvs'; From = $nvsCopy }
Ok 'RestoreNvs: settings back exactly' (($r -eq 'ok') -and (Same '0x9000' $nvsCopy)) $r
$r = Run-Tool @{ Action = 'RestoreNvs'; From = (Join-Path $Out 'pokedock_m6_gift_app.bin') }
Ok 'RestoreNvs with a wrong file: refused' ($r -like '*0x6000*') $r
New-Ball 'mfg'
$r = Run-Tool @{ Action = 'UpdateAssets'; PrivateOut = $Priv }
Ok 'UpdateAssets: pack written, manufacturing app untouched' (($r -eq 'ok') -and (Same '0x610000' (Join-Path $Priv 'assets_pack.bin')) -and (Same '0x10000' (Join-Path $W 'mfg.bin'))) $r
$r = Run-Tool @{ Action = 'InstallGift' }
Ok 'InstallGift without -PrivateOut: refused' ($r -like '*-PrivateOut*') $r

# 8. FirstInstall (M7 self-build: a new board still has the Waveshare factory layout)
New-Ball 'factory' 'factory'
$orig = Sha '0x0' '0x1000000'
$r = Run-Tool @{ Action = 'FirstInstall'; PrivateOut = $Priv }
Ok 'FirstInstall on a factory board: succeeds' ($r -eq 'ok') $r
$wr = @(Writes)
$expect = @('write_flash', '0x0', (Join-Path $Out 'pokedock_m6_gift.bin'), '0x610000', (Join-Path $Priv 'assets_pack.bin'), '0xFFF000', (Join-Path $Priv 'message_slot.bin'))
Copy-Item $Log (Join-Path $ArgvDump 'flash_argv_firstinstall.log') -Force
Ok 'FirstInstall: exact argv (merged at 0x0 + pack + slot)' (($wr.Count -eq 1) -and ($wr[0] -eq ($expect -join '|'))) ($wr -join ' || ')
$first = (@(Cmds) | Select-Object -First 2 | ForEach-Object { ($_ -split '\|')[0] }) -join ','
Ok 'FirstInstall: chip check and full factory backup first' ($first -eq 'flash_id,read_flash') $first
$fbk = Latest 'pokedock_full_*.bin'
Ok 'FirstInstall: backup holds the factory firmware' ((Py @($Util, 'sha', $fbk, '0x0', '0x1000000')) -eq $orig)
Ok 'FirstInstall: gift app at 0x10000' (Same '0x10000' (Join-Path $Out 'pokedock_m6_gift_app.bin'))
[IO.File]::WriteAllBytes((Join-Path $W 'tbl.bin'), [IO.File]::ReadAllBytes($Dev)[0x8000..0x8BFF])
$tchk = & python -X utf8 $Check 'ptable' (Join-Path $W 'tbl.bin'); $tcode = $LASTEXITCODE
Ok 'FirstInstall: table on the ball equals firmware/partitions.csv' ($tcode -eq 0) "$tchk"
$r = Run-Tool @{ Action = 'Check' }
Ok 'after FirstInstall: Check identifies the gift app' ($r -eq 'ok') $r
Remove-Item $Log
$r = Run-Tool @{ Action = 'FirstInstall'; PrivateOut = $Priv }
Ok 'FirstInstall on a PokeDock-layout ball: refused, nothing written' (($r -like '*InstallGift*') -and (Writes).Count -eq 0) $r
$r = Run-Tool @{ Action = 'RestoreFull'; From = $fbk }
Ok 'RestoreFull with the factory backup: whole 16 MiB back to factory' (($r -eq 'ok') -and ((Sha '0x0' '0x1000000') -eq $orig)) $r
New-Ball 'factory' 'factory'
$r = Run-Tool @{ Action = 'FirstInstall' }
Ok 'FirstInstall without -PrivateOut: merged written, assets erased' (($r -eq 'ok') -and (@(Writes)[1] -eq 'erase_region|0x610000|0x9F0000') -and ((Py @($Util, 'allff', $Dev, '0x610000', '0x9F0000')) -eq 'OK')) ((@(Writes)) -join ' || ')
New-Ball 'factory' 'factory'
$r = Run-Tool @{ Action = 'FirstInstall'; PrivateOut = $Priv; Rotate180 = $true }
Ok 'FirstInstall -Rotate180: rotate180 merged image' (($r -eq 'ok') -and (Same '0x10000' (Join-Path $Out 'pokedock_m6_gift_app_rotate180.bin'))) $r
New-Ball 'factory' 'factory'
Copy-Item (Join-Path $Out 'pokedock_m6_gift.bin') (Join-Path $W 'merged_keep.bin')
Py @($Util, 'poke', (Join-Path $Out 'pokedock_m6_gift.bin'), '0x10500', 'deadbeef') | Out-Null
$r = Run-Tool @{ Action = 'FirstInstall'; PrivateOut = $Priv }
Ok 'FirstInstall with a modified merged image: refused, nothing sent' (($r -like '*refused*') -and ((Cmds).Count -eq 0)) $r
Copy-Item (Join-Path $W 'merged_keep.bin') (Join-Path $Out 'pokedock_m6_gift.bin') -Force

Remove-Item -Recurse -Force $W
$failed = @($results | Where-Object { -not $_.Pass }).Count
Write-Host ("{0}: {1}/{2} flash tool checks (mock esptool, not a real ball)" -f $(if ($failed) { 'FAIL' } else { 'PASS' }), ($results.Count - $failed), $results.Count)
if ($failed) { exit 1 }
