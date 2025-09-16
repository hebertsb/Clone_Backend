<#
Script mínimo para ejecutar todas las migraciones sin crear venv.
Uso (desde la raíz del repo, con el entorno apropiado activado si es necesario):
  powershell -File .\scripts\migrate_all.ps1
Esto ejecuta: `.venv\Scripts\python.exe manage.py migrate --noinput` si existe .venv,
o `python manage.py migrate --noinput` si no existe.
#>

Write-Host "Running migrate_all.ps1"

$python = "python"
if (Test-Path ".venv\Scripts\python.exe") { $python = ".\.venv\Scripts\python.exe" }

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $python
$psi.Arguments = "manage.py migrate --noinput"
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false

$p = [System.Diagnostics.Process]::Start($psi)
$out = $p.StandardOutput.ReadToEnd()
$err = $p.StandardError.ReadToEnd()
$p.WaitForExit()

Write-Host $out
if ($err) { Write-Error $err }

if ($p.ExitCode -ne 0) { exit $p.ExitCode }

Write-Host "migrate_all.ps1 finished."
