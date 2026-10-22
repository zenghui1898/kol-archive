"""0xAA 推文领域分类 + 干货评分（规则版，可复现；对应参考站 jev_* 字段的透明替代）"""
import json,re,math,datetime,collections,csv,pathlib
R=pathlib.Path(__file__).resolve().parent.parent/'0xaa'
D=json.load(open(R/'data/tweets_all.json'))['data']
TZ=datetime.timezone(datetime.timedelta(hours=8))
DOM=[
 ('01_solidity_edu','Solidity 与 Web3 开发教育',r'solidity|智能合约|合约|wtf|教程|ethers|evm|erc\d|openzeppelin|foundry|hardhat|编程|开发者|黑客松|hackathon|北大|链协|讲|课程|零知识|zk|密码学|uniswap.*(源码|v[234])|源码'),
 ('02_security','链上安全、黑客与白帽救援',r'黑客|被盗|私钥|助记词|救援|rescue|漏洞|钓鱼|攻击|盗|exploit|hack|mev|夹子|安全|授权|骗|跑路|rug|蜜罐'),
 ('03_meme','Meme 实战与社区币',r'meme|\$[a-z]{2,10}(?![a-z])|土狗|冲了|买了|卖了|梭|翻倍|市值|开盘|内盘|外盘|four\.?meme|pump|bsc|(?<![a-z])sol(?![a-z])|solana|scihub|ca[:：]|0x[0-9a-f]{40}|金狗|仓位|止盈|出本|回本|聪明钱|链上交易'),
 ('04_ai','AI、Agent 与 Vibe Coding',r'(?<![a-z])ai(?![a-z])|claude|gpt|openai|chatgpt|agent|vibe|llm|deepseek|gemini|大模型|龙虾|openclaw|cursor|grok|prompt|提示词|编码|写代码|codex|skill|token|蒸馏|模型|xapi'),
 ('05_industry','交易所、行业事件与市场观点',r'币安|binance|(?<![a-z])cz(?![a-z])|一姐|okx|交易所|暴跌|暴涨|牛市|熊市|周期|btc|美股|a股|港股|币价|行情|比特币|(?<![a-z])eth(?![a-z])|以太坊|监管|ftx|luna|3ac|爆雷|空投|airdrop|vc|项目方|融资|l2|starknet|strk|polymarket|预测市场|稳定币|etf|出金|银行'),
]
GIVE=r'抽\d*|抽奖|(?<![a-z])wl(?![a-z])|白名单|giveaway|开奖|点赞转发|转发.{0,4}点赞|drop your'
RULE=r'建议|原则|方法|步骤|教程|复盘|总结|注意|一定要|不要|记得|技巧|路线图|如何|怎么|为什么|经验|教训|\n\s*[1-9][\.、）)]|1️⃣|🧵|thread'
def kind(t):
    ty={r['type'] for r in t['referenced_tweets']}
    if t['is_retweet'] or 'retweeted' in ty: return 'rt'
    if t['is_reply'] or 'replied_to' in ty or t['in_reply_to_user_id']: return 'reply'
    return 'orig'
def bj(t): return datetime.datetime.fromisoformat(t['created_at'].replace('Z','+00:00')).astimezone(TZ)
def run():
    out=[]
    for t in D:
        x=t['text'];l=x.lower();k=kind(t);pm=t['public_metrics']
        hits={c:len(re.findall(p,l)) for c,_,p in DOM}
        give=bool(re.search(GIVE,l))
        rule=len(re.findall(RULE,l))
        body=re.sub(r'https?://\S+|@\w+','',x).strip()
        if k=='rt' : dom='07_daily'
        elif give: dom='06_giveaway'
        elif max(hits.values())==0 or len(body)<15: dom='07_daily'
        else: dom=max(hits,key=lambda c:(hits[c],-[d[0] for d in DOM].index(c)))
        sub=round(min(len(body),600)/100+1.2*min(rule,5)+math.log10(1+pm['like_count'])*1.5-(3 if k=='reply' else 0)-(4 if give else 0),2)
        out.append(dict(id=t['id'],date=bj(t).strftime('%Y-%m-%d %H:%M:%S'),kind=k,domain=dom,substance_score=sub,rule_hits=rule,
            likes=pm['like_count'],retweets=pm['retweet_count'],replies=pm['reply_count'],views=pm['impression_count'],
            text=x,url=f"https://x.com/0xAA_Science/status/{t['id']}"))
    out.sort(key=lambda r:r['date'],reverse=True)
    return out
NAMES={c:n for c,n,_ in DOM}|{'06_giveaway':'抽奖、白名单与活动','07_daily':'日常碎念、回复与转推'}
if __name__=='__main__':
    o=run();(R/'data/domains').mkdir(exist_ok=True)
    json.dump(o,open(R/'data/0xaa_evaluated.json','w'),ensure_ascii=False)
    for c in NAMES:
        rows=[r for r in o if r['domain']==c]
        json.dump(rows,open(R/f'data/domains/{c}.json','w'),ensure_ascii=False)
        with open(R/f'data/domains/{c}.csv','w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(collections.Counter(r['domain'] for r in o))
    print(collections.Counter(r['domain'] for r in o if r['kind']=='orig'))
