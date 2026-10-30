import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { HEXAGRAMS, TRIGRAMS, TRIGRAM_ORDER, type TrigramKey } from "../data/hexagrams";
import { HexFigure } from "../components/HexFigure";

export function IndexPage() {
  const [query, setQuery] = useState("");
  const [trigram, setTrigram] = useState<TrigramKey | "all">("all");

  const items = useMemo(() => {
    const needle = query.trim();
    return HEXAGRAMS.filter((hex) => {
      if (trigram !== "all" && hex.upper !== trigram && hex.lower !== trigram) return false;
      if (!needle) return true;
      const bag = `${hex.id}${hex.name}${hex.title}${hex.gist}${hex.upperLabel}${hex.lowerLabel}`;
      return bag.includes(needle);
    });
  }, [query, trigram]);

  return (
    <div className="index-page">
      <header className="index-head">
        <div>
          <p className="kicker">通行卦序</p>
          <h1>六十四卦</h1>
          <p className="lede">按上下卦浏览。点开是卦义速读，不是一次起卦。</p>
        </div>
        <label className="search">
          <span className="sr">搜索卦名</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜卦名、卦象或数字"
          />
        </label>
      </header>

      <div className="chips" role="group" aria-label="按卦象筛选">
        <button type="button" className={trigram === "all" ? "on" : ""} onClick={() => setTrigram("all")}>
          全部
        </button>
        {TRIGRAM_ORDER.map((key) => (
          <button
            key={key}
            type="button"
            className={trigram === key ? "on" : ""}
            onClick={() => setTrigram(key)}
          >
            {TRIGRAMS[key].nature}
            {TRIGRAMS[key].name}
          </button>
        ))}
      </div>

      {items.length === 0 ? (
        <div className="empty-state slim">
          <h2>没有相符的卦</h2>
          <p>试试「屯」，或一个卦象，比如「火」。</p>
        </div>
      ) : (
        <ul className="gua-grid">
          {items.map((hex) => (
            <li key={hex.id}>
              <Link to={`/gua/${hex.id}`} className="gua-card">
                <HexFigure bits={hex.bits} size="sm" label={hex.title} />
                <div>
                  <b>
                    {hex.name}
                    <small>第 {hex.id} 卦</small>
                  </b>
                  <span>{hex.title}</span>
                  <em>{hex.gist}</em>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
