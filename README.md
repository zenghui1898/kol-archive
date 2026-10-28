# KOL 档案馆

中文 meme KOL 档案站。线上地址：<https://zenghui1898.github.io/kol-archive/>

根目录 `index.html` 是门户本身：一个哈希路由的静态页（`#home`、`#<slug>`、`#compare`、`#download`），打开后读取 `data/kols.json` 和 `data/<slug>.json`。这个文件要保留，不要用生成器覆盖。

推送到 `main` 后，GitHub Actions 会把仓库根目录部署到 GitHub Pages。

## 如何新增一位 KOL

1. 在 `data/` 放入四份文件：`<slug>.json`、`<slug>_models.json`、`<slug>_articles.json`、`<slug>_tweets.csv`。字段名跟现有档案一致。门户已经接受两套写法：徽章用 `v`/`k` 或 `value`/`label`，推文用定长数组或 `{i,t,k,x,...}` 对象，思维模型用 `lec` 或 `lectures`、`quote` 对象或字符串，长文用 `text` 或 `body`/`excerpt`。
2. 只在 `data/kols.json` 追加这一位的目录项，不要改其他 KOL 已有字段。
3. 在仓库根目录运行：

```bash
python3 build.py
```

脚本校验门户和数据是否能被页面加载，并保持 `index.html` 原样。

`python3 build.py --legacy` 仍会按各子目录的 `meta.json` 重建旧版 `<slug>/index.html` 和 `style.css`（目前只有 `0xaa/`）。它不会再写根目录 `index.html`。以前默认构建会把那份约 1.4KB 的卡片墙写到根 `index.html` 上，哈希路由门户会被换掉。
