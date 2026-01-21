<#
.SYNOPSIS
  Convert repository to package-friendly layout & fix encoding issues (remove BOM).
  This script focuses on two fixes:
    - rewrite setup.cfg without BOM (fix configparser MissingSectionHeaderError)
    - rewrite src/chem_standard/__init__.py with safe UTF-8 content (no garbled comments)
  It also attempts `pip install -e .` at the end.

.NOTES
  Run this script from the repository root (D:\chem_standard).
  Usage: PowerShell -ExecutionPolicy Bypass -File .\convert_to_package.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Log {
    param($msg)
    $t = (Get-Date).ToString("u")
    Write-Output "[$t] $msg"
}

# 1) 基本检查：确保在仓库根
$repoRoot = (Get-Location).Path
Write-Log "Starting package conversion script. Repository root: $repoRoot"

# Ensure we have a .git folder
if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Log "ERROR: Current directory does not appear to be a git repository (no .git). Exiting."
    exit 1
}

# 2) 创建/切换到专用分支并保存未提交改动（安全）
$branch = "infra/convert-to-package"
$currentBranch = (& git rev-parse --abbrev-ref HEAD).Trim()
Write-Log "Current git branch: $currentBranch"

# Create branch if not exists
$branches = & git branch --list $branch
if ($branches -eq "") {
    Write-Log "Creating branch: $branch"
    & git checkout -b $branch
} else {
    Write-Log "Switching to existing branch: $branch"
    & git checkout $branch
}

# If there are uncommitted changes, make a backup commit
$porcelain = (& git status --porcelain).Trim()
if ($porcelain) {
    Write-Log "Uncommitted changes detected. Creating temporary backup commit."
    & git add -A
    & git commit -m "chore: backup before package conversion" | Out-Null
} else {
    Write-Log "No uncommitted changes."
}

# 3) Ensure directories exist
$pkgInitPath = Join-Path $repoRoot "src\chem_standard\__init__.py"
if (-not (Test-Path (Split-Path $pkgInitPath -Parent))) {
    Write-Log "Creating package directory src\chem_standard"
    New-Item -ItemType Directory -Path (Split-Path $pkgInitPath -Parent) -Force | Out-Null
}

# 4) Recreate setup.cfg WITHOUT BOM using .NET UTF8Encoding(false)
$setupCfgPath = Join-Path $repoRoot "setup.cfg"

# Recommended setup.cfg content (adjust authors/email if you want)
$setupCfgContent = @"
[metadata]
name = chem_standard
version = 0.1.0
description = chem_standard — atomic/reaction standardization and tools
long_description = file: README.md
long_description_content_type = text/markdown
author = Zhang Da
author_email = zhangda@users.noreply.github.com
license = MIT

[options]
packages = find:
package_dir =
    = src
python_requires = >=3.10

[options.packages.find]
where = src
"@

Write-Log "Backing up existing setup.cfg if present"
if (Test-Path $setupCfgPath) {
    Copy-Item -Path $setupCfgPath -Destination ($setupCfgPath + ".bak") -Force
    Write-Log "Backed up setup.cfg -> setup.cfg.bak"
}

Write-Log "Writing setup.cfg without BOM"
# Use .NET API to write UTF-8 without BOM reliably
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($setupCfgPath, $setupCfgContent, $utf8NoBom)
Write-Log "setup.cfg written (UTF-8 no BOM)."

# 5) Fix src/chem_standard/__init__.py content (no BOM, safe comments)
$initPath = $pkgInitPath
$initContent = @'
"""Top-level package for chem_standard.

Export the core public types for convenience:
  from chem_standard import Atom, Molecule, Reaction
Keep comments plain ASCII/UTF-8 to avoid encoding issues.
"""

# Public exports
from .atom import Atom
from .molecule import Molecule
from .reaction import Reaction

# Optional subpackages (uncomment if you want to expose these at package root)
# from . import io, graph, dataset, rules, path, ml, signature, identity
'@

Write-Log "Backing up existing __init__.py if present"
if (Test-Path $initPath) {
    Copy-Item -Path $initPath -Destination ($initPath + ".bak") -Force
    Write-Log "Backed up __init__.py -> __init__.py.bak"
}

Write-Log "Writing src/chem_standard/__init__.py (UTF-8 no BOM)"
[System.IO.File]::WriteAllText($initPath, $initContent, $utf8NoBom)
Write-Log "__init__.py written."

# 6) Search & fix any lingering 'from src.' import patterns inside src/ files (best-effort)
# This replaces "from src." with "from chem_standard." only in .py files inside src\ (skip tests and examples).
Write-Log "Scanning src/ for 'from src.' and 'import src.' occurrences and replacing with package imports"
Get-ChildItem -Path (Join-Path $repoRoot "src") -Recurse -Include *.py |
    Where-Object { $_.FullName -notmatch "\\tests\\" -and $_.FullName -notmatch "\\examples\\" } |
    ForEach-Object {
        $text = Get-Content -Raw -LiteralPath $_.FullName -Encoding UTF8
        $new = $text -replace 'from\s+src\.', 'from chem_standard.' -replace 'import\s+src\.', 'import chem_standard.'
        if ($new -ne $text) {
            Copy-Item -Path $_.FullName -Destination ($_.FullName + ".bak") -Force
            [System.IO.File]::WriteAllText($_.FullName, $new, $utf8NoBom)
            Write-Log "Rewrote import references in: $($_.FullName)"
        }
    }

# 7) Try installing editable package
Write-Log "Attempting 'pip install -e .' (editable install). This may take a while."
try {
    & python -m pip install -e . --no-input
    Write-Log "pip install -e . completed (check output above for details)."
} catch {
    Write-Log "WARNING: pip install -e . failed. See error output above. You can inspect setup.cfg and pyproject.toml manually."
    Write-Log "Exception: $($_.Exception.Message)"
}

# 8) Run tests (optional): small smoke test using pytest
Write-Log "Running pytest -q (smoke test)."
try {
    & python -m pytest -q
    Write-Log "pytest completed (see above)."
} catch {
    Write-Log "pytest returned a non-zero exit code (see output above). This may be expected if tests depend on other state."
}

# 9) Post-run notes
Write-Log "Script finished. Recommended next steps:"
Write-Log "  1) Inspect setup.cfg and src/chem_standard/__init__.py.bak if anything unexpected."
Write-Log "  2) If editable install succeeded and tests pass, commit the deterministic fixes:"
Write-Log "       git add setup.cfg src/chem_standard/__init__.py"
Write-Log "       git commit -m 'chore(pkg): remove BOM and fix package init for packaging' && git push"
Write-Log "  3) If you prefer, revert automatic import replacements by restoring .bak files in src/ if any change is undesirable."
