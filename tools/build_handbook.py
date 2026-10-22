"""由 handbook_spec + classify 生成：方法论全书 HTML 片段、Markdown 全书、精选池/规则库/领域分卷数据。"""
import json,html,re,datetime,collections,csv,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import classify, handbook_spec as H
esc=lambda s:html.escape(str(s))
def render(d):
    rows=classify.run(); R=d/'data'
    (R/'domains').mkdir(exist_ok=True)
    byid={r['id']:r for r in rows}
    json.dump(rows,open(R/'0xaa_evaluated.json','w'),ensure_ascii=False)
    json.dump({r['id']:r['domain'][:2] for r in rows},open(R/'domain_map.json','w'))
    for c in classify.NAMES:
        rs=[r for r in rows if r['domain']==c]
        json.dump(rs,open(R/f'domains/{c}.json','w'),ensure_ascii=False)
        with open(R/f'domains/{c}.csv','w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
    orig=[r for r in rows if r['kind']=='orig']
    feat={c:sorted([r for r in orig if r['domain']==c],key=lambda r:-r['substance_score'])[:60] for c in classify.NAMES if c[:2] in '0102030405'}
    rules=sorted([r for r in orig if r['rule_hits']>=2 and r['domain']!='06_giveaway' and len(r['text'])>=60],key=lambda r:-r['substance_score'])[:300]
    json.dump([r for v in feat.values() for r in v],open(R/'0xaa_featured.json','w'),ensure_ascii=False)
    json.dump(rules,open(R/'0xaa_rules.json','w'),ensure_ascii=False)
    for n,rs in (('0xaa_featured',[r for v in feat.values() for r in v]),('0xaa_rules',rules)):
        with open(R/f'{n}.csv','w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
    # 引用编号
    num={};
    def ref(i):
        if i not in byid: raise SystemExit(f'推文 {i} 不在数据集中')
        num.setdefault(i,len(num)+1); return num[i]
    def quote(i):
        r=byid[i];n=ref(i)
        return (f'<blockquote class="q" id="t{i}"><div class="mut">[#{n}] {r["date"]} 北京时间 · ❤ {r["likes"]} · 🔁 {r["retweets"]} · 👁 {r["views"]} · '
                f'<a href="{r["url"]}" target="_blank">原推</a></div><p>{esc(r["text"])}</p></blockquote>')
    toc=[];body=[];md=[f'# 0xAA（@0xAA_Science）方法论全书\n\n> 数据：15,372 条推文（2021-11 ~ 2026-10-22）。每条结论附原推链接。生成：{datetime.date.today()}\n\n## 序言\n\n{H.PREFACE}\n']
    for vi,(vk,vt,vd,topics) in enumerate(H.VOLS):
        toc.append(f'<a class="tv" href="#v{vi}">{vk} {esc(vt)}</a>')
        body.append(f'<div class="sec vol" id="v{vi}"><div class="vk">{vk}</div><h2>{esc(vt)}</h2><p class="mut">{esc(vd)}</p>')
        md.append(f'\n## {vk}：{vt}\n\n*{vd}*\n')
        for ti,(tt,bul,interp,qs) in enumerate(topics):
            tid=f'v{vi}t{ti}';toc.append(f'<a class="tt" href="#{tid}">· {esc(tt)}</a>')
            li=''.join(f'<li>{esc(b)} '+' '.join(f'<a class="rf" href="{byid[i]["url"]}" target="_blank">[#{ref(i)}]</a>' for i in ids)+'</li>' for b,ids in bul)
            body.append(f'<div class="topic" id="{tid}"><h3>{esc(tt)}</h3><h4>💡 要点（均可溯源）</h4><ul>{li}</ul>'
                        +(f'<h4>🔍 整理者解读</h4><p>{esc(interp)}</p>' if interp else '')
                        +f'<details><summary>💬 原推精选（{len(qs)} 条全文）</summary>{"".join(quote(i) for i in qs)}</details></div>')
            md.append(f'\n### {tt}\n\n#### 要点\n'+''.join(f'- {b} '+' '.join(f'[原推]({byid[i]["url"]})' for i in ids)+'\n' for b,ids in bul)
                      +(f'\n#### 整理者解读\n{interp}\n' if interp else '')+'\n#### 原推精选\n'
                      +''.join(f'\n> **{byid[i]["date"]}** · ❤ {byid[i]["likes"]} · 👁 {byid[i]["views"]}\n>\n> '+byid[i]['text'].replace('\n','\n> ')+f'\n>\n> 🔗 {byid[i]["url"]}\n' for i in qs))
        body.append('</div>')
    # 领域分布（年度）
    yrs=sorted({r['date'][:4] for r in rows});cnt=collections.Counter((r['date'][:4],r['domain']) for r in orig)
    cols={'01':'#B45309','02':'#B91C1C','03':'#7C3AED','04':'#0369A1','05':'#15803D','06':'#9CA3AF','07':'#D6D3D1'}
    bars=''
    for y in yrs:
        tot=sum(cnt[(y,c)] for c in classify.NAMES) or 1
        seg=''.join(f'<span title="{classify.NAMES[c]} {cnt[(y,c)]}" style="width:{cnt[(y,c)]*100/tot:.2f}%;background:{cols[c[:2]]}"></span>' for c in classify.NAMES)
        bars+=f'<div class="brow"><b>{y}</b><div class="bar">{seg}</div><span class="mut">{tot}</span></div>'
    leg=''.join(f'<span><i style="background:{cols[c[:2]]}"></i>{classify.NAMES[c]}（{sum(1 for r in rows if r["domain"]==c)}）</span>' for c in classify.NAMES)
    dist=f'<div class="sec" id="dist"><h2>领域分布 · 原创推文按年</h2><p class="mut">规则分类（tools/classify.py，关键词+干货分，可复现）。数字为原创推文数；括号内为全部推文数。</p>{bars}<div class="leg">{leg}</div></div>'
    toc.insert(0,'<a class="tv" href="#dist">领域分布</a>')
    # 精选池 + 规则库
    pool=''.join(f'<details><summary>{classify.NAMES[c]} · 干货分前 {len(v)} 条</summary>'+''.join(
        f'<div class="tw"><div class="mut">{r["date"]} · 干货分 {r["substance_score"]} · ❤ {r["likes"]} · <a href="{r["url"]}" target="_blank">原推</a></div><p>{esc(r["text"])}</p></div>' for r in v)+'</details>' for c,v in feat.items())
    rul=''.join(f'<div class="tw rc" data-d="{r["domain"][:2]}"><div class="mut"><span class="kd kd-orig">{classify.NAMES[r["domain"]]}</span> {r["date"][:10]} · ❤ {r["likes"]} · <a href="{r["url"]}" target="_blank">原推</a></div><p>{esc(r["text"])}</p></div>' for r in rules)
    body.append(f'<div class="sec" id="pool"><h2>分卷精选池</h2><p class="mut">每个领域按“干货分”（正文长度、规则性措辞、互动量；回复/抽奖降权）取前 60 条原创。</p>{pool}</div>')
    body.append(f'<div class="sec" id="rules"><h2>规则与经验卡片库 <span class="mut">（{len(rules)} 条）</span></h2><p class="mut">自动抽取含“建议/原则/复盘/步骤/列表”等规则性措辞的原创推文，原文呈现、不改写。</p><div class="twbar"><input id="rq" type="search" placeholder="搜索规则卡片…"><span id="rn" class="mut"></span></div><div id="rl" style="max-height:640px;overflow:auto">{rul}</div></div>')
    dl=''.join(f'<li><b>{classify.NAMES[c]}</b>：<a href="data/domains/{c}.json">JSON</a> · <a href="data/domains/{c}.csv">CSV</a></li>' for c in classify.NAMES)
    body.append(f'<div class="sec" id="dl"><h2>数据下载</h2><ul><li>全量原始：<a href="data/tweets_all.json">tweets_all.json</a>（15,372 条）</li><li>评分后全量：<a href="data/0xaa_evaluated.json">0xaa_evaluated.json</a></li><li>精选：<a href="data/0xaa_featured.json">JSON</a> · <a href="data/0xaa_featured.csv">CSV</a>；规则卡片：<a href="data/0xaa_rules.json">JSON</a> · <a href="data/0xaa_rules.csv">CSV</a></li>{dl}<li>方法论全书 Markdown：<a href="docs/0xAA_方法论全书.md">0xAA_方法论全书.md</a>；生成脚本：tools/classify.py、tools/handbook_spec.py</li></ul><p class="mut">CSV 为 UTF-8-SIG，Excel 直开不乱码。</p></div>')
    toc+=['<a class="tv" href="#pool">分卷精选池</a>','<a class="tv" href="#rules">规则卡片库</a>','<a class="tv" href="#cases">链上案例/报告</a>','<a class="tv" href="#timeline">全量时间线</a>','<a class="tv" href="#dl">数据下载</a>']
    (d/'docs/0xAA_方法论全书.md').write_text('\n'.join(md))
    js="""<script>(function(){const q=document.getElementById('rq');if(!q)return;const cs=[...document.querySelectorAll('#rl .rc')];const f=()=>{const v=q.value.trim().toLowerCase();let n=0;cs.forEach(c=>{const m=!v||c.textContent.toLowerCase().includes(v);c.style.display=m?'':'none';n+=m});document.getElementById('rn').textContent=`${n} / ${cs.length}`};q.addEventListener('input',f);f();})();</script>"""
    pre=f'<div class="sec"><h2>序言</h2><p>{esc(H.PREFACE)}</p><p class="mut">共引用 {len(num)} 条原推；正文要点 [#n] 编号对应下方引文。</p></div>'
    return ''.join(toc), pre+dist+''.join(body)+js, len(num)
