import type { CoinFace } from "../lib/cast";

type Props = {
  faces: readonly [CoinFace | null, CoinFace | null, CoinFace | null];
  spinning: boolean;
  lands: readonly [number, number, number];
};

export function Coins({ faces, spinning, lands }: Props) {
  return (
    <div className="coins" aria-hidden={spinning}>
      {faces.map((face, index) => (
        <div
          key={index}
          className={`coin ${spinning ? "spin" : ""} ${face === 3 ? "is-yang" : face === 2 ? "is-yin" : "is-blank"}`}
          style={{
            animationDelay: `${index * 90}ms`,
            animationDuration: `${880 + index * 120}ms`,
            transform: spinning ? undefined : `rotate(${lands[index]}deg)`,
          }}
        >
          <svg viewBox="0 0 120 120" className="coin-svg">
            <circle cx="60" cy="60" r="56" className="coin-metal" />
            <circle cx="60" cy="60" r="46" className="coin-ring" />
            <rect x="48" y="48" width="24" height="24" className="coin-hole" />
            {face && (
              <text x="60" y="38" textAnchor="middle" className="coin-char">
                {face === 3 ? "字" : "背"}
              </text>
            )}
          </svg>
          <span className="coin-caption">{face === 3 ? "字 · 三" : face === 2 ? "背 · 二" : "未落"}</span>
        </div>
      ))}
    </div>
  );
}
