param(
  [string]$RootParts   = "C:\BRS-Nextcloud\Workshop_Construction",
  [string]$Base        = "C:\nx-quality",
  [int]$TimeoutMinutes = 60
)

$ErrorActionPreference = "Stop"
$bin     = Join-Path $Base "bin"
$reports = Join-Path $Base "reports"
$webData = Join-Path $Base "web\data"
$lock    = Join-Path $Base ".run.lock"

if (Test-Path $lock) { Write-Host "Already running. Exit."; exit 1 }
New-Item -Path $lock -ItemType File -Force | Out-Null

try {
  $stamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
  $out   = Join-Path $reports $stamp
  New-Item -Path $out -ItemType Directory -Force | Out-Null

  $journal   = Join-Path $bin "batch_runner.py"
  if (-not (Test-Path $journal)) { throw "Journal fehlt: $journal" }

  # Hinweis: UGII_BASE_DIR muss gesetzt sein (über NX Command Prompt oder ugiicmd.bat)
  $nxExe = Join-Path $env:UGII_BASE_DIR "ugii\run_journal.exe"
  if (-not (Test-Path $nxExe)) { throw "run_journal.exe nicht gefunden. UGII_BASE_DIR korrekt?" }

  $args = @(
    "`"$journal`"",
    "--root", "`"$RootParts`"",
    "--report", "`"$out`""
  )

  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $nxExe
  $psi.Arguments = $args -join " "
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError  = $true
  $psi.UseShellExecute = $false
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  [void]$p.Start()

  if (-not $p.WaitForExit($TimeoutMinutes * 60 * 1000)) {
    $p.Kill()
    throw "Timeout nach $TimeoutMinutes Minuten."
  }
  if ($p.ExitCode -ne 0) {
    $err = $p.StandardError.ReadToEnd()
    throw "NX Journal ExitCode $($p.ExitCode). Fehler: $err"
  }

  $json = Join-Path $out "results.json"
  if (!(Test-Path $json)) { throw "results.json fehlt in $out" }

  New-Item -ItemType Directory -Path $webData -Force | Out-Null
  Copy-Item $json (Join-Path $webData "latest.json") -Force

  Write-Host "OK: Artefakte in $out und web\data\latest.json aktualisiert."
}
catch {
  Write-Error $_
  exit 2
}
finally {
  if (Test-Path $lock) { Remove-Item $lock -Force }
}