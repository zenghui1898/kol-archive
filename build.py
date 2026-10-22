#!/usr/bin/env python3
"""KOL 档案库生成器：扫描每个含 meta.json 的子目录，生成 <slug>/index.html 与根 index.html。
新增 KOL：建文件夹 <slug>/，放 meta.json、docs/*.md、images/avatar.jpg、可选 data/tweets.json，然后 python3 build.py。"""
import json, re, html, pathlib, datetime
ROOT = pathlib.Path(__file__).parent
TZ = datetime.timezone(datetime.timedelta(hours=8))
esc = lambda s: html.escape(str(s))

def inline(s):
    s = esc(s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f'<img alt="{m[1]}" src="{m[2] if m[2].startswith("http") else "images/"+m[2].split("/")[-1]}">', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2" target="_blank">\1</a>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    return s

def md(text):
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        l = lines[i]
        if m := re.match(r'(#{1,6})\s+(.*)', l):
            n = min(len(m[1]) + 1, 6); out.append(f'<h{n}>{inline(m[2])}</h{n}>')
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells): rows.append(cells)
                i += 1
            t = '<div class="tbl"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>'
            t += ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rows[1:])
            out.append(t + '</tbody></table></div>'); continue
        elif re.match(r'\s*[-*]\s+', l):
            items = []
            while i < len(lines) and re.match(r'\s*[-*]\s+', lines[i]):
                items.append(re.sub(r'\s*[-*]\s+', '', lines[i], count=1)); i += 1
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>'); continue
        elif l.strip():
            out.append(f'<p>{inline(l)}</p>')
        i += 1
    return '\n'.join(out)

CSS = """:root{--bg:#FAF8F3;--bg2:#F3EFE4;--card:#FFF;--card2:#FBF9F5;--bd:#EAE2D2;--bdl:#F2ECE0;--tx:#1F1B16;--sub:#544D42;--mut:#887E6E;--amber:#B45309;--amberh:#92400E;--amberl:#FEF3C7;--gold:#D97706;--green:#15803D;--red:#B91C1C;
--sans:"Plus Jakarta Sans",-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;--serif:"Noto Serif SC","Cinzel",Georgia,serif}
*{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--tx);font-family:var(--sans);line-height:1.8}
a{color:var(--amber)}.banner{background:linear-gradient(90deg,#92400E,#B45309,#D97706);color:#fff;text-align:center;padding:8px;font-size:13px}
.wrap{max-width:1120px;margin:0 auto;padding:32px 20px}h1,h2,h3{font-family:var(--serif)}
.hero{text-align:center;padding:40px 0 24px}.hero h1{font-size:40px}.hero p{color:var(--sub)}
.stats{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin:20px 0 36px}.stat{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px 26px;text-align:center}
.stat b{display:block;font-size:26px;color:var(--amber);font-family:var(--serif)}.stat span{font-size:13px;color:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:22px;text-decoration:none;color:inherit;box-shadow:0 4px 20px rgba(31,27,22,.05);transition:.2s}
.card:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(180,83,9,.12);border-color:var(--amber)}
.card img,.avatar{width:64px;height:64px;border-radius:50%;border:2px solid var(--amberl)}.card h3{margin:10px 0 2px}.mut{color:var(--mut);font-size:13px}
.badge{display:inline-block;font-size:12px;padding:2px 10px;border-radius:99px;margin:6px 6px 0 0;background:var(--amberl);color:var(--amberh)}.badge.no{background:#FEE2E2;color:var(--red)}.badge.tag{background:var(--bg2);color:var(--sub)}
.sec{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:26px;margin:20px 0}.sec>h2{font-size:22px;border-left:4px solid var(--amber);padding-left:12px;margin-bottom:14px}
.sec ul{padding-left:20px}.two{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:700px){.two{grid-template-columns:1fr}}
.pro h3{color:var(--green)}.con h3{color:var(--red)}code{background:var(--bg2);padding:1px 6px;border-radius:4px;font-size:.9em;word-break:break-all}
.case{background:var(--card2);border:1px solid var(--bdl);border-radius:12px;padding:14px 18px;margin:10px 0}
.md h2,.md h3,.md h4{margin:18px 0 8px}.md p,.md ul{margin:6px 0}.md img{max-width:100%}.tbl{overflow-x:auto}table{border-collapse:collapse;margin:10px 0;font-size:14px}th,td{border:1px solid var(--bd);padding:5px 9px}th{background:var(--bg2)}
details{margin:12px 0}summary{cursor:pointer;font-weight:600;color:var(--amberh)}
.tw{border-bottom:1px dashed var(--bd);padding:12px 0}.tw p{white-space:pre-wrap}.nav{margin-bottom:10px}
footer{text-align:center;color:var(--mut);font-size:13px;padding:30px}"""
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@400;600&family=Noto+Serif+SC:wght@500;700;900&display=swap" rel="stylesheet">'

def page(title, body, css_path):
    return f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>{FONTS}<link rel="stylesheet" href="{css_path}"></head><body><div class="banner">KOL 档案馆 · 仅作研究记录，不构成任何投资建议</div>{body}<footer>由 build.py 生成 · {datetime.datetime.now(TZ):%Y-%m-%d %H:%M}（北京时间）</footer></body></html>'

def badges(m):
    return f'<span class="badge">{esc(m.get("status",""))}</span><span class="badge no">{esc(m.get("recommend",""))}</span>' + ''.join(f'<span class="badge tag">{esc(t)}</span>' for t in m.get('tags', []))

ul = lambda xs: '<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in xs) + '</ul>' if xs else '<p class="mut">数据缺失</p>'

def tweets_html(d):
    f = d / 'data' / 'tweets.json'
    if not f.exists(): return [], '<p class="mut">暂无推文数据</p>'
    tw = sorted(json.loads(f.read_text()).get('data', []), key=lambda t: t['created_at'], reverse=True)
    out = []
    for t in tw:
        ts = datetime.datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')).astimezone(TZ)
        pm = t.get('public_metrics', {}); kind = ','.join(r['type'] for r in t.get('referenced_tweets', [])) or 'original'
        out.append(f'<div class="tw"><div class="mut">{ts:%Y-%m-%d %H:%M} 北京时间 · {kind} · ❤ {pm.get("like_count",0)} · 👁 {pm.get("impression_count",0)} · <a href="https://x.com/i/status/{t["id"]}" target="_blank">原帖</a></div><p>{esc(t["text"])}</p></div>')
    return tw, ''.join(out)

def build_kol(d, m):
    tw, tl = tweets_html(d)
    docs = ''.join(f'<details{" open" if i == 0 else ""}><summary>{esc(n)}</summary><div class="md">{md((d/"docs"/n).read_text())}</div></details>'
                   for i, n in enumerate(m.get('docs', [])) if (d/'docs'/n).exists())
    wal = ''.join(f'<p><b>{esc(w["chain"])}</b> <code>{esc(w["address"])}</code><br><span class="mut">{esc(w.get("note",""))}</span></p>' for w in m.get('wallets', [])) or '<p class="mut">数据缺失</p>'
    cases = ''.join(f'<div class="case"><b>{esc(c["title"])}</b> <span class="mut">{esc(c.get("date",""))}</span><p>{inline(c["body"])}</p></div>' for c in m.get('cases', []))
    body = f'''<div class="wrap"><div class="nav"><a href="../index.html">← 返回档案墙</a></div>
<div class="sec" style="display:flex;gap:20px;align-items:center"><img class="avatar" style="width:96px;height:96px" src="images/avatar.jpg" alt=""><div><h1>{esc(m["name"])}</h1><a href="https://x.com/{esc(m["handle"])}" target="_blank">@{esc(m["handle"])}</a><div>{badges(m)}</div></div></div>
<div class="sec"><h2>简介 / 身份</h2><p>{inline(m.get("bio",""))}</p>{ul(m.get("identity",[]))}</div>
<div class="sec"><h2>主要打法</h2>{ul(m.get("playbook",[]))}</div>
<div class="sec two"><div class="pro"><h3>优势</h3>{ul(m.get("strengths",[]))}</div><div class="con"><h3>劣势</h3>{ul(m.get("weaknesses",[]))}</div></div>
<div class="sec"><h2>钱包</h2>{wal}</div>
<div class="sec"><h2>核心案例</h2>{cases or '<p class="mut">数据缺失</p>'}</div>
<div class="sec"><h2>分析报告</h2>{docs or '<p class="mut">暂无</p>'}</div>
<div class="sec"><h2>推文时间线 <span class="mut">（{len(tw)} 条）</span></h2>{tl}</div></div>'''
    (d / 'index.html').write_text(page(f'{m["name"]} · KOL 档案', body, '../style.css'))
    return len(tw)

def main():
    (ROOT / 'style.css').write_text(CSS)
    kols = []
    for mf in sorted(ROOT.glob('*/meta.json')):
        m = json.loads(mf.read_text()); m['_tw'] = build_kol(mf.parent, m); m['_slug'] = mf.parent.name; kols.append(m)
    cards = ''.join(f'<a class="card" href="{m["_slug"]}/index.html"><img src="{m["_slug"]}/images/avatar.jpg" alt=""><h3>{esc(m["name"])}</h3><div class="mut">@{esc(m["handle"])} · 粉丝 {m.get("followers","?"):,}</div><div>{badges(m)}</div></a>' for m in kols)
    stats = [(len(kols), '收录 KOL'), (sum(m['_tw'] for m in kols), '归档推文'), (sum(len(m.get('docs', [])) for m in kols), '分析报告'), (sum(len(m.get('wallets', [])) for m in kols), '跟踪钱包')]
    body = '<div class="wrap"><div class="hero"><h1>KOL 档案馆</h1><p>链上 KOL 研究记录 · 身份、打法、钱包与推文归档</p></div><div class="stats">' + ''.join(f'<div class="stat"><b>{v}</b><span>{k}</span></div>' for v, k in stats) + f'</div><div class="grid">{cards}</div></div>'
    (ROOT / 'index.html').write_text(page('KOL 档案馆', body, 'style.css'))
    print(f'built {len(kols)} KOL(s)')

if __name__ == '__main__': main()
