# -*- coding: utf-8 -*-
"""
CI / 本地通用同步脚本: 用 staging/ 里的 Steam DLL 重新生成 pattern TOML.

用法:
    python ci_sync.py

流程:
    1. 把仓库里现有的 steamclient/ steamui/ TOML 当作种子
    2. 对 staging/steamclient64.dll、staging/steamui.dll 逐个调用 pattern_updater.py
    3. 生成的 <sha256>.toml 覆盖回 steamclient/ steamui/
"""

import glob
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STAGING = os.path.join(ROOT, "staging")
WORK = os.path.join(ROOT, "_ci")

TARGETS = [
    ("steamclient64.dll", "steamclient"),
    ("steamui.dll", "steamui"),
]


def prepare_workdir():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    shutil.copy2(os.path.join(ROOT, "pattern_updater.py"), WORK)

    # 用仓库里已有的 TOML 当种子
    for _, comp in TARGETS:
        src = os.path.join(ROOT, comp)
        dst = os.path.join(WORK, "pattern_cache", comp)
        os.makedirs(dst, exist_ok=True)
        for f in glob.glob(os.path.join(src, "*.toml")) if os.path.isdir(src) else []:
            shutil.copy2(f, dst)
            print("[seed] %s/%s" % (comp, os.path.basename(f)))


def run_one(dll, comp):
    print("\n=== %s -> %s ===" % (dll, comp))
    r = subprocess.run(
        [sys.executable, "pattern_updater.py",
         "--dll", dll, "--component", comp, "--out_dir", "output"],
        cwd=WORK, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.stdout:
        print(r.stdout.rstrip())
    if r.returncode != 0:
        print("[warn] pattern_updater exit=%d" % r.returncode)
        if r.stderr:
            print("[warn] stderr: %s" % r.stderr.rstrip()[-800:])
        return False

    out_dir = os.path.join(WORK, "output", "pattern", comp)
    files = glob.glob(os.path.join(out_dir, "*.toml"))
    if not files:
        print("[warn] no toml produced for %s" % comp)
        return False

    dst = os.path.join(ROOT, comp)
    os.makedirs(dst, exist_ok=True)
    for f in files:
        shutil.copy2(f, dst)
        print("[+] %s/%s" % (comp, os.path.basename(f)))
    return True


def main():
    prepare_workdir()

    ok = 0
    for dll_name, comp in TARGETS:
        dll = os.path.join(STAGING, dll_name)
        if not os.path.isfile(dll):
            print("[skip] %s not found in staging/" % dll_name)
            continue
        if run_one(dll, comp):
            ok += 1

    print("\n[done] %d/%d component(s) regenerated" % (ok, len(TARGETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
