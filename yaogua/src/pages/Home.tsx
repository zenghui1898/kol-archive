import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { resolveCast } from "../lib/cast";
import {
  clearDraft,
  clearPendingQuestion,
  formatWhen,
  loadDraft,
  loadRecords,
  savePendingQuestion,
} from "../lib/storage";

export function Home() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState("");
  const draft = useMemo(() => loadDraft(), []);
  const last = useMemo(() => loadRecords()[0], []);
  const lastHex = last ? resolveCast(last.lines).primary : undefined;

  function start(fresh: boolean) {
    if (fresh) {
      clearDraft();
      clearPendingQuestion();
      savePendingQuestion(question);
    }
    navigate("/cast");
  }

  return (
    <div className="home">
      <aside className="inscription">
        <div className="seal" aria-hidden="true">
          问心
        </div>
        <p className="vertical">自下而上，六爻成象</p>
        <ol>
          <li>字为阳，记作三</li>
          <li>背为阴，记作二</li>
          <li>老阳、老阴为动爻</li>
        </ol>
      </aside>

      <div className="home-main">
        <p className="kicker">铜钱六爻</p>
        <h1>摇卦</h1>
        <p className="lede">
          把一件事放在心里。三枚铜钱摇六次，从最下面的初爻摇到最上面的上爻。卦象自己站出来，供你对照，不替你做决定。
        </p>

        <label className="ask-label" htmlFor="question">
          此刻所问
          <span>可以留空</span>
        </label>
        <input
          id="question"
          className="question"
          maxLength={40}
          value={question}
          placeholder="可以写下，也可以只放在心里"
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") start(true);
          }}
        />
        <div className="ask-meta">{question.length}/40</div>

        <div className="actions">
          <button type="button" className="btn" onClick={() => start(true)}>
            {draft && draft.lines.length > 0 ? "重新摇一卦" : "开始摇卦"}
          </button>
          {draft && draft.lines.length > 0 && (
            <button type="button" className="btn ghost" onClick={() => start(false)}>
              继续未完的卦
            </button>
          )}
        </div>

        {last && lastHex && (
          <p className="last">
            上次是 {formatWhen(last.createdAt)} 的「{lastHex.name}」。
            <Link to={`/result/${last.id}`}>打开</Link>
          </p>
        )}

        <section className="method">
          <h2>铜钱怎么读</h2>
          <div className="method-grid">
            <article>
              <h3>三枚钱</h3>
              <p>有字的一面为阳，作三。背面为阴，作二。三枚相加，就是这一爻。</p>
            </article>
            <article>
              <h3>四个数</h3>
              <p>六是老阴，八是少阴，都是断的。七是少阳，九是老阳，都是连的。六和九要变。</p>
            </article>
            <article>
              <h3>本卦与之卦</h3>
              <p>六爻先组成现在的本卦。动爻翻转之后，成为后势的之卦。</p>
            </article>
          </div>
        </section>
      </div>
    </div>
  );
}
