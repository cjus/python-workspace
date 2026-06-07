#Requires -Version 5.1
# Start the Jupyter AI (v3) environment on Windows.
#
# This is the Windows port of start.sh (same behavior, same order). Run it via
# start.cmd, which works under Windows' default "Restricted" execution policy:
#
#   start.cmd
#
# or directly:  powershell -NoProfile -ExecutionPolicy Bypass -File start.ps1
#
# Chat is served by the Jupyternaut agent; pick the model in Jupyternaut
# Settings and @-mention @Jupyternaut in a chat.
#
# Backend: Ollama (local, default) or OpenRouter (hosted). Ollama is required
# unless OPENROUTER_API_KEY is set, in which case a missing Ollama server is a
# warning rather than an error (so you can run OpenRouter-only).
#
# Steps performed:
#   1. Check the Ollama server (fatal unless OPENROUTER_API_KEY is set).
#   2. Ensure the local virtualenv (creating/installing it if missing).
#   3. Launch JupyterLab with the Jupyter AI chat enabled.
#
# NOTE: this file is intentionally ASCII-only and avoids '&&'/'||' so it runs
# under stock Windows PowerShell 5.1 (which mis-decodes BOM-less UTF-8 and
# lacks the pipeline-chain operators that PowerShell 7 added).

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

# Run a native exe with ALL output suppressed; return its exit code.
# (A wrapper is needed because under $ErrorActionPreference='Stop', Windows
# PowerShell 5.1 turns redirected stderr lines from native commands into
# terminating errors -- the "NativeCommandError" gotcha.)
function Invoke-NativeQuiet {
    param([string]$Exe, [object[]]$ArgList)
    $eap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Exe @ArgList *> $null } catch { return 127 }
    finally { $ErrorActionPreference = $eap }
    return $LASTEXITCODE
}

# Ollama's OLLAMA_HOST convention allows a bare host:port (no scheme).
$OllamaHostUrl = if ($env:OLLAMA_HOST) { $env:OLLAMA_HOST } else { 'http://127.0.0.1:11434' }
if ($OllamaHostUrl -notmatch '^[A-Za-z][A-Za-z0-9+.-]*://') {
    $OllamaHostUrl = "http://$OllamaHostUrl"
}

# 1. Is Ollama running? (On Windows the Ollama app normally autostarts in the
#    tray, so this usually passes without a manual 'ollama serve'.)
$OllamaUp = $false
try {
    Invoke-WebRequest -UseBasicParsing -Uri "$OllamaHostUrl/api/tags" -TimeoutSec 3 | Out-Null
    $OllamaUp = $true
} catch {
    if ($env:OPENROUTER_API_KEY) {
        Write-Host "WARNING: Ollama not reachable at $OllamaHostUrl, but OPENROUTER_API_KEY is set."
        Write-Host '         Continuing for OpenRouter use (local Ollama models will be unavailable).'
    } else {
        Write-Host "ERROR: Ollama server not reachable at $OllamaHostUrl"
        Write-Host 'Start the Ollama app (or run: ollama serve), or set OPENROUTER_API_KEY to use OpenRouter instead.'
        exit 1
    }
}

# 2. Ensure the virtualenv exists and its dependencies are in sync.
#    Windows venv layout: the interpreter lives at .venv\Scripts\python.exe
#    (not .venv/bin/python as on macOS/Linux).
$VenvDir = Join-Path $PSScriptRoot '.venv'
$VenvPy  = Join-Path $VenvDir 'Scripts\python.exe'

if (-not (Test-Path -LiteralPath $VenvDir)) {
    Write-Host 'Creating virtualenv (first run)...'
    # Prefer the 'py' launcher: bare 'python' may be the Microsoft Store stub
    # on a machine where Python isn't actually installed.
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv $VenvDir
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv $VenvDir
    } else {
        Write-Host 'ERROR: Python not found. Install Python 3.9+ from https://www.python.org/downloads/'
        Write-Host '       (or the Microsoft Store) and re-run this script.'
        exit 1
    }
    if (($LASTEXITCODE -ne 0) -or (-not (Test-Path -LiteralPath $VenvPy))) {
        Write-Host 'ERROR: could not create .venv (is Python 3.9+ installed and on PATH?)'
        exit 1
    }
    & $VenvPy -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { Write-Host 'ERROR: pip self-upgrade failed.'; exit 1 }
}

# (Re)install deps whenever requirements.txt is newer than the last install.
# Installing only on venv creation would mean dependencies ADDED to
# requirements.txt later silently never land in an existing .venv. The stamp
# makes the launcher idempotent and self-healing while staying fast on
# unchanged runs. (This mirrors start.sh's '-nt' mtime check.)
$ReqTxt   = Join-Path $PSScriptRoot 'requirements.txt'
$ReqStamp = Join-Path $VenvDir '.requirements-installed'
$NeedInstall = -not (Test-Path -LiteralPath $ReqStamp)
if (-not $NeedInstall) {
    $ReqTime   = (Get-Item -LiteralPath $ReqTxt).LastWriteTimeUtc
    $StampTime = (Get-Item -LiteralPath $ReqStamp).LastWriteTimeUtc
    $NeedInstall = ($ReqTime -gt $StampTime)
}
if ($NeedInstall) {
    Write-Host 'Installing/updating dependencies from requirements.txt...'
    & $VenvPy -m pip install -r $ReqTxt
    if ($LASTEXITCODE -ne 0) { Write-Host 'ERROR: pip install failed.'; exit 1 }
    New-Item -ItemType File -Path $ReqStamp -Force | Out-Null
    (Get-Item -LiteralPath $ReqStamp).LastWriteTimeUtc = [DateTime]::UtcNow
}

# Pin the Jupyter kernelspec to THIS venv's interpreter (absolute path).
# ipykernel ships a default kernelspec whose argv[0] is the bare string
# "python" (PATH-relative). On a machine where bare 'python' resolves to
# another interpreter (or the Store stub), notebooks would silently run
# OUTSIDE this venv and miss its deps. Rewriting the spec via
# 'ipykernel install' pins argv[0] to .venv\Scripts\python.exe.
# '--sys-prefix' writes to .venv\share\jupyter\kernels\python3\kernel.json
# (same layout as POSIX). The check parses kernel.json instead of
# string-matching, because JSON escapes the backslashes in Windows paths.
$KernelJson = Join-Path $VenvDir 'share\jupyter\kernels\python3\kernel.json'
$NeedPin = $true
if (Test-Path -LiteralPath $KernelJson) {
    try {
        $argv0 = (Get-Content -Raw -Encoding UTF8 -LiteralPath $KernelJson | ConvertFrom-Json).argv[0]
        # Normalize both sides so formatting differences (8.3 names, stray
        # separators) don't cause a needless re-pin on every launch.
        if ($argv0 -and ([System.IO.Path]::GetFullPath($argv0) -ieq [System.IO.Path]::GetFullPath($VenvPy))) {
            $NeedPin = $false
        }
    } catch { $NeedPin = $true }
}
if ($NeedPin) {
    Write-Host 'Pinning Jupyter kernelspec to the venv interpreter...'
    $PinRc = Invoke-NativeQuiet $VenvPy @(
        '-m', 'ipykernel', 'install', '--sys-prefix',
        '--name', 'python3', '--display-name', 'Python 3 (.venv)'
    )
    if ($PinRc -ne 0) {
        # Fail closed (start.sh does too, via set -e): an unpinned kernel can
        # silently run notebooks OUTSIDE this venv.
        Write-Host 'ERROR: failed to pin the Jupyter kernelspec to the venv interpreter.'
        exit 1
    }
}

# Jupyter AI v3 ships no model agent by default; the Ollama/OpenRouter chat
# needs the optional Jupyternaut agent (the [jupyternaut] extra). Warn if
# it's missing.
if ((Invoke-NativeQuiet $VenvPy @('-c', 'import jupyter_ai_jupyternaut')) -ne 0) {
    Write-Host "WARNING: the Jupyternaut agent isn't installed in .venv, so @Jupyternaut"
    Write-Host '         won''t appear in chats. Reinstall deps: .venv\Scripts\python.exe -m pip install -r requirements.txt'
}

# 3. Launch JupyterLab.
# $DefaultModel is the default *Ollama* model (only used for the message +
# check below). gemma4:12b is the repo default on every platform -- the
# standard GGUF tag that fits ~16 GB machines (use gemma4:26b on a >=32 GB
# RAM / large-GPU box; see docs/TEACHERS-GUIDE.md for advanced options).
# The model Jupyter AI actually loads comes from Jupyternaut Settings, saved
# in %APPDATA%\jupyter\jupyter_ai\config.json -- OpenRouter models are
# selected there too. See SETUP.md.
$DefaultModel = 'gemma4:12b'
if ($OllamaUp) {
    Write-Host "Ollama OK at $OllamaHostUrl. Default Ollama model for this repo: $DefaultModel"
    Write-Host 'Available models:'
    $ModelLines = @()
    try { $ModelLines = @(& ollama list) } catch { $ModelLines = @() }
    $ModelLines | ForEach-Object { Write-Host $_ }
    if (-not ($ModelLines -match [regex]::Escape($DefaultModel))) {
        Write-Host "NOTE: default model '$DefaultModel' not pulled yet. Run: ollama pull $DefaultModel"
    }
    # RAM sanity check: the default 12B model wants ~16 GB. On a smaller machine
    # warn (don't block) and point to the lighter model from the Teacher's Guide.
    # Any detection hiccup is silently skipped -- this is advisory only.
    try {
        $RamBytes = (Get-CimInstance -ClassName Win32_ComputerSystem -ErrorAction Stop).TotalPhysicalMemory
        if ($RamBytes -and ($RamBytes -gt 0)) {
            $RamGiB = [int]($RamBytes / 1GB)
            # 15, not 16: Windows reports usable RAM minus hardware-reserved
            # memory, so a real 16 GB machine can compute 15 and would false-warn.
            if ($RamGiB -lt 15) {
                Write-Host "NOTE: this machine has about $RamGiB GB RAM; the default '$DefaultModel' wants ~16 GB"
                Write-Host '      and may be slow or stall. A lighter model that still works well:'
                Write-Host '      ollama pull gemma4:e2b-it-qat   (then pick ollama_chat/gemma4:e2b-it-qat in Settings)'
            }
        }
    } catch { }
}
Write-Host ''
Write-Host 'Tip: open a chat from the launcher (Chat card) and @-mention @Jupyternaut,'
Write-Host '     or @-mention @Tutor for the built-in Python tutor persona.'
Write-Host "     Pick the model in Settings -> Jupyternaut Settings (e.g. ollama_chat/$DefaultModel)."
Write-Host ''

# --config applies jupyter_ai_config.py (e.g. the per-model num_ctx caps).
# @args forwards any arguments given to this script, like "$@" in start.sh.
$ConfigPy = Join-Path $PSScriptRoot 'jupyter_ai_config.py'
& (Join-Path $VenvDir 'Scripts\jupyter.exe') lab "--config=$ConfigPy" @args
exit $LASTEXITCODE
