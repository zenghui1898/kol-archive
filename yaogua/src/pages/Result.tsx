import { Link, useParams } from "react-router-dom";
import { Reading } from "../components/Reading";
import { resolveCast } from "../lib/cast";
import { formatWhen, getRecord } from "../lib/storage";

export function Result() {
  const { id = "" } = useParams();
  const record = getRecord(id);

  if (!record) {
    return (
      <div className="empty-state">
        <p className="kicker">没有这页记录</p>
        <h1>卦不在这里</h1>
        <p>它可能来自另一台浏览器，或已经被清掉。记录只留在摇出它的这台设备上。</p>
        <Link className="btn" to="/cast">
          去摇一卦
        </Link>
      </div>
    );
  }

  const cast = resolveCast(record.lines);

  return (
    <div className="result-page">
      <Reading cast={cast} hex={cast.primary} question={record.question} when={formatWhen(record.createdAt)} />
      <div className="actions result-actions">
        <Link className="btn" to="/">
          再摇一卦
        </Link>
        <Link className="btn ghost" to="/gua">
          六十四卦
        </Link>
        <Link className="btn ghost" to="/history">
          记录
        </Link>
      </div>
    </div>
  );
}
