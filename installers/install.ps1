param(
    [switch]$VerboseMode,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: install.ps1 [-VerboseMode]" 
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -VerboseMode   Show progress messages during installation"
    exit 0
}

function Write-Log {
    param([string]$Message)
    if ($VerboseMode) {
        Write-Host "[install] $Message"
    }
}

$Root = (Convert-Path (Join-Path $PSScriptRoot ".."))
Set-Location $Root

$Python = "python"
try {
    & $Python --version | Out-Null
} catch {
    Write-Error "Python is required but was not found on PATH."
    exit 1
}

$VenvPath = Join-Path $Root ".venv"
if (-not (Test-Path $VenvPath)) {
    Write-Log "Creating virtual environment"
    & $Python -m venv $VenvPath
} else {
    Write-Log "Virtual environment already exists"
}

$VenvPython = Join-Path $VenvPath "Scripts/python.exe"
$VenvPip = Join-Path $VenvPath "Scripts/pip.exe"

Write-Log "Upgrading pip"
if ($VerboseMode) {
    & $VenvPip install --upgrade pip
} else {
    & $VenvPip install --upgrade pip | Out-Null
}

Write-Log "Installing project dependencies"
if ($VerboseMode) {
    & $VenvPip install -e .[server,dev]
} else {
    & $VenvPip install -q -e .[server,dev] | Out-Null
}

$Prefix = Join-Path $Root ".min_tokenization_translator\bin"
if (-not (Test-Path $Prefix)) {
    New-Item -ItemType Directory -Force -Path $Prefix | Out-Null
}

Write-Log "Creating CLI wrappers"
$BootstrapScript = @"
`$RootDir = "$Root"
& "$VenvPython" "$Root\scripts\bootstrap_session.py" @args
"@
Set-Content -Path (Join-Path $Prefix "mtt-bootstrap.ps1") -Value $BootstrapScript -Encoding UTF8

$BenchmarkScript = @"
`$RootDir = "$Root"
& "$VenvPython" "$Root\scripts\run_benchmark.py" @args
"@
Set-Content -Path (Join-Path $Prefix "mtt-benchmark.ps1") -Value $BenchmarkScript -Encoding UTF8

$BootstrapBat = @"
@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0mtt-bootstrap.ps1" %*
"@
Set-Content -Path (Join-Path $Prefix "mtt-bootstrap.bat") -Value $BootstrapBat -Encoding ASCII

$BenchmarkBat = @"
@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0mtt-benchmark.ps1" %*
"@
Set-Content -Path (Join-Path $Prefix "mtt-benchmark.bat") -Value $BenchmarkBat -Encoding ASCII

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Log "Building Docker image (min-tokenization-translator:latest)"
    if ($VerboseMode) {
        docker build -t min-tokenization-translator:latest $Root
    } else {
        docker build -q -t min-tokenization-translator:latest $Root | Out-Null
    }
} else {
    Write-Log "Docker not available; skipping image build"
}

Write-Host "Installation complete."
Write-Host "Add $Prefix to your PATH, e.g.:"
Write-Host "  setx PATH `%PATH%;$Prefix"
Write-Host ""
Write-Host "Available commands:"
Write-Host "  mtt-bootstrap"
Write-Host "  mtt-benchmark"
