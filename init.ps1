$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$Req = Join-Path $Root "requirements.txt"
$BinDir = Join-Path $env:LOCALAPPDATA "CoreUtils\bin"
$Launcher = Join-Path $BinDir "filejump.cmd"

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonExe = "py"
    $PythonArgs = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonExe = "python"
    $PythonArgs = @()
} else {
    throw "Python 3.11+ is required but was not found in PATH."
}

& $PythonExe @PythonArgs -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Python 3.11+ is required." }

if (-not (Test-Path (Join-Path $Venv "Scripts\python.exe"))) {
    Write-Host "Creating local virtual environment in $Venv"
    & $PythonExe @PythonArgs -m venv $Venv
}

$VenvPython = Join-Path $Venv "Scripts\python.exe"
Write-Host "Installing dependencies into $Venv"
& $VenvPython -m pip install --disable-pip-version-check -r $Req

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
@"
@echo off
set "PROJECT_ROOT=$Root"
set "VENV_PYTHON=$VenvPython"
"%VENV_PYTHON%" -m codejump.main %*
"@ | Set-Content -Path $Launcher -Encoding ASCII

Write-Host "Installed launcher: $Launcher"
Write-Host "Add $BinDir to PATH if you want to run filejump from any terminal."
Write-Host "Launching CodeJump..."
& $Launcher @args
