#!/usr/bin/env python3
"""把 twillot 导出里尚未收录的阿峰推文补进档案。

不改已有讲义、记分结论、旧帖的 lv/标签。只做三件事：
1. 导出里正文（去掉空白和字面 \\n 后）确实不同的旧帖，改回导出原文。
2. 导出里没有的 id 追加进来，按下面的规则打标。
3. 重算 meta / kols.json 的条数、年份、可信度占比和截止日期。

规则（只用于新帖）：
- 方法论（原创/引用/Article，正文够长，且写出建议、不适合、原则等）→ lv2
- 观点 / 预测 / 晒单 / 复盘 / 事实爆料 → lv1
- 其余 → lv0 闲聊
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_IN = Path(sys.argv[1]) if len(sys.argv) > 1 else None
SLUG = "aa_afeng"

TAGS = [
    ("链上安全与黑客", r"黑客|被盗|私钥|钓鱼|二维码|诈骗|貔貅|貔犰"),
    ("AI与大模型", r"(?i)(?<![a-z])ai(?![a-z])|deep\s*seek|大模型|chatgpt|claude|大肥鱼|人工智能"),
    ("工具与教程", r"(?i)gmgn|debot|axiom|扫链|蝴蝶"),
    ("涨粉与互关", r"互关|涨粉|蓝v|蓝V"),
    ("盘型识别", r"阴谋|控盘|洗盘|吸筹|庄家"),
    ("仓位与风控", r"仓位|止损|出本|补仓|满仓|本金|风控|all\s*in|回撤"),
    ("周期与牛熊判断", r"牛市|熊市|周期|牛初|主升|抄底|阴跌|下探"),
    ("美股与AI投资", r"美股|币股|英伟达|纳指"),
    ("Meme与链上交易", r"(?i)meme|土狗|内盘|外盘|pvp|金狗|打狗|归0|four\.?meme|市值"),
    ("交易所与行业", r"(?i)币安|binance|okx|交易所|交所|bnb|提现"),
    ("宏观与市场判断", r"(?i)(?<![a-z])btc(?![a-z])|比特币|(?<![a-z])eth(?![a-z])|以太|大盘|行情"),
    ("项目与叙事分析", r"叙事|fomo|创新|盘子|标的"),
    ("心态与纪律", r"心态|纪律|休息|别黑"),
    ("链上数据分析", r"开发地址|dev地址|尾号|链上数据"),
    ("KOL与信息源", r"(?i)kol|工作室|跟单"),
    ("晒单", r"赚了|亏了|盈利|回吐|万u"),
    ("复盘", r"复盘"),
]

def unescape(s):
    if not s:
        return ""
    return s.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")

def squash(s):
    return re.sub(r"\s+", "", unescape(s or ""))

def body_len(s):
    return len(re.sub(r"https?://\S+|@\w+|\s+", "", s or ""))

def tag_of(text):
    hits = []
    for name, pat in TAGS:
        n = len(re.findall(pat, text))
        if n:
            hits.append((n, name))
    hits.sort(reverse=True)
    if not hits:
        return ["生活杂谈"]
    top = hits[0][0]
    out = []
    for n, name in hits:
        if name in out:
            continue
        if len(out) < 2 and n >= 1:
            out.append(name)
        if len(out) >= 2:
            break
    return out

def dtype_of(text, kind):
    n = body_len(text)
    if "复盘" in text and n >= 30 and kind in ("post", "quote", "Article"):
        return "复盘"
    if n >= 50 and re.search(r"误检测|二维码扫|被盗|不要用.{0,12}(钱包|二维码)", text):
        return "事实爆料"
    if kind in ("post", "quote", "Article") and n >= 80 and re.search(r"不适合|一定要|原则|记住|交易逻辑", text):
        return "方法论"
    if kind in ("post", "quote") and n >= 28 and re.search(r"下探|看涨|看跌|dip|满仓|all in|会阴跌", text, re.I):
        return "预测"
    if kind in ("post", "quote") and n >= 24 and re.search(r"赚了|亏了|盈利|回吐|归0", text) and re.search(r"\d", text):
        return "晒单"
    if kind in ("post", "quote", "Article") and n >= 50 and re.search(r"感觉|觉得|其实|说实话", text):
        return "观点"
    return "闲聊"

def lv_of(dt):
    if dt == "方法论":
        return 2
    if dt == "闲聊":
        return 0
    return 1

def flag_of(text):
    if re.search(r"抽奖|转发.{0,6}关注|关注.{0,6}转发", text):
        return ["tpl"]
    if re.search(r"axiom\.trade/@|邀请码|返佣", text, re.I):
        return ["ref"]
    if re.search(r"0x[0-9a-fA-F]{40}|pump\b", text) and re.search(r"买|卖|仓|hold|call", text, re.I):
        return ["own"]
    return []

def first_line(text, n=42):
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:n]
    return ""

def has_media(row):
    if str(row.get("Image", "")).lower() == "true":
        return 1
    media = (row.get("Media") or "").strip()
    return 0 if media in ("", "[]", "null") else 1

def as_int(v):
    try:
        return int(v or 0)
    except ValueError:
        return 0

def main():
    if CSV_IN is None or not CSV_IN.exists():
        sys.exit("usage: supplement_aa_afeng.py <twillot.csv>")
    rows = list(csv.DictReader(CSV_IN.open(encoding="utf-8-sig")))
    by_id = {r["Post ID"]: r for r in rows}
    doc_path = ROOT / "data" / f"{SLUG}.json"
    csv_path = ROOT / "data" / f"{SLUG}_tweets.csv"
    art_path = ROOT / "data" / f"{SLUG}_articles.json"
    kols_path = ROOT / "data" / "kols.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    tw = doc["tw"]
    old_ids = {t[0] for t in tw}
    text_fixed = []
    quote_fixed = []
    metric_fixed = 0
    for t in tw:
        src = by_id.get(t[0])
        if not src:
            continue
        new_text = unescape(src["Content"])
        if squash(t[3]) != squash(new_text):
            old_summary = t[8]
            if old_summary and old_summary.strip() == first_line(t[3], len(old_summary)):
                t[8] = first_line(new_text, max(len(old_summary), 12))
            t[3] = new_text
            text_fixed.append(t[0])
        new_quote = unescape(src["Quoted Post"])
        if squash(t[4]) != squash(new_quote):
            t[4] = new_quote
            quote_fixed.append(t[0])
        likes, views, rts = as_int(src["Favorite Count"]), as_int(src["Views Count"]), as_int(src["Retweet Count"])
        media = has_media(src)
        if (t[9], t[10], t[11], t[12]) != (likes, views, rts, media):
            t[9], t[10], t[11], t[12] = likes, views, rts, media
            metric_fixed += 1

    added = []
    for src in rows:
        if src["Post ID"] in old_ids:
            continue
        text = unescape(src["Content"])
        kind = src["Post Type"] or "post"
        dt = dtype_of(text, kind)
        lv = lv_of(dt)
        added.append([
            src["Post ID"],
            src["Created At"],
            kind,
            text,
            unescape(src["Quoted Post"]),
            lv,
            tag_of(text),
            dt if lv else "闲聊",
            first_line(text) if lv else "",
            as_int(src["Favorite Count"]),
            as_int(src["Views Count"]),
            as_int(src["Retweet Count"]),
            has_media(src),
            flag_of(text),
            [],
            [],
        ])

    tw.extend(added)
    tw.sort(key=lambda t: (t[1], t[0]))
    doc["tw"] = tw

    known_articles = {a["id"] for a in doc["articles"]}
    new_articles = 0
    for src in rows:
        if src["Post Type"] != "Article" and not (src.get("Article Title") or "").strip():
            continue
        if src["Post ID"] in known_articles:
            continue
        text = unescape(src["Content"])
        title = (src.get("Article Title") or "").strip() or first_line(text, 40) or src["Post ID"]
        words = len(re.sub(r"\s+", "", text))
        doc["articles"].append({
            "id": src["Post ID"],
            "title": title,
            "date": src["Created At"][:10],
            "url": src["URL"],
            "words": words,
            "readMin": max(1, words // 400),
            "excerpt": text,
            "note": "导出仅有短摘录，全文未收录",
            "full": None,
        })
        known_articles.add(src["Post ID"])
        new_articles += 1
    doc["articles"].sort(key=lambda a: a["date"])

    lv_c = Counter(t[5] for t in tw)
    cand = len(tw)
    good = lv_c[1] + lv_c[2]
    core = lv_c[2]
    old_total = doc["meta"]["total"]
    old_cand = doc["meta"]["cand"]
    filtered_out = old_total - old_cand
    total = cand + filtered_out
    years = Counter(t[1][:4] for t in tw)
    flag_n = Counter(f for t in tw for f in t[13])
    def pct(k):
        return round(flag_n[k] / cand * 100, 2) if cand else 0
    meta = doc["meta"]
    meta["total"] = total
    meta["cand"] = cand
    meta["good"] = good
    meta["core"] = core
    meta["to"] = max(t[1][:10] for t in tw)
    meta["built"] = "2026-10-30"
    meta["years"] = {y: years[y] for y in sorted(years)}
    meta["flags"] = {"tpl": pct("tpl"), "ref": pct("ref"), "tr": pct("tr"), "own": pct("own"), "fab": pct("fab")}
    core_pct = core / cand * 100 if cand else 0
    lv1 = lv_c[1]
    lv1_pct = lv1 / cand * 100 if cand else 0
    meta["tagging"] = (
        f"逐条打标 cand={cand}；lv2={core}（{core_pct:.1f}%） lv1={lv1}（{lv1_pct:.1f}%）。"
        f"2026-10-30 用 twillot 导出补入此前未收录的 {len(added)} 条；新帖按规则打标，不改已有讲义和记分。"
        "旧档略低于5–10%/15–30%目标，因抽奖短回复与2022粉圈多，方法集中在2026-08~10，未灌水。"
        "背景：据慧哥2026-09-11推特五维与波段型四人对照。"
    )
    for b in meta["badges"]:
        key = b.get("k") or b.get("label")
        if key == "预筛推文":
            b["v"] = f"{cand:,}"
        elif key == "干货 lv≥1":
            b["v"] = f"{good:,}"
        elif key == "核心 lv2":
            b["v"] = f"{core}（{core_pct:.1f}%）"
        elif key == "X Article":
            b["v"] = str(len(doc["articles"]))

    doc_path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    art_path.write_text(json.dumps(doc["articles"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "time", "kind", "text", "quote", "lv", "tags", "dtype", "summary", "likes", "views", "rts", "media", "flags", "lectures"])
        for t in tw:
            w.writerow([
                t[0], t[1], t[2], t[3], t[4], t[5], "|".join(t[6]), t[7], t[8],
                t[9], t[10], t[11], t[12], "|".join(t[13]), "|".join(str(x) for x in t[14]),
            ])
    kols = json.loads(kols_path.read_text(encoding="utf-8"))
    for k in kols:
        if k["slug"] != SLUG:
            continue
        k["total"] = total
        k["good"] = good
        k["core"] = core
        k["to"] = meta["to"]
        k["updated"] = "2026-10-30"
    kols_path.write_text(json.dumps(kols, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    new_lv = Counter((t[5], t[7]) for t in added)
    print(f"added {len(added)}  text_fixed {len(text_fixed)}  quote_fixed {len(quote_fixed)}  metric_fixed {metric_fixed}  articles+{new_articles}")
    print(f"cand {old_cand} -> {cand}  good {good}  core {core}  total {old_total} -> {total}  to {meta['to']}")
    print("new lv", dict(new_lv))
    print("text ids", text_fixed)
    print("quote ids", quote_fixed)
    print("--- new lv2 ---")
    for t in added:
        if t[5] == 2:
            print(t[1], t[2], t[6], t[3][:70].replace("\n", " | "))

if __name__ == "__main__":
    main()
