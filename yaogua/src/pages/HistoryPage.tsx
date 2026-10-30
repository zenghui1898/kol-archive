import { useState } from "react";
import { Link } from "react-router-dom";
import { HexFigure } from "../components/HexFigure";
import { resolveCast } from "../lib/cast";
import { clearRecords, deleteRecord, formatWhen, loadRecords, type CastRecord } from "../lib/storage";

export function HistoryPage() {
  const [records, setRecords] = useState<CastRecord[]>(() => loadRecords());

  function remove(id: string) {
    deleteRecord(id);
    setRecords(loadRecords());
  }

  function removeAll() {
    if (!window.confirm("清掉这台浏览器里的起卦记录？")) return;
    clearRecords();
    setRecords([]);
  }

  if (records.length === 0) {
    return (
      <div className="empty-state">
        <p className="kicker">记录</p>
        <h1>还没有留下卦</h1>
        <p>摇过一次，就会记在这台浏览器里。换一台设备，或清掉站点数据，记录就没有了。</p>
        <Link className="btn" to="/">
          去摇一卦
        </Link>
      </div>
    );
  }

  return (
    <div className="history">
      <header className="index-head">
        <div>
          <p className="kicker">只存在这台浏览器</p>
          <h1>记录</h1>
          <p className="lede">最近 {records.length} 次。新的在上面。</p>
        </div>
        <button type="button" className="btn ghost" onClick={removeAll}>
          全部清掉
        </button>
      </header>
      <ul className="history-list">
        {records.map((record) => {
          const cast = resolveCast(record.lines);
          return (
            <li key={record.id}>
              <Link to={`/result/${record.id}`} className="history-card">
                <HexFigure bits={cast.bits} changing={cast.info.map((line) => line.changing)} size="sm" label={cast.primary.title} />
                <div>
                  <b>
                    {cast.primary.name}
                    <small>{cast.primary.title}</small>
                  </b>
                  <span>{record.question || "没有写下问题"}</span>
                  <em>
                    {formatWhen(record.createdAt)}
                    {cast.quiet ? " · 无动爻" : ` · ${cast.moving.length} 爻在动`}
                    {!cast.quiet && cast.primary.id !== cast.relating.id ? ` · 之${cast.relating.name}` : ""}
                  </em>
                </div>
              </Link>
              <button type="button" className="text-btn" onClick={() => remove(record.id)}>
                删除
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
