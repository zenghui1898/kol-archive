# KOL 档案馆

中文 meme KOL 档案站，结构参照 [suoha888/Trader-Archives](https://github.com/suoha888/Trader-Archives)。每个 KOL 一份静态档案，记录身份、打法、钱包、分析报告和推文。页面由仓库根目录的 `build.py` 生成，只使用 Python 标准库。

线上地址：<https://zenghui1898.github.io/kol-archive/>

## 如何新增一位 KOL

1. 在仓库根目录放入 `<slug>/` 文件夹，其中包含：
   - `<slug>/meta.json`
   - `<slug>/docs/` 下的 Markdown 报告（文件名写进 `meta.json` 的 `docs` 字段）
   - `<slug>/images/`（至少包含 `avatar.jpg`，报告配图也放这里）
2. 可选：`<slug>/data/tweets.json`
3. 在仓库根目录运行：

```bash
python3 build.py
```

脚本会重新生成根目录的 `index.html`、`style.css`，以及 `<slug>/index.html`。样式、页面和图片都使用相对路径，因此在 GitHub Pages 的 `/kol-archive/` 子路径下可以正常打开。
