    <#
convert_to_package.ps1

一键把仓库转换为 installable package (src layout -> package name chem_standard),
统一 import 路径 (from src.* -> from chem_standard.*, import src.* -> import chem_standard.*),
并执行 pip install -e . 与 pytest 验证，最后在测试通过时提交并 push。

运行示例（在仓库根 D:\chem_standard，确保激活了 chem-standard conda 环境）:
    # 如果系统策略限制脚本执行：
    PowerShell -ExecutionPolicy Bypass -File .\convert_to_package.ps1

或者在已允许运行脚本的 PowerShell 中：
    .\convert_to_package.ps1
#>

# ------------------------
# 配置（如需改动在此修改）
# ------------------------
$BranchName = "infra/convert-to-package"
$BackupCommitMsg = "chore: backup before package conversion"
$FinalCommitMsg = "chore(pkg): make project installable as chem_standard (src layout), unify imports and tests"
$PackageName = "chem_standard"
$SetupCfgContent = @"
[metadata]
name = chem_standard
version = 0.1.0
description = chem_standard — atomic/reaction standardization and tools
author = Zhang Da
author_email = zhangda@users.noreply.github.com
long_description = file: README.md
long_description_content_type = text/markdown

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.10

[options.packages.find]
where = src
"@

$InitTemplate = @"
# src/chem_standard/__init__.py
\"\"\"Top-level package for chem_standard.\"\"\"

# 常用导出，按需修改
from .atom import Atom
from .molecule import Molecule
from .reaction import Reaction

# 可选：暴露子包（按需取消注释）
# from . import io, graph, dataset, rules, path, ml, signature, identity
"@

# 排除路径片段（不会在这些目录下做替换）
$Excludes = @(
    ".git",
    ".venv",
    "venv",
    "env",
    "core__DEPRECATED",
    "build",
    "dist",
    "examples\\data",
    "__pycache__"
)

# ------------------------
# 工具函数
# ------------------------
function Write-Log($msg) {
    $ts = (Get-Date).ToString("u")
    Write-Host "[$ts] $msg"
}

function Is-GitRepo {
    try {
        git rev-parse --is-inside-work-tree > $null 2>&1
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Run-Or-Exit($cmd, $errMsg) {
    Write-Log "Running: $cmd"
    iex $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: $errMsg" -ForegroundColor Red
        throw "Command failed: $cmd"
    }
}

# ------------------------
# 开始执行
# ------------------------
Write-Log "Starting package conversion script. Make sure you're in the repository root."

if (-not (Is-GitRepo)) {
    Write-Host "This directory is not a git repository. Please run from repository root." -ForegroundColor Red
    exit 1
}

# 1) 切换/创建分支
Write-Log "Create/switch branch: $BranchName"
# If branch exists, checkout; otherwise create from current HEAD
$branchExists = git branch --list $BranchName | ForEach-Object { $_.Trim() }
if ($branchExists) {
    git checkout $BranchName
} else {
    git checkout -b $BranchName
}
if ($LASTEXITCODE -ne 0) { throw "Failed to create/switch branch $BranchName" }

# 2) 如果有未提交更改，先做一个备份提交（便于回滚）
$porcelain = git status --porcelain
if ($porcelain) {
    Write-Log "Uncommitted changes detected. Creating backup commit."
    git add -A
    git commit -m "$BackupCommitMsg"
    if ($LASTEXITCODE -ne 0) { throw "Backup commit failed." }
} else {
    Write-Log "Working tree clean. No backup commit necessary."
}

# 3) 创建 setup.cfg（如果不存在）
if (-not (Test-Path "setup.cfg")) {
    Write-Log "Creating setup.cfg"
    Set-Content -Path "setup.cfg" -Value $SetupCfgContent -Encoding UTF8
} else {
    Write-Log "setup.cfg already exists; leaving as-is (backup not overwritten)."
}

# 4) Ensure src/chem_standard/__init__.py exists
$pkgInitPath = Join-Path -Path "src" -ChildPath "$PackageName\__init__.py"
if (-not (Test-Path $pkgInitPath)) {
    Write-Log "Creating $pkgInitPath with recommended exports."
    # ensure directory exists
    $dir = Split-Path $pkgInitPath -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $pkgInitPath -Value $InitTemplate -Encoding UTF8
} else {
    Write-Log "$pkgInitPath exists; not overwriting."
}

# 5) 批量替换 Python 文件中的导入路径
Write-Log "Scanning *.py files and performing safe replacements..."

$modified = @()
$pyFiles = Get-ChildItem -Recurse -Filter *.py | Where-Object {
    # skip files within excluded paths
    $full = $_.FullName
    foreach ($ex in $Excludes) {
        if ($full -like "*$ex*") { return $false }
    }
    return $true
}

foreach ($f in $pyFiles) {
    $path = $f.FullName
    try {
        $text = Get-Content -Raw -LiteralPath $path -ErrorAction Stop
    } catch {
        Write-Log "Skipping unreadable file: $path"
        continue
    }
    $new = $text -replace 'from\s+src\.', "from $PackageName." -replace '\bimport\s+src\.', "import $PackageName."
    if ($new -ne $text) {
        # write back UTF8 (no BOM)
        Set-Content -LiteralPath $path -Value $new -Encoding UTF8
        $modified += $path
        Write-Host "Rewrote: $path"
    }
}

if ($modified.Count -eq 0) {
    Write-Log "No files needed replacement (no 'from src.' or 'import src.' found outside excluded directories)."
} else {
    Write-Log "Total files modified: $($modified.Count)"
}

# 6) Show any remaining occurrences of 'from src.' or 'import src.' for manual review
Write-Log "Searching for any remaining 'from src.' or 'import src.' occurrences..."
$leftover = Get-ChildItem -Recurse -Filter *.py | Select-String -Pattern "from\s+src\.|import\s+src\." -List | ForEach-Object { $_.Path } | Sort-Object -Unique
# Filter excluded paths
$leftover = $leftover | Where-Object {
    $p = $_
    $skip = $false
    foreach ($ex in $Excludes) {
        if ($p -like "*$ex*") { $skip = $true; break }
    }
    -not $skip
}
if ($leftover) {
    Write-Host "WARNING: Found remaining occurrences of 'src' imports in files (please inspect manually):" -ForegroundColor Yellow
    $leftover | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Log "No remaining 'src' import occurrences found (outside excluded paths)."
}

# 7) Attempt editable install
Write-Log "Installing package in editable mode (pip install -e .). This may take time..."
# Use pip from current environment
try {
    python -m pip install -e . --no-input
    if ($LASTEXITCODE -ne 0) { throw "pip install returned non-zero exit code" }
} catch {
    Write-Host "ERROR: pip install -e . failed. See pip output above." -ForegroundColor Red
    Write-Host "You can inspect the modified files and revert if needed via git. Exiting."
    exit 2
}

# 8) Run pytest
Write-Log "Running pytest -q ..."
# run pytest and capture exit code
pytest -q
$pytest_exit = $LASTEXITCODE

if ($pytest_exit -eq 0) {
    Write-Log "pytest passed. Proceeding to final commit and push."

    # 9) Final commit and push
    git add -A
    git commit -m "$FinalCommitMsg"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: git commit failed. Please inspect the repo state." -ForegroundColor Red
        exit 3
    }

    Write-Log "Pushing branch to origin (git push -u origin HEAD)..."
    git push -u origin HEAD
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: git push failed. Local commit exists; push manually." -ForegroundColor Yellow
        exit 0
    }

    Write-Host "SUCCESS: conversion completed, tests passed, changes pushed." -ForegroundColor Green
    exit 0
} else {
    Write-Host "pytest failed (exit code $pytest_exit). Not committing final changes." -ForegroundColor Red
    Write-Host "You can inspect files in the modified list above, run pytest locally to diagnose, fix issues, then commit manually." -ForegroundColor Yellow
    # show modified files for convenience
    if ($modified.Count -gt 0) {
        Write-Host "`nModified files (not committed):"
        $modified | ForEach-Object { Write-Host "  $_" }
    }
    exit 4
}
