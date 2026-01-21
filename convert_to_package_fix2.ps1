# convert_to_package_fix2.ps1
# 安全、可重复执行的 package-conversion 脚本（适用于 Windows PowerShell）
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($msg) { Write-Output "[INFO] $msg" }
function ErrorAndExit($msg, $code=1) {
    Write-Error $msg
    exit $code
}

try {
    $root = (Get-Location).Path
    Info "Repository root: $root"

    $backup = Join-Path $root "package_move_backup"
    if (-not (Test-Path $backup)) { New-Item -ItemType Directory -Path $backup | Out-Null }
    Info "backup directory: $backup"

    $pkgDir = Join-Path $root "src\chem_standard"
    if (-not (Test-Path $pkgDir)) { New-Item -ItemType Directory -Path $pkgDir -Force | Out-Null }
    Info "package directory: $pkgDir"

    # top-level files to move (if present under src\)
    $topFiles = @("atom.py","molecule.py","reaction.py","__init__.py")
    foreach ($f in $topFiles) {
        $src = Join-Path $root ("src\" + $f)
        if (Test-Path $src) {
            $dest = Join-Path $pkgDir $f
            if (Test-Path $dest) {
                Info "Target exists; backing up existing $dest -> $backup"
                Copy-Item -Path $dest -Destination (Join-Path $backup ("dest."+ $f + ".bak")) -Force -Recurse -ErrorAction SilentlyContinue
                Remove-Item -Path $dest -Force -Recurse -ErrorAction SilentlyContinue
            }
            Info "Moving $src -> $pkgDir"
            Move-Item -Path $src -Destination $pkgDir -Force
        }
    }

    # subdirectories to move
    $subdirs = @("io","dataset","graph","rules","path","signature","identity","ml")
    foreach ($d in $subdirs) {
        $srcd = Join-Path $root ("src\" + $d)
        if (Test-Path $srcd) {
            $destd = Join-Path $pkgDir $d
            if (Test-Path $destd) {
                Info "Destination directory exists: $destd. Backing up source to $backup and removing source."
                Copy-Item -Path $srcd -Destination (Join-Path $backup ($d + "_src_backup")) -Recurse -Force
                Remove-Item -Path $srcd -Recurse -Force
            }
            Info "Moving directory $srcd -> $pkgDir"
            Move-Item -Path $srcd -Destination $pkgDir -Force
        }
    }

    # move any remaining top-level .py files under src (except package dir and packaging files)
    $items = Get-ChildItem -Path (Join-Path $root "src") -File -ErrorAction SilentlyContinue
    foreach ($it in $items) {
        if ($it.Name -ne "chem_standard" -and $it.Name -ne "setup.cfg" -and $it.Name -ne "pyproject.toml") {
            $srcpath = $it.FullName
            $destpath = Join-Path $pkgDir $it.Name
            if (Test-Path $destpath) {
                Info "Found $($it.Name) but target exists; backup and remove target"
                Copy-Item -Path $destpath -Destination (Join-Path $backup ("dest."+ $it.Name + ".bak")) -Force -Recurse -ErrorAction SilentlyContinue
                Remove-Item -Path $destpath -Force -Recurse -ErrorAction SilentlyContinue
            }
            Info "Moving extra file $srcpath -> $pkgDir"
            Move-Item -Path $srcpath -Destination $pkgDir -Force
        }
    }

    # remove src\__init__.py if still present (we use src/chem_standard/__init__.py)
    $oldInit = Join-Path $root "src\__init__.py"
    if (Test-Path $oldInit) {
        Info "Backing up and removing src\__init__.py"
        Copy-Item -Path $oldInit -Destination (Join-Path $backup "__init__.py.bak") -Force
        Remove-Item -Path $oldInit -Force
    }

    Info "Listing src/chem_standard contents:"
    Get-ChildItem -Path $pkgDir -Recurse | ForEach-Object { Write-Output $_.FullName }

    # editable install: python -m pip install -e .
    Info "Running: python -m pip install -e . --no-input"
    $proc = Start-Process -FilePath python -ArgumentList "-m pip install -e . --no-input" -NoNewWindow -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        ErrorAndExit "pip install -e . failed with exit code $($proc.ExitCode). See pip output above."
    }
    Info "pip install -e . completed successfully."

    # run pytest -q
    Info "Running pytest -q (smoke test)"
    $proc2 = Start-Process -FilePath python -ArgumentList "-m pytest -q" -NoNewWindow -Wait -PassThru
    if ($proc2.ExitCode -ne 0) {
        ErrorAndExit "pytest failed with exit code $($proc2.ExitCode). Please check test output and fix before committing."
    }
    Info "pytest passed."

    # git add & commit (only if there are staged changes)
    Info "Staging changes: git add -A"
    Start-Process -FilePath git -ArgumentList "add -A" -NoNewWindow -Wait -PassThru | Out-Null

    # check if there is anything staged
    $diff = Start-Process -FilePath git -ArgumentList "diff --staged --quiet" -NoNewWindow -Wait -PassThru
    if ($LASTEXITCODE -ne 0) {
        Info "Creating commit for package layout changes"
        Start-Process -FilePath git -ArgumentList "commit -m `"chore(pkg): move modules into src/chem_standard package layout`"" -NoNewWindow -Wait -PassThru | Out-Null
        Start-Process -FilePath git -ArgumentList "push" -NoNewWindow -Wait -PassThru | Out-Null
        Info "Commit & push attempted."
    } else {
        Info "No staged changes to commit."
    }

    Info "DONE: package layout move, editable install and pytest succeeded."
    exit 0
}
catch {
    Write-Error "Exception: $($_.Exception.Message)"
    Write-Output "Backups are in: $backup"
    exit 1
}
