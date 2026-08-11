<#
PowerShell one-click installer for Windows (Windows 10+)

Usage (from repository root where this script lives):
  Right-click -> Run with PowerShell (or open PowerShell as Administrator)
  Or run from PowerShell terminal:
    .\setup_windows.ps1 [-Yes] [ -Serve ] [ -Model "qwen2.5:1.5b" ]

Options:
  -Yes    : auto-accept prompts and install packages non-interactively when possible
  -Serve  : start `ollama serve` after pulling the model
  -Model  : override the model to pull (default taken from .env or .env.example, fallback qwen2.5:1.5b)

Notes:
- The script prefers winget when available. If winget cannot install Ollama, the script will ask the user to install Ollama manually from https://ollama.com/download or provide a way to continue without it.
- This script will attempt to install system packages (Python, Node) using the system package manager and therefore requires Administrator privileges for those steps.
- If you cannot run elevated installs, install Python (3.8+), Node (LTS), and Ollama manually, then re-run the script to perform repo-local steps (venv, pip, npm, model pull).
#>

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [switch]$Yes,
    [switch]$Serve,
    [string]$Model = ''
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Elevate if needed for system installs
function Ensure-Elevated {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Warn "Some installation steps require Administrator privileges. Attempting to re-launch elevated..."
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = 'powershell'
        $args = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        if ($Yes) { $args += ' -Yes' }
        if ($Serve) { $args += ' -Serve' }
        if ($Model) { $args += " -Model `"$Model`"" }
        $psi.Arguments = $args
        $psi.Verb = 'runas'
        try {
            [System.Diagnostics.Process]::Start($psi) | Out-Null
            Exit
        } catch {
            Write-Err "Failed to elevate: $_"
            Write-Err "Please re-run this script from an elevated PowerShell prompt (Run as Administrator)."
            Exit 1
        }
    }
}

# prefer winget when available
function Get-PackageManager {
    if (Get-Command winget -ErrorAction SilentlyContinue) { return 'winget' }
    if (Get-Command choco -ErrorAction SilentlyContinue) { return 'choco' }
    if (Get-Command scoop -ErrorAction SilentlyContinue) { return 'scoop' }
    return $null
}

function Install-Package($pkgId, $pkgName) {
    $pm = Get-PackageManager
    if (-not $pm) {
        Write-Warn "No supported package manager (winget/choco/scoop) found. Please install $pkgName manually and re-run the script."
        return $false
    }
    Write-Info "Installing $pkgName using $pm..."
    try {
        switch ($pm) {
            'winget' {
                # use -e (exact) where possible; winget IDs differ across systems
                & winget install --accept-package-agreements --accept-source-agreements --id $pkgId -e
            }
            'choco' {
                & choco install $pkgId -y
            }
            'scoop' {
                & scoop install $pkgId
            }
        }
        return $true
    } catch {
        Write-Warn "Package manager $pm failed to install $pkgName: $_"
        return $false
    }
}

# Determine script root (repo root)
$RepoRoot = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location -Path $RepoRoot
Write-Info "Repository root: $RepoRoot"

# Determine model from .env or .env.example unless user provided -Model
if (-not $Model) {
    $envPath = Join-Path $RepoRoot '.env'
    $envExamplePath = Join-Path $RepoRoot '.env.example'
    $modelLine = ''
    if (Test-Path $envPath) { $modelLine = Select-String -Path $envPath -Pattern '^\s*OLLAMA_MODEL\s*=' -SimpleMatch -ErrorAction SilentlyContinue | Select-Object -First 1 }
    if (-not $modelLine -and (Test-Path $envExamplePath)) { $modelLine = Select-String -Path $envExamplePath -Pattern '^\s*OLLAMA_MODEL\s*=' -SimpleMatch -ErrorAction SilentlyContinue | Select-Object -First 1 }
    if ($modelLine) {
        $Model = ($modelLine.ToString() -split '=')[1].Trim() -replace '"','' -replace "'",''
    }
}
if (-not $Model) { $Model = 'qwen2.5:1.5b' }
Write-Info "Using Ollama model: $Model"

# 1) Ensure prerequisites: python3, python -m venv, node, npm, curl
$missing = @()
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) { $missing += 'python' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { $missing += 'node' }
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { $missing += 'npm' }
if (-not (Get-Command curl -ErrorAction SilentlyContinue)) { $missing += 'curl' }

if ($missing.Count -gt 0) {
    Write-Warn "Missing system tools: $($missing -join ', ')"
    if ($Yes) {
        Ensure-Elevated
        $pm = Get-PackageManager
        if (-not $pm) {
            Write-Err "No package manager found (winget/choco/scoop). Please install the missing tools manually: $($missing -join ', ')"
            Exit 1
        }
        foreach ($m in $missing) {
            switch ($m) {
                'python' {
                    # winget id: Python.Python.3 (try common IDs)
                    if (-not (Install-Package 'Python.Python.3' 'Python 3')) { Install-Package 'Python.Python' 'Python' } }
                'node' {
                    Install-Package 'OpenJS.NodeJS.LTS' 'Node.js LTS' }
                'npm' { Write-Info 'npm is provided by the Node.js installer; if missing, ensure Node was installed.' }
                'curl' { Install-Package 'curl' 'curl' }
            }
        }
    } else {
        Write-Warn "The script can install missing tools automatically using winget/choco/scoop. Run with -Yes to auto-install, or install these manually and re-run: $($missing -join ', ')"
        # continue to repo-local steps if python/node exist afterwards
    }
}

# Refresh commands after potential install
Start-Sleep -Seconds 2

# 2) Create .env from .env.example if missing
$envFile = Join-Path $RepoRoot '.env'
$envExample = Join-Path $RepoRoot '.env.example'
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Copy-Item -Path $envExample -Destination $envFile -Force
    Write-Info "Created .env from .env.example"
}

# 3) Setup Python virtualenv and install backend requirements
$VenvPath = Join-Path $RepoRoot 'backend\.venv'
if (-not (Test-Path $VenvPath)) {
    # prefer 'python' or 'python3'
    $pyCmd = (Get-Command python -ErrorAction SilentlyContinue) ? 'python' : 'python3'
    if (-not (Get-Command $pyCmd -ErrorAction SilentlyContinue)) {
        Write-Err "Python not found. Please install Python 3.8+ and re-run the script."
        Exit 1
    }
    Write-Info "Creating virtual environment at backend\\.venv using $pyCmd"
    & $pyCmd -m venv "$VenvPath"
} else {
    Write-Info "Virtualenv already exists at backend\\.venv"
}

# Activate venv for pip install (PowerShell activation)
$activate = Join-Path $VenvPath 'Scripts\Activate.ps1'
if (-not (Test-Path $activate)) {
    Write-Warn "Virtualenv activation script not found at $activate — continuing but pip may target system Python"
} else {
    Write-Info "Activating virtualenv"
    try {
        & $activate
    } catch {
        Write-Warn "Failed to run Activate.ps1; using explicit venv pip/py invocation instead"
    }
}

# Use venv pip if available
$Pip = Join-Path $VenvPath 'Scripts\pip.exe'
if (-not (Test-Path $Pip)) { $Pip = (Get-Command pip -ErrorAction SilentlyContinue).Source }
if (-not $Pip) {
    Write-Err "pip not found. Ensure Python environment is correct."
    Exit 1
}

$ReqFile = Join-Path $RepoRoot 'backend\requirements.txt'
if (Test-Path $ReqFile) {
    Write-Info "Installing Python requirements from backend\\requirements.txt"
    & "$Pip" install --upgrade pip setuptools wheel
    & "$Pip" install --upgrade -r "$ReqFile"
} else {
    Write-Warn "backend\\requirements.txt not found — skipping Python dependency installation"
}

# 4) Install frontend Node dependencies
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Err "npm is not found. Please install Node.js (which includes npm) and re-run the script."
    Exit 1
}

Push-Location -Path (Join-Path $RepoRoot 'frontend')
if (Test-Path 'package-lock.json') {
    Write-Info "Running npm ci in frontend"
    npm ci
} else {
    Write-Info "Running npm install in frontend"
    npm install
}
Pop-Location

# 5) Ollama: check for binary and try to install/prompt
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Write-Warn "Ollama CLI not found on PATH."
    $pm = Get-PackageManager
    if ($pm -and $Yes) {
        Write-Info "Attempting to install Ollama via $pm"
        $installed = $false
        if ($pm -eq 'winget') {
            try { & winget install --accept-package-agreements --accept-source-agreements --id Ollama.Ollama -e; $installed = $true } catch { $installed = $false }
        } elseif ($pm -eq 'choco') {
            try { choco install ollama -y; $installed = $true } catch { $installed = $false }
        }
        if ($installed) { Write-Info "Ollama installation attempted via $pm" } else { Write-Warn "Automated Ollama install via $pm failed or package not found." }
    }

    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Warn "Ollama not installed. Please download and install Ollama for Windows from https://ollama.com/download and ensure 'ollama' is on PATH."
        if (-not $Yes) {
            Read-Host "Press ENTER after Ollama is installed to continue (or Ctrl+C to abort)"
        } else {
            Write-Warn "Continuing without Ollama — model pull and AI features will be skipped until Ollama is installed."
        }
    }
}

# 6) Pull the model if Ollama is available
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Info "Checking existing Ollama models"
    try {
        $list = ollama list 2>$null
        if ($list -match [regex]::Escape($Model)) {
            Write-Info "Model $Model already present"
        } else {
            Write-Info "Pulling model $Model (this may take a while)"
            ollama pull $Model
        }
    } catch {
        Write-Warn "Failed to query/pull models with Ollama: $_"
    }
} else {
    Write-Warn "Ollama not available; skipping model pull"
}

# 7) Optionally start Ollama serve
if ($Serve) {
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        Write-Info "Starting 'ollama serve' in background. Output will be in $RepoRoot\\ollama-serve.log"
        $log = Join-Path $RepoRoot 'ollama-serve.log'
        Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden -RedirectStandardOutput $log -RedirectStandardError $log
        Start-Sleep -Seconds 2
        Write-Info "Started ollama serve (check $log for logs)."
    } else {
        Write-Warn "Cannot start Ollama because it is not installed."
    }
}

Write-Info "SETUP COMPLETE"
Write-Host "Backend virtualenv: backend\\.venv (activate using: backend\\.venv\\Scripts\\Activate.ps1)"
Write-Host "Frontend: node modules installed in frontend\\node_modules"
Write-Host "Environment file: $envFile"
Write-Host "Ollama model: $Model (if Ollama was installed)

Next steps:
  - Activate backend venv: .\\backend\\.venv\\Scripts\\Activate.ps1
  - Start backend: cd backend; uvicorn app.main:app --reload --port 8000
  - Start frontend: cd frontend; npm run dev
  - Start Ollama if not started: ollama serve
"

Exit 0
