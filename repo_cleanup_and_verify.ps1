# repo_cleanup_and_verify_safe.ps1
# Safe, linear cleanup + verify script for Windows PowerShell
# Usage: run at repository root (D:\chem_standard) with activated Python env (chem-standard)
# Example: PowerShell -ExecutionPolicy Bypass -File .\repo_cleanup_and_verify_safe.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configuration
$branchName = "infra/convert-to-package"
$shouldPush = $true
$runStaticChecks = $true
$verifyDir = "src\chem_standard\io"

Write-Output "=== repo_cleanup_and_verify_safe.ps1 start ==="

# 0. basic checks
if (-not (Test-Path ".git")) {
    Write-Error "This does not look like a git repository. Please run this from repository root."
    exit 1
}

# print current branch
$curBranch = (& git rev-parse --abbrev-ref HEAD).Trim()
Write-Output "Current git branch: $curBranch"

if ($curBranch -ne $branchName) {
    Write-Output "Switching to branch: $branchName (create if not exists)"
    $exists = (& git branch --list $branchName).Trim()
    if ($exists -ne "") {
        & git checkout $branchName
        if ($LASTEXITCODE -ne 0) { Write-Error "git checkout failed"; exit 1 }
    } else {
        & git checkout -b $branchName
        if ($LASTEXITCODE -ne 0) { Write-Error "git checkout -b failed"; exit 1 }
    }
}

# 1. Untrack generated egg-info directories and backups (keep local copies)
Write-Output "1) Untracking generated egg-info and backup files from git index (local files kept)."

$eggDirs = Get-ChildItem -Path src -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*egg-info*" }
foreach ($d in $eggDirs) {
    $p = $d.FullName
    Write-Output "  git rm --cached --ignore-unmatch `"$p`""
    & git rm -r --cached --ignore-unmatch $p
    # ignore failure
}

if (Test-Path "package_move_backup") {
    Write-Output "  git rm --cached --ignore-unmatch package_move_backup"
    & git rm -r --cached --ignore-unmatch "package_move_backup"
}

# untrack common backups and scripts if present
& git rm --cached --ignore-unmatch "src/chem_standard/__init__.py.bak"
& git rm --cached --ignore-unmatch "convert_to_package.ps1"
& git rm --cached --ignore-unmatch "convert_to_package_fix*.ps1"

# 2. Update .gitignore (append lines if not present)
Write-Output "2) Updating .gitignore"

if (-not (Test-Path ".gitignore")) {
    New-Item -Path .gitignore -ItemType File -Force | Out-Null
}

$gi = Get-Content .gitignore -ErrorAction SilentlyContinue
$entries = @(
    "src/*.egg-info/",
    "package_move_backup/",
    "src/chem_standard/__init__.py.bak",
    "convert_to_package*.ps1"
)

foreach ($line in $entries) {
    if ($gi -notcontains $line) {
        Add-Content -Path .gitignore -Value $line
        Write-Output "  added to .gitignore: $line"
    } else {
        Write-Output "  already in .gitignore: $line"
    }
}

# 3. Add .gitattributes to standardize line endings if not present
Write-Output "3) Ensure .gitattributes exists to normalize line endings"
if (-not (Test-Path ".gitattributes")) {
    $text = "* text=auto`n*.py text eol=lf`n"
    Set-Content -Path .gitattributes -Value $text -Encoding UTF8
    Write-Output "  .gitattributes created"
} else {
    Write-Output "  .gitattributes already exists"
}

# 4. Stage and commit git changes if any
Write-Output "4) Staging and committing .gitignore and .gitattributes and removed-index changes"
& git add .gitignore .gitattributes
& git add -u

# check staged
& git diff --staged --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Output "  creating commit for cleanup changes"
    & git commit -m "chore(pkg): remove generated egg-info and backups; update .gitignore and .gitattributes"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "git commit failed"
        exit 1
    }
    if ($shouldPush) {
        Write-Output "  pushing to origin/$branchName"
        & git push --set-upstream origin $branchName
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "git push returned non-zero. You may need to run 'git push' manually."
        } else {
            Write-Output "  push succeeded"
        }
    }
} else {
    Write-Output "  no staged changes to commit"
}

# 5. pip editable install
Write-Output "5) Installing package editable: python -m pip install -e . --no-input"
& python -m pip install -e . --no-input
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip install -e . failed. Inspect pip output above."
    exit 1
}
Write-Output "  pip install -e succeeded"

# 6. Run pytest
Write-Output "6) Running pytest -q"
& python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "pytest failed. Inspect test output above."
    exit 1
}
Write-Output "  pytest passed"

# 7. Run verify scripts (discover verify_*.py under $verifyDir)
Write-Output "7) Running verify scripts under $verifyDir (if any)"
if (Test-Path $verifyDir) {
    $vf = Get-ChildItem -Path $verifyDir -Filter "verify_*.py" -File -ErrorAction SilentlyContinue
    if ($vf.Count -eq 0) {
        Write-Output "  no verify_*.py found under $verifyDir"
    } else {
        foreach ($file in $vf) {
            $path = $file.FullName
            Write-Output "  Running: python `"$path`""
            & python $path
            if ($LASTEXITCODE -ne 0) {
                Write-Error "verify script failed: $path (exit $LASTEXITCODE)"
                exit 1
            } else {
                Write-Output "  verify passed: $($file.Name)"
            }
        }
    }
} else {
    Write-Output "  verify directory not found: $verifyDir"
}

# 8. Optional static checks: ruff and mypy
if ($runStaticChecks) {
    Write-Output "8) Optional static checks: ruff and mypy (if installed)"
    $ruffCmd = Get-Command ruff -ErrorAction SilentlyContinue
    if ($null -ne $ruffCmd) {
        Write-Output "  running: ruff check src"
        & ruff check src
        if ($LASTEXITCODE -ne 0) { Write-Warning "ruff found issues (non-zero exit)"; }
    } else {
        Write-Output "  ruff not installed, skipping"
    }

    $mypyCmd = Get-Command mypy -ErrorAction SilentlyContinue
    if ($null -ne $mypyCmd) {
        Write-Output "  running: mypy src"
        & mypy src
        if ($LASTEXITCODE -ne 0) { Write-Warning "mypy found issues (non-zero exit)"; }
    } else {
        Write-Output "  mypy not installed, skipping"
    }
}

Write-Output "=== repo_cleanup_and_verify_safe.ps1 finished successfully ==="
exit 0
