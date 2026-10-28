#!/usr/bin/env python3
"""KOL 档案库工具。

线上门户是根目录 index.html：哈希路由（#home、#<slug>），运行时读取
data/kols.json 与 data/<slug>.json。默认 `python3 build.py` 只校验这些数据，
不改写 index.html。

根因（不要再写回去）：main() 曾经无条件把「扫描 */meta.json 生成的卡片墙」
写入根 index.html。仓库里只有 0xaa/meta.json，产物约 1.4KB，会盖掉约 17KB 的
真门户，#0xaa / #efo / #bokaiixu 等路由全部失效。`--legacy` 仍会按 meta.json
重建旧版 <slug>/index.html 与 style.css，但根 index.html 一律不动。

新增门户档案：把 <slug>.json、_models.json、_articles.json、_tweets.csv 放进
data/，在 data/kols.json 追加一条，再运行 python3 build.py。
"""
import json, re, html, pathlib, datetime, sys
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
.twbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:10px 0 14px;padding:10px 14px;background:var(--card2);border:1px solid var(--bdl);border-radius:12px}
.twbar input[type=search]{flex:1;min-width:200px;padding:7px 12px;border:1px solid var(--bd);border-radius:99px;font:inherit;background:#fff}
.twbar label{font-size:14px;color:var(--sub);cursor:pointer}.twbar button{font:inherit;font-size:13px;padding:4px 12px;border:1px solid var(--bd);border-radius:99px;background:#fff;color:var(--amberh);cursor:pointer}
.twbar button:hover{border-color:var(--amber)}details.mon{border-top:1px solid var(--bdl);padding:6px 0;margin:0}details.mon>summary{font-family:var(--serif);font-size:17px;padding:4px 0}
.kd{padding:0 7px;border-radius:99px;font-size:12px}.kd-orig{background:var(--amberl);color:var(--amberh)}.kd-reply{background:var(--bg2);color:var(--sub)}.kd-rt{background:#DCFCE7;color:var(--green)}
.wrap.wide{max-width:1240px}.hbwrap{display:grid;grid-template-columns:230px 1fr;gap:22px}.toc{position:sticky;top:12px;align-self:start;max-height:94vh;overflow:auto;font-size:13px;background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:12px}.toc a{display:block;text-decoration:none;padding:2px 0}.toc .tv{font-weight:600;margin-top:6px}.toc .tt{color:var(--sub);padding-left:8px}
.vk{font-family:var(--serif);color:var(--gold);font-size:13px;letter-spacing:2px}.topic{border-top:1px solid var(--bdl);padding:14px 0}.topic h4{font-size:14px;color:var(--amberh);margin:8px 0 4px}.topic ul{padding-left:20px}.rf{font-size:12px;text-decoration:none}
blockquote.q{border-left:3px solid var(--amber);background:var(--card2);padding:8px 12px;margin:8px 0}blockquote.q p{white-space:pre-wrap}
.brow{display:grid;grid-template-columns:50px 1fr 50px;gap:8px;align-items:center;margin:4px 0}.bar{display:flex;height:16px;border-radius:4px;overflow:hidden;background:var(--bg2)}.bar span{display:block;height:100%}.leg{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;margin-top:8px}.leg i{display:inline-block;width:10px;height:10px;margin-right:4px;border-radius:2px}
#twd{font:inherit;font-size:13px;padding:4px 8px;border:1px solid var(--bd);border-radius:99px}
@media(max-width:860px){.hbwrap{grid-template-columns:1fr}.toc{position:static;max-height:none}}
footer{text-align:center;color:var(--mut);font-size:13px;padding:30px}"""
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@400;600&family=Noto+Serif+SC:wght@500;700;900&display=swap" rel="stylesheet">'

def page(title, body, css_path):
    return f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>{FONTS}<link rel="stylesheet" href="{css_path}"></head><body><div class="banner">KOL 档案馆 · 仅作研究记录，不构成任何投资建议</div>{body}<footer>由 build.py 生成 · {datetime.datetime.now(TZ):%Y-%m-%d %H:%M}（北京时间）</footer></body></html>'

def badges(m):
    return f'<span class="badge">{esc(m.get("status",""))}</span><span class="badge no">{esc(m.get("recommend",""))}</span>' + ''.join(f'<span class="badge tag">{esc(t)}</span>' for t in m.get('tags', []))

ul = lambda xs: '<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in xs) + '</ul>' if xs else '<p class="mut">数据缺失</p>'

def load_tweets(d):
    """优先读取 data/tweets_all.json（完整归档），否则回退 data/tweets.json。"""
    for name in ('tweets_all.json', 'tweets.json'):
        f = d / 'data' / name
        if f.exists():
            return name, sorted(json.loads(f.read_text()).get('data', []), key=lambda t: t['created_at'], reverse=True)
    return None, []

def kind_of(t):
    ty = {r['type'] for r in t.get('referenced_tweets', [])}
    if t.get('is_retweet') or 'retweeted' in ty: return 'rt'
    if t.get('is_reply') or 'replied_to' in ty or t.get('in_reply_to_user_id'): return 'reply'
    return 'orig'

def tweets_html(d):
    name, tw = load_tweets(d)
    if not tw: return [], '<p class="mut">暂无推文数据</p>'
    months = {}
    for t in tw:
        ts = datetime.datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')).astimezone(TZ)
        months.setdefault(f'{ts:%Y-%m}', []).append(t)
    cnt = {k: sum(1 for t in tw if kind_of(t) == k) for k in ('orig', 'reply', 'rt')}
    first = datetime.datetime.fromisoformat(tw[-1]['created_at'].replace('Z', '+00:00')).astimezone(TZ)
    last = datetime.datetime.fromisoformat(tw[0]['created_at'].replace('Z', '+00:00')).astimezone(TZ)
    head = (f'<p class="mut">覆盖 {first:%Y-%m-%d} ~ {last:%Y-%m-%d}（北京时间）· 原创 {cnt["orig"]} · 回复 {cnt["reply"]} · 转推 {cnt["rt"]} · 按月折叠，最新在前</p>'
            '<div class="twbar"><input id="twq" type="search" placeholder="关键词搜索推文…">'
            '<label><input type="checkbox" class="twk" value="orig" checked> 原创</label>'
            '<label><input type="checkbox" class="twk" value="reply" checked> 回复</label>'
            '<label><input type="checkbox" class="twk" value="rt" checked> 转推</label>'
            '<select id="twd"><option value="">全部领域</option><option value="01">Solidity/开发教育</option><option value="02">安全/救援</option><option value="03">Meme 实战</option><option value="04">AI/Agent</option><option value="05">交易所/行业</option><option value="06">抽奖/活动</option><option value="07">日常/回复</option></select>'
            '<button type="button" id="twexp">全部展开</button><button type="button" id="twcol">全部折叠</button>'
            '<span id="twn" class="mut"></span></div>')
    body = [f'<div id="tl" data-src="data/{name}">']
    for i, (mk, items) in enumerate(months.items()):
        body.append(f'<details class="mon" data-m="{mk}"{" open" if i == 0 else ""}><summary>{mk} <span class="mut mc">（{len(items)} 条）</span></summary><div class="mbody">')
        if i == 0: body.append(''.join(tw_item(t) for t in items))
        body.append('</div></details>')
    body.append('</div>')
    return tw, head + ''.join(body) + TL_JS

def tw_item(t):
    ts = datetime.datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')).astimezone(TZ)
    pm = t.get('public_metrics', {}); k = kind_of(t); lab = {'orig': '原创', 'reply': '回复', 'rt': '转推'}[k]
    q = ' · 引用' if t.get('is_quote') or any(r['type'] == 'quoted' for r in t.get('referenced_tweets', [])) else ''
    return (f'<div class="tw" data-k="{k}"><div class="mut">{ts:%Y-%m-%d %H:%M} 北京时间 · <span class="kd kd-{k}">{lab}</span>{q} · ❤ {pm.get("like_count",0)} · 🔁 {pm.get("retweet_count",0)} · 👁 {pm.get("impression_count",0)} · '
            f'<a href="https://x.com/i/status/{t["id"]}" target="_blank">原帖</a></div><p>{esc(t["text"])}</p></div>')

# 客户端：读取 data JSON，按月懒渲染，支持类型筛选与关键词搜索
TL_JS = """<script>
(function(){
const tl=document.getElementById('tl');if(!tl)return;
const KL={orig:'原创',reply:'回复',rt:'转推'};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const bj=iso=>{const d=new Date(new Date(iso).getTime()+8*3600e3);return d.toISOString().slice(0,16).replace('T',' ');};
const kind=t=>{const ty=(t.referenced_tweets||[]).map(r=>r.type);if(t.is_retweet||ty.includes('retweeted'))return'rt';if(t.is_reply||ty.includes('replied_to')||t.in_reply_to_user_id)return'reply';return'orig';};
let byM={},data=[];
const item=t=>{const k=t._k,pm=t.public_metrics||{},q=(t.is_quote||(t.referenced_tweets||[]).some(r=>r.type==='quoted'))?' · 引用':'';
 return `<div class="tw" data-k="${k}"><div class="mut">${bj(t.created_at)} 北京时间 · <span class="kd kd-${k}">${KL[k]}</span>${q} · ❤ ${pm.like_count||0} · 🔁 ${pm.retweet_count||0} · 👁 ${pm.impression_count||0} · <a href="https://x.com/i/status/${t.id}" target="_blank">原帖</a></div><p>${esc(t.text)}</p></div>`;};
const DM={};const state=()=>({d:(document.getElementById('twd')||{}).value||'',q:document.getElementById('twq').value.trim().toLowerCase(),ks:[...document.querySelectorAll('.twk:checked')].map(x=>x.value)});
const match=(t,s)=>s.ks.includes(t._k)&&(!s.d||DM[t.id]===s.d)&&(!s.q||t._l.includes(s.q));
function render(det){const s=state(),m=det.dataset.m,list=(byM[m]||[]).filter(t=>match(t,s));
 det.querySelector('.mbody').innerHTML=list.length?list.map(item).join(''):'<p class="mut">（无匹配）</p>';det._r=1;}
function apply(){const s=state();let n=0;
 tl.querySelectorAll('details.mon').forEach(det=>{const c=(byM[det.dataset.m]||[]).filter(t=>match(t,s)).length;n+=c;
  det.querySelector('.mc').textContent=`（${c} 条）`;det.style.display=c?'':'none';det._r=0;
  if(s.q&&c&&!det.open)det.open=true;if(det.open)render(det);});
 document.getElementById('twn').textContent=`匹配 ${n} / ${data.length} 条`;}
fetch('data/domain_map.json').then(r=>r.ok?r.json():{}).catch(()=>({})).then(m=>Object.assign(DM,m)).then(()=>fetch(tl.dataset.src)).then(r=>r.json()).then(j=>{data=j.data||[];data.sort((a,b)=>a.created_at<b.created_at?1:-1);
 data.forEach(t=>{t._k=kind(t);t._l=(t.text||'').toLowerCase();const m=bj(t.created_at).slice(0,7);(byM[m]=byM[m]||[]).push(t);});
 tl.querySelectorAll('details.mon').forEach(det=>det.addEventListener('toggle',()=>{if(det.open&&!det._r)render(det);}));
 let tm;document.getElementById('twq').addEventListener('input',()=>{clearTimeout(tm);tm=setTimeout(apply,200);});
 document.querySelectorAll('.twk').forEach(x=>x.addEventListener('change',apply));const sd=document.getElementById('twd');if(sd)sd.addEventListener('change',apply);
 document.getElementById('twexp').onclick=()=>tl.querySelectorAll('details.mon').forEach(d=>{if(d.style.display!=='none')d.open=true;});
 document.getElementById('twcol').onclick=()=>tl.querySelectorAll('details.mon').forEach(d=>d.open=false);
 apply();}).catch(e=>{document.getElementById('twn').textContent='推文数据加载失败（请通过 http 访问）：'+e;});
})();
</script>"""

def build_kol(d, m):
    tw, tl = tweets_html(d)
    toc, hb, nref = '', '', 0
    if m.get('handbook'):
        import sys; sys.path.insert(0, str(ROOT / 'tools')); import build_handbook
        toc, hb, nref = build_handbook.render(d)
    docs = ''.join(f'<details{" open" if i == 0 else ""}><summary>{esc(n)}</summary><div class="md">{md((d/"docs"/n).read_text())}</div></details>'
                   for i, n in enumerate(m.get('docs', [])) if (d/'docs'/n).exists())
    wal = ''.join(f'<p><b>{esc(w["chain"])}</b> <code>{esc(w["address"])}</code><br><span class="mut">{esc(w.get("note",""))}</span></p>' for w in m.get('wallets', [])) or '<p class="mut">数据缺失</p>'
    cases = ''.join(f'<div class="case"><b>{esc(c["title"])}</b> <span class="mut">{esc(c.get("date",""))}</span><p>{inline(c["body"])}</p></div>' for c in m.get('cases', []))
    body = f'''<div class="wrap{' wide' if m.get('handbook') else ''}"><div class="nav"><a href="../index.html">← 返回档案墙</a></div>
<div class="sec" style="display:flex;gap:20px;align-items:center"><img class="avatar" style="width:96px;height:96px" src="images/avatar.jpg" alt=""><div><h1>{esc(m["name"])}</h1><a href="https://x.com/{esc(m["handle"])}" target="_blank">@{esc(m["handle"])}</a><div>{badges(m)}</div></div></div>
{hb}
<div class="sec" id="cases"><h2>链上档案摘要（原版保留）</h2></div>
<div class="sec"><h2>简介 / 身份</h2><p>{inline(m.get("bio",""))}</p>{ul(m.get("identity",[]))}</div>
<div class="sec"><h2>主要打法</h2>{ul(m.get("playbook",[]))}</div>
<div class="sec two"><div class="pro"><h3>优势</h3>{ul(m.get("strengths",[]))}</div><div class="con"><h3>劣势</h3>{ul(m.get("weaknesses",[]))}</div></div>
<div class="sec"><h2>钱包</h2>{wal}</div>
<div class="sec"><h2>核心案例</h2>{cases or '<p class="mut">数据缺失</p>'}</div>
<div class="sec"><h2>分析报告</h2>{docs or '<p class="mut">暂无</p>'}</div>
<div class="sec" id="timeline"><h2>推文时间线 <span class="mut">（{len(tw)} 条）</span></h2>{tl}</div></div>'''
    if toc: body = f'<div class="hbwrap"><aside class="toc"><b>目录</b>{toc}</aside><main>{body}</main></div>'

    (d / 'index.html').write_text(page(f'{m["name"]} · KOL 档案', body, '../style.css'))
    return len(tw)

def legacy_card_wall(kols):
    """旧版首页 HTML。只供对照，禁止写入根 index.html。"""
    cards = ''.join(f'<a class="card" href="{m["_slug"]}/index.html"><img src="{m["_slug"]}/images/avatar.jpg" alt=""><h3>{esc(m["name"])}</h3><div class="mut">@{esc(m["handle"])} · 粉丝 {m.get("followers","?"):,}</div><div>{badges(m)}</div></a>' for m in kols)
    stats = [(len(kols), '收录 KOL'), (sum(m['_tw'] for m in kols), '归档推文'), (sum(len(m.get('docs', [])) for m in kols), '分析报告'), (sum(len(m.get('wallets', [])) for m in kols), '跟踪钱包')]
    body = '<div class="wrap"><div class="hero"><h1>KOL 档案馆</h1><p>链上 KOL 研究记录 · 身份、打法、钱包与推文归档</p></div><div class="stats">' + ''.join(f'<div class="stat"><b>{v}</b><span>{k}</span></div>' for v, k in stats) + f'</div><div class="grid">{cards}</div></div>'
    return page('KOL 档案馆', body, 'style.css')

def build_legacy():
    """按 */meta.json 重建旧版子站。不碰根目录门户。"""
    (ROOT / 'style.css').write_text(CSS)
    kols = []
    for mf in sorted(ROOT.glob('*/meta.json')):
        m = json.loads(mf.read_text()); m['_tw'] = build_kol(mf.parent, m); m['_slug'] = mf.parent.name; kols.append(m)
    # 故意不写 ROOT/index.html。旧逻辑写的就是约 1.4KB 的卡片墙。
    print(f'legacy: rebuilt {len(kols)} meta.json site(s); portal index.html left untouched')

def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

def _has_text(v):
    return isinstance(v, str)

def check_archive(slug, doc):
    """门户会直接取的字段。别名与 index.html 里的兼容分支一致，不改档案原文。"""
    problems = []
    for key in ('meta', 'outline', 'lec', 'tw', 'score', 'scoreSum', 'models', 'articles'):
        if key not in doc:
            problems.append(f'{slug}: 缺少顶层 {key}')
    meta, outline = doc.get('meta') or {}, doc.get('outline') or {}
    if not isinstance(meta, dict):
        return problems + [f'{slug}: meta 不是对象']
    for key in ('hero', 'handle', 'type', 'from', 'to', 'built', 'lede', 'note'):
        if not _has_text(meta.get(key)):
            problems.append(f'{slug}: meta.{key} 缺失')
    for key in ('total', 'cand', 'good', 'core'):
        if not _num(meta.get(key)):
            problems.append(f'{slug}: meta.{key} 不是数字')
    if not isinstance(meta.get('badges'), list):
        problems.append(f'{slug}: meta.badges 不是数组')
    else:
        for i, b in enumerate(meta['badges']):
            if not isinstance(b, dict) or not (_has_text(b.get('v')) or _has_text(b.get('value')) or _num(b.get('v')) or _num(b.get('value'))):
                problems.append(f'{slug}: badges[{i}] 缺少 v/value')
            if not isinstance(b, dict) or not (_has_text(b.get('k')) or _has_text(b.get('label'))):
                problems.append(f'{slug}: badges[{i}] 缺少 k/label')
    if not isinstance(meta.get('sugg'), list):
        problems.append(f'{slug}: meta.sugg 不是数组')
    vols = outline.get('vols') if isinstance(outline, dict) else None
    if not isinstance(vols, list) or not vols:
        problems.append(f'{slug}: outline.vols 为空')
        vol_ids = set()
    else:
        vol_ids = set()
        for v in vols:
            if not isinstance(v, dict) or 'v' not in v or not isinstance(v.get('lec'), list):
                problems.append(f'{slug}: 卷目录缺少 v/lec')
                continue
            vol_ids.add(v['v'])
            for lec in v['lec']:
                if not (isinstance(lec, list) and len(lec) >= 2):
                    problems.append(f'{slug}: 卷{v["v"]} 讲条不是 [n, title, ...]')
    if not isinstance(meta.get('loopDetail'), list):
        problems.append(f'{slug}: meta.loopDetail 不是数组')
    else:
        for i, step in enumerate(meta['loopDetail']):
            if not isinstance(step, dict) or not _has_text(step.get('name')) or not _has_text(step.get('desc')):
                problems.append(f'{slug}: loopDetail[{i}] 缺少 name/desc')
            elif step.get('vol') not in vol_ids:
                problems.append(f'{slug}: loopDetail[{i}] 的 vol={step.get("vol")} 对不上目录')
    ss = doc.get('scoreSum') or {}
    if not isinstance(ss, dict):
        problems.append(f'{slug}: scoreSum 不是对象')
    else:
        for key in ('total', 'verifiable', 'right', 'wrong', 'partial', 'pending', 'insight', 'by_domain'):
            if key not in ss:
                problems.append(f'{slug}: scoreSum 缺少 {key}')
        if 'by_domain' in ss and not isinstance(ss['by_domain'], dict):
            problems.append(f'{slug}: scoreSum.by_domain 不是对象')
    lecs = doc.get('lec')
    if not isinstance(lecs, list) or not lecs:
        problems.append(f'{slug}: lec 为空')
    else:
        for lec in lecs:
            if not isinstance(lec, dict):
                problems.append(f'{slug}: lec 条目不是对象')
                continue
            n = lec.get('n')
            for key in ('title', 'question', 'limits'):
                if not _has_text(lec.get(key)):
                    problems.append(f'{slug}: L{n} 缺少 {key}')
            if not isinstance(lec.get('takeaways'), list):
                problems.append(f'{slug}: L{n} takeaways 不是数组')
            deep = lec.get('deep') if isinstance(lec.get('deep'), dict) else {}
            if not _has_text(deep.get('phenomenon')) or not _has_text(deep.get('mechanism')) or not isinstance(deep.get('rules'), list):
                problems.append(f'{slug}: L{n} deep 缺少 phenomenon/mechanism/rules')
            gm = lec.get('gmgn') if isinstance(lec.get('gmgn'), dict) else {}
            if not isinstance(gm.get('borrow'), list) or not isinstance(gm.get('filter'), list) or not _has_text(gm.get('guard')):
                problems.append(f'{slug}: L{n} gmgn 缺少 borrow/filter/guard')
            if not isinstance(lec.get('cases'), list) or not isinstance(lec.get('timeline'), list) or not isinstance(lec.get('lead'), list):
                problems.append(f'{slug}: L{n} cases/timeline/lead 不是数组')
            quote = lec.get('quote')
            if isinstance(quote, dict):
                if 'text' not in quote:
                    problems.append(f'{slug}: L{n} quote 缺少 text')
            elif not _has_text(quote):
                problems.append(f'{slug}: L{n} quote 缺失')
            for c in lec.get('cases') or []:
                if not isinstance(c, dict) or any(k not in c for k in ('name', 'discover', 'entry', 'hold', 'exit', 'lesson', 'ids')):
                    problems.append(f'{slug}: L{n} 案例字段不全')
                    break
    tw = doc.get('tw')
    if not isinstance(tw, list):
        problems.append(f'{slug}: tw 不是数组')
    elif tw:
        t0 = tw[0]
        if isinstance(t0, dict):
            for key in ('i', 't', 'k', 'x', 'q', 'lv', 'g', 'd', 's', 'l', 'v', 'r', 'm', 'f', 'L'):
                if key not in t0:
                    problems.append(f'{slug}: 推文对象缺少 {key}')
                    break
        elif not (isinstance(t0, list) and len(t0) >= 15):
            problems.append(f'{slug}: 推文数组长度不足')
    for m in doc.get('models') or []:
        if not isinstance(m, dict) or not _has_text(m.get('name')) or not _has_text(m.get('desc')):
            problems.append(f'{slug}: 思维模型缺少 name/desc')
            break
        q = m.get('quote')
        if isinstance(q, dict):
            if 'text' not in q:
                problems.append(f'{slug}: 思维模型 quote 缺少 text')
                break
        elif not _has_text(q):
            problems.append(f'{slug}: 思维模型 quote 缺失')
            break
        if not isinstance(m.get('lec') or m.get('lectures'), list):
            problems.append(f'{slug}: 思维模型缺少 lec/lectures')
            break
    for a in doc.get('articles') or []:
        if not isinstance(a, dict) or not _has_text(a.get('title')) or not _has_text(a.get('url')):
            problems.append(f'{slug}: 长文缺少 title/url')
            break
        if not any(_has_text(a.get(k)) for k in ('text', 'body', 'excerpt')):
            problems.append(f'{slug}: 长文缺少 text/body/excerpt')
            break
    for s in doc.get('score') or []:
        if not isinstance(s, dict) or any(k not in s for k in ('date', 'asset', 'claim', 'id', 'result', 'evidence')):
            problems.append(f'{slug}: 记分卡条目缺少 date/asset/claim/id/result/evidence')
            break
    return problems

def check_portal():
    """确认门户文件还在，且每个 kols.json 条目都能被页面加载。"""
    index = ROOT / 'index.html'
    text = index.read_text(encoding='utf-8') if index.exists() else ''
    problems = []
    if 'id="app"' not in text or 'data/kols.json' not in text or 'function route' not in text:
        problems.append('根目录 index.html 不是哈希路由门户。已拒绝写回旧版卡片墙；请从版本库恢复 index.html。')
    kols_path = ROOT / 'data' / 'kols.json'
    try:
        kols = json.loads(kols_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as e:
        print(f'门户校验失败：data/kols.json 无法读取 ({e})')
        raise SystemExit(1)
    if not isinstance(kols, list) or not kols:
        problems.append('data/kols.json 应是非空数组')
        kols = []
    slugs = []
    for k in kols:
        if not isinstance(k, dict) or not k.get('slug'):
            problems.append('kols.json 有条目缺少 slug')
            continue
        slug = k['slug']
        slugs.append(slug)
        for key in ('name', 'handle', 'type', 'intro', 'from', 'to'):
            if not _has_text(k.get(key)):
                problems.append(f'{slug}: kols.json 缺少 {key}')
        for key in ('total', 'good', 'core', 'lectures'):
            if not _num(k.get(key)):
                problems.append(f'{slug}: kols.json.{key} 不是数字')
        sc = k.get('score') if isinstance(k.get('score'), dict) else {}
        for key in ('right', 'wrong', 'partial', 'pending'):
            if key not in sc:
                problems.append(f'{slug}: kols.json.score 缺少 {key}')
        for suffix in ('.json', '_models.json', '_articles.json', '_tweets.csv'):
            if not (ROOT / 'data' / f'{slug}{suffix}').exists():
                problems.append(f'缺少 data/{slug}{suffix}')
        arch = ROOT / 'data' / f'{slug}.json'
        if arch.exists():
            try:
                doc = json.loads(arch.read_text(encoding='utf-8'))
            except json.JSONDecodeError as e:
                problems.append(f'{slug}.json 无法解析: {e}')
                continue
            problems.extend(check_archive(slug, doc))
            if (doc.get('meta') or {}).get('slug') not in (None, slug):
                problems.append(f'{slug}: meta.slug 与文件名不一致')
    if problems:
        print('门户校验失败：')
        for p in problems:
            print(' -', p)
        raise SystemExit(1)
    print(f'门户校验通过：{len(slugs)} 个档案（{", ".join(slugs)}）。未改写 index.html。')

def main():
    if '--legacy' in sys.argv[1:]:
        build_legacy()
        return
    before = (ROOT / 'index.html').read_bytes() if (ROOT / 'index.html').exists() else None
    check_portal()
    after = (ROOT / 'index.html').read_bytes() if (ROOT / 'index.html').exists() else None
    if before != after:
        print('门户校验改动了 index.html，这不应该发生')
        raise SystemExit(1)

if __name__ == '__main__': main()
