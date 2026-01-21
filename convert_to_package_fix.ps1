# convert_to_package_fix.ps1
# 修正版：将 src/* 移入 src/chem_standard，并做 editable install + pytest smoke test
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Run-Command($cmd) {
    Write-Output "-> Running: $cmd"
    & cmd /c $cmd
    return $LASTEXITCODE
}

try {
    $root = (Get-Location).Path
    Write-Output "[INFO] Repository root: $root"

    $backup = Join-Path $root "package_move_backup"
    if (-not (Test-Path $backup)) { New-Item -ItemType Directory -Path $backup | Out-Null }
    Write-Output "[INFO] backup -> $backup"

    $pkgDir = Join-Path $root "src\chem_standard"
    if (-not (Test-Path $pkgDir)) { New-Item -ItemType Directory -Path $pkgDir -Force | Out-Null }
    Write-Output "[INFO] package dir: $pkgDir"

    $topFiles = @("atom.py","molecule.py","reaction.py","__init__.py")
    foreach ($f in $topFiles) {
        $src = Join-Path $root ("src\" + $f)
        if (Test-Path $src) {
            $dest = Join-Path $pkgDir $f
            if (Test-Path $dest) {
                Write-Output "[INFO] 目标已存在, 备份目标: $dest -> $backup"
                Copy-Item $dest (Join-Path $backup ("dest."+ $f + ".bak")) -Force -Recurse -ErrorAction SilentlyContinue
                Remove-Item $dest -Force -Recurse -ErrorAction SilentlyContinue
            }
            Write-Output "[INFO] 移动 $src -> $pkgDir"
            Move-Item -Path $src -Destination $pkgDir -Force
        }
    }

    $subdirs = @("io","dataset","graph","rules","path","signature","identity","ml")
    foreach ($d in $subdirs) {
        $srcd = Join-Path $root ("src\" + $d)
        if (Test-Path $srcd) {
            $destd = Join-Path $pkgDir $d
            if (Test-Path $destd) {
                Write-Output "[INFO] 目标目录已存在: $destd. 备份源目录到 $backup"
                Copy-Item $srcd (Join-Path $backup ($d + "_src_backup")) -Recurse -Force
                Remove-Item $srcd -Recurse -Force
            }
            Write-Output "[INFO] 移动目录 $srcd -> $pkgDir"
            Move-Item -Path $srcd -Destination $pkgDir -Force
        }
    }

    # 移动 src 根下的其它 .py（避免遗漏）
    Get-ChildItem -Path (Join-Path $root "src") -File -Exclude "chem_standard" | ForEach-Object {
        $fname = $_.Name
        if ($fname -ne "setup.cfg" -and $fname -ne "pyproject.toml") {
            $srcpath = $_.FullName
            $destpath = Join-Path $pkgDir $fname
            if (Test-Path $destpath) {
                Write-Output "[INFO] 发现 $fname 但目标已存在 -> 备份并删除目标"
                Copy-Item $destpath (Join-Path $backup ("dest."+ $fname + ".bak")) -Force -Recurse -ErrorAction SilentlyContinue
                Remove-Item $destpath -Force -Recurse -ErrorAction SilentlyContinue
            }
            Write-Output "[INFO] 移动额外文件 $srcpath -> $pkgDir"
            Move-Item -Path $srcpath -Destination $pkgDir -Force
        }
    }

    $oldInit = Join-Path $root "src\__init__.py"
    if (Test-Path $oldInit) {
        Write-Output "[INFO] 备份并移除 src\__init__.py"
        Copy-Item $oldInit (Join-Path $backup "__init__.py.bak") -Force
        Remove-Item $oldInit -Force
    }

    Write-Output "`n[INFO] 列出 src/chem_standard 内容："
    Get-ChildItem -Path $pkgDir -Recurse | ForEach-Object { Write-Output $_.FullName }

    Write-Output "`n[STEP] pip editable install ..."
    $ret = Run-Command "python -m pip install -e . --no-input"
    if ($ret -ne 0) {
        Write-Error "[ERROR] pip install -e . 失败 (exit code $ret). 请检查输出并修正后重试。"
        exit $ret
    }

    Write-Output "`n[STEP] 运行 pytest -q (smoke test)"
    $ret = Run-Command "python -m pytest -q"
    if ($ret -ne 0) {
        Write-Error "[ERROR] pytest 未全部通过 (exit code $ret). 请检查测试输出。"
        exit $ret
    }

    Write-Output "`n[STEP] pytest 通过，准备 git commit & push"
    # add & commit (仅当有变动时)
    Run-Command "git add -A"
    $ret = Run-Command "git diff --staged --quiet"
    if ($LASTEXITCODE -ne 0) {
        # 有 staged 变更
        Run-Command "git commit -m ""chore(pkg): move modules into src/chem_standard package layout"""
        Run-Command "git push"
    } else {
        Write-Output "[INFO] 无需提交：没有 staged 变更。"
    }

    Write-Output "`n==== 完成：已将 src 移入 src/chem_standard 并执行 reinstall & pytest。 ===="
    exit 0
}
catch {
    Write-Error "[EXCEPTION] 脚本执行出错： $($_.Exception.Message)"
    Write-Output "[INFO] 已把备份放到: $backup"
    Write-Output "[INFO] 请把上面的错误输出完整粘回给我，我会继续帮助修正。"
    exit 1
}
