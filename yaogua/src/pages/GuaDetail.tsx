import { Link, useParams } from "react-router-dom";
import { Reading } from "../components/Reading";
import { hexagramById } from "../data/hexagrams";

export function GuaDetail() {
  const { id = "" } = useParams();
  const hex = hexagramById(Number(id));

  if (!hex) {
    return (
      <div className="empty-state">
        <p className="kicker">六十四卦之外</p>
        <h1>没有这一卦</h1>
        <p>通行的卦序从 1 到 64。回到目录里找。</p>
        <Link className="btn" to="/gua">
          返回目录
        </Link>
      </div>
    );
  }

  const prev = hex.id > 1 ? hex.id - 1 : null;
  const next = hex.id < 64 ? hex.id + 1 : null;

  return (
    <div className="result-page">
      <p className="canon-note">卦义速读。若要为眼下的事起一卦，回到摇卦。</p>
      <Reading hex={hex} />
      <div className="actions result-actions">
        <Link className="btn" to="/">
          为这件事摇一卦
        </Link>
        {prev && (
          <Link className="btn ghost" to={`/gua/${prev}`}>
            上一卦
          </Link>
        )}
        {next && (
          <Link className="btn ghost" to={`/gua/${next}`}>
            下一卦
          </Link>
        )}
        <Link className="btn ghost" to="/gua">
          目录
        </Link>
      </div>
    </div>
  );
}
