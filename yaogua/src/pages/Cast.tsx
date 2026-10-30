import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Coins } from "../components/Coins";
import { HexFigure } from "../components/HexFigure";
import {
  CAST_HINTS,
  arithmetic,
  interpretLine,
  throwCoins,
  type CastLine,
  type CoinFace,
} from "../lib/cast";
import {
  clearDraft,
  clearPendingQuestion,
  loadDraft,
  loadPendingQuestion,
  saveDraft,
  saveRecord,
} from "../lib/storage";

const PLACES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"];
const EMPTY_FACES: [CoinFace | null, CoinFace | null, CoinFace | null] = [null, null, null];

export function Cast() {
  const navigate = useNavigate();
  const draft = useMemo(() => loadDraft(), []);
  const [question] = useState(() => draft?.question || loadPendingQuestion());
  const [lines, setLines] = useState<CastLine[]>(() => draft?.lines ?? []);
  const [faces, setFaces] = useState(EMPTY_FACES);
  const [lands, setLands] = useState<[number, number, number]>([0, 0, 0]);
  const [spinning, setSpinning] = useState(false);
  const [latest, setLatest] = useState<CastLine | null>(null);
  const timer = useRef<number | null>(null);
  const lock = useRef(false);

  useEffect(() => {
    return () => {
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, []);

  const done = lines.length >= 6;
  const index = Math.min(lines.length, 5);
  const bits = `${lines
    .map((line) => (line.sum === 7 || line.sum === 9 ? "1" : "0"))
    .join("")}${" ".repeat(Math.max(0, 6 - lines.length))}`;
  const changing = [
    ...lines.map((line) => line.sum === 6 || line.sum === 9),
    ...Array(Math.max(0, 6 - lines.length)).fill(false),
  ];
  const revealed = latest ? interpretLine(latest, lines.length - 1) : null;

  function shake() {
    if (lock.current || lines.length >= 6) return;
    lock.current = true;
    const thrown = throwCoins();
    setSpinning(true);
    setLatest(null);
    setFaces(EMPTY_FACES);
    timer.current = window.setTimeout(() => {
      setLines((current) => {
        const next = [...current, thrown];
        saveDraft({ question, lines: next });
        return next;
      });
      setFaces(thrown.coins);
      const tilt = crypto.getRandomValues(new Uint8Array(3));
      setLands([
        (tilt[0] % 13) - 6,
        (tilt[1] % 13) - 6,
        (tilt[2] % 13) - 6,
      ]);
      setLatest(thrown);
      setSpinning(false);
      lock.current = false;
    }, 1180);
  }

  function finish() {
    if (lines.length !== 6 || lock.current) return;
    lock.current = true;
    const record = saveRecord({ question, lines });
    clearDraft();
    clearPendingQuestion();
    navigate(`/result/${record.id}`);
  }

  function abandon() {
    if (timer.current) window.clearTimeout(timer.current);
    clearDraft();
    clearPendingQuestion();
    navigate("/");
  }

  return (
    <div className="cast">
      <header className="cast-head">
        <p className="kicker">第 {done ? 6 : lines.length + 1} / 6 爻</p>
        <h1>{done ? "六爻已齐" : CAST_HINTS[index]}</h1>
        <p className="question-echo">{question ? `所问：${question}` : "所问留在心里。"}</p>
      </header>

      <div className="cast-stage">
        <aside className="cast-board">
          <HexFigure bits={bits} changing={changing} size="lg" label="正在形成的卦，初爻在下" />
          <ol className="board-list">
            {[5, 4, 3, 2, 1, 0].map((slot) => {
              const line = lines[slot];
              const info = line ? interpretLine(line, slot) : null;
              return (
                <li key={slot} className={info ? "filled" : ""}>
                  <span>{PLACES[slot]}</span>
                  <strong>{info ? `${info.name}${info.changing ? " · 动" : ""}` : "—"}</strong>
                </li>
              );
            })}
          </ol>
        </aside>

        <section className="cast-play">
          <div className="live" aria-live="polite">
            {spinning && <p>铜钱还在空中。</p>}
            {!spinning && revealed && (
              <p>
                {revealed.place} · {revealed.name}
                {revealed.changing ? " · 动" : ""}
                <span>{arithmetic(latest as CastLine)}</span>
              </p>
            )}
            {!spinning && !revealed && <p>三枚钱还没有落地。</p>}
          </div>
          <Coins faces={faces} spinning={spinning} lands={lands} />
          <div className="actions">
            {!done ? (
              <button type="button" className="btn" onClick={shake} disabled={spinning}>
                {spinning ? "摇动中" : `摇${PLACES[lines.length]}`}
              </button>
            ) : (
              <button type="button" className="btn" onClick={finish}>
                看这一卦
              </button>
            )}
            <button type="button" className="btn ghost" onClick={() => navigate("/")}>
              先放下
            </button>
          </div>
          <p className="fine">
            字为三，背为二。六是老阴，七是少阳，八是少阴，九是老阳。摇出的爻不再改。
            {lines.length > 0 && (
              <button type="button" className="text-btn" onClick={abandon}>
                放弃这次
              </button>
            )}
          </p>
        </section>
      </div>
    </div>
  );
}
