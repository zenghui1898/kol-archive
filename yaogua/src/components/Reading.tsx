import { Link } from "react-router-dom";
import type { Hexagram } from "../data/hexagrams";
import { arithmetic, type LineInfo, type ResolvedCast } from "../lib/cast";
import { HexFigure } from "./HexFigure";

type Props = {
  cast?: ResolvedCast;
  hex: Hexagram;
  question?: string;
  when?: string;
};

export function Reading({ cast, hex, question, when }: Props) {
  const changing = cast?.info.map((line) => line.changing);
  const same = cast ? cast.primary.id === cast.relating.id : true;

  return (
    <article className="reading">
      {(question !== undefined || when) && (
        <header className="reading-ask">
          {question ? <p className="ask-text">「{question}」</p> : <p className="ask-text muted-ask">没有写下问题。卦仍可读，当作心里那一件事。</p>}
          {when && <p className="when">{when}</p>}
        </header>
      )}

      <div className="reading-hero">
        <HexFigure
          bits={cast?.bits ?? hex.bits}
          changing={changing}
          size="lg"
          label={`${hex.title}，自下而上`}
        />
        <div>
          <p className="kicker">第 {hex.id} 卦</p>
          <h1>{hex.name}</h1>
          <p className="title-line">{hex.title}</p>
          <p className="trigram-line">
            上卦 {hex.upperLabel}
            <span>下卦 {hex.lowerLabel}</span>
          </p>
          <p className="gist">{hex.gist}</p>
        </div>
      </div>

      <p className="legend">○ 老阳，将变为阴。× 老阴，将变为阳。爻从下往上读，初爻在最下。</p>

      <section className="prose">
        <h2>卦意</h2>
        <p>{hex.judgment}</p>
      </section>
      <section className="prose">
        <h2>象意</h2>
        <p>{hex.image}</p>
      </section>

      {cast ? <CastLines cast={cast} /> : <CanonLines hex={hex} />}

      {cast && !same && (
        <section className="relating">
          <div>
            <p className="kicker">之卦</p>
            <h2>
              第 {cast.relating.id} 卦 · {cast.relating.name}
            </h2>
            <p className="title-line">{cast.relating.title}</p>
            <p>
              动爻翻转之后，后势走向这一卦。本卦仍是现在，之卦是接下来的天气。
            </p>
            <p>{cast.relating.judgment}</p>
            <Link to={`/gua/${cast.relating.id}`}>看{cast.relating.name}的全文</Link>
          </div>
          <HexFigure bits={cast.changedBits} size="md" label={`${cast.relating.title}，变后的卦象`} />
        </section>
      )}

      {cast && same && (
        <section className="prose quiet">
          <h2>没有之卦</h2>
          <p>六爻都安静，没有要翻转的爻。读本卦即可。</p>
        </section>
      )}

      {cast && (
        <details className="throws">
          <summary>这次六次铜钱</summary>
          <ol>
            {cast.info.map((line) => (
              <li key={line.index}>
                <b>
                  {line.place} · {line.yao} · {line.name}
                  {line.changing ? " · 动" : ""}
                </b>
                <span>{arithmetic(line)}</span>
              </li>
            ))}
          </ol>
        </details>
      )}
    </article>
  );
}

function CastLines({ cast }: { cast: ResolvedCast }) {
  if (cast.quiet) return null;
  return (
    <section className="prose">
      <h2>动爻</h2>
      <p className="lead">
        {cast.moving.length === 1
          ? "这一爻在动。它的句子比其余五爻更贴着你现在的位置。"
          : "这几爻都在动。自下而上逐条读，再看它们翻转后的之卦。"}
      </p>
      <ul className="line-list">
        {cast.moving.map((line) => (
          <LineItem key={line.index} hex={cast.primary} line={line} />
        ))}
      </ul>
    </section>
  );
}

function CanonLines({ hex }: { hex: Hexagram }) {
  return (
    <section className="prose">
      <h2>六爻</h2>
      <p className="lead">这是卦义速读，不是一次起卦。自下而上。</p>
      <ul className="line-list">
        {hex.lines.map((text, index) => (
          <li key={index}>
            <b>{["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"][index]}</b>
            <span>{text}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function LineItem({ hex, line }: { hex: Hexagram; line: LineInfo }) {
  return (
    <li>
      <b>
        {line.yao} · {line.place} · {line.name} {line.mark}
      </b>
      <span>{hex.lines[line.index]}</span>
    </li>
  );
}
