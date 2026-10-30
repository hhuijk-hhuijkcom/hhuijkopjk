# 手动更新 Steam DLL 的两种方式

## 方式 1 (推荐)：GitHub Release

Steam 更新后, 你只需要把新 DLL 传上来, 剩下的 workflow 自动跑:

1. Fork → 左侧 **Releases** → **Draft a new release**
2. Tag: `v<Steam版本号或日期>`, 比如 `v20261030`
3. 把这些文件拖进去:
   - `steamclient64.dll` (Steam 安装目录里的)
   - `steamui.dll`      (Steam 安装目录 steamui/ 子目录里的)
4. 点 **Publish release**
5. 回到 Actions tab, `Sync Steam Pattern TOMLs` 会自动触发 (或手动 **Run workflow**)
6. Bot 生成新 TOML → commit → push → OpenSteamTool.dll 下次启动自动拉

## 方式 2 (省事但 DLL 进 git): staging/ 目录

```bash
# Steam 更新后, 直接把 DLL 拷进 fork
cp "C:\steam\steamclient64.dll" staging/
cp "C:\steam\steamui\steamui.dll"   staging/
git add staging/
git commit -m "staging: Steam update $(date)"
git push
```

push 到 main 后 workflow 也会自动触发 (workflow 里有 `push paths: staging/**`)。

## 说明

- **steamclient.dll (32位)** 也会被尝试下载, 但 OpenSteamTool 只 hook 64 位版, 建议只传 64 位 DLL.
- 第一次跑需要先有 **上游 steam-monitor 仓库对应的旧 TOML** 当 seed. 你的 fork 第一次可以手动从 steam-monitor 抄几个 TOML 当种子.
- Bot 每次先尝试从 upstream steam-monitor 抄最新 TOML, 抄不到才走 sig 自匹配.
