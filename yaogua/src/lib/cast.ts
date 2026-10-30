import { hexagramByBits, type Hexagram } from "../data/hexagrams";

export type CoinFace = 2 | 3;
export type LineSum = 6 | 7 | 8 | 9;

export type CastLine = {
  coins: [CoinFace, CoinFace, CoinFace];
  sum: LineSum;
};

const PLACES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"] as const;

const SUM_NAME: Record<LineSum, string> = {
  6: "老阴",
  7: "少阳",
  8: "少阴",
  9: "老阳",
};

export type LineInfo = {
  index: number;
  sum: LineSum;
  yang: boolean;
  changing: boolean;
  coins: [CoinFace, CoinFace, CoinFace];
  name: string;
  yao: string;
  place: string;
  mark: string;
};

export function throwCoins(): CastLine {
  const bytes = new Uint8Array(3);
  crypto.getRandomValues(bytes);
  const coins: [CoinFace, CoinFace, CoinFace] = [
    bytes[0] % 2 === 0 ? 3 : 2,
    bytes[1] % 2 === 0 ? 3 : 2,
    bytes[2] % 2 === 0 ? 3 : 2,
  ];
  const sum = (coins[0] + coins[1] + coins[2]) as LineSum;
  return { coins, sum };
}

export function yaoName(index: number, yang: boolean): string {
  const kind = yang ? "九" : "六";
  if (index === 0) return `初${kind}`;
  if (index === 5) return `上${kind}`;
  return `${kind}${["", "二", "三", "四", "五"][index]}`;
}

export function interpretLine(line: CastLine, index: number): LineInfo {
  const yang = line.sum === 7 || line.sum === 9;
  const changing = line.sum === 6 || line.sum === 9;
  return {
    index,
    sum: line.sum,
    yang,
    changing,
    coins: line.coins,
    name: SUM_NAME[line.sum],
    yao: yaoName(index, yang),
    place: PLACES[index],
    mark: line.sum === 9 ? "○" : line.sum === 6 ? "×" : "",
  };
}

export function coinWord(face: CoinFace): string {
  return face === 3 ? "字" : "背";
}

export function arithmetic(line: CastLine): string {
  const words = line.coins.map(coinWord).join(" ");
  const sumText = line.coins.join("+");
  return `${words} · ${sumText}=${line.sum}`;
}

export type ResolvedCast = {
  info: LineInfo[];
  bits: string;
  changedBits: string;
  primary: Hexagram;
  relating: Hexagram;
  moving: LineInfo[];
  quiet: boolean;
};

export function resolveCast(lines: CastLine[]): ResolvedCast {
  const info = lines.map(interpretLine);
  const bits = info.map((line) => (line.yang ? "1" : "0")).join("");
  const changedBits = info
    .map((line) => {
      const yang = line.changing ? !line.yang : line.yang;
      return yang ? "1" : "0";
    })
    .join("");
  const moving = info.filter((line) => line.changing);
  return {
    info,
    bits,
    changedBits,
    primary: hexagramByBits(bits),
    relating: hexagramByBits(changedBits),
    moving,
    quiet: moving.length === 0,
  };
}

export const CAST_HINTS = [
  "初爻在最下。先摇这一笔。",
  "二爻。铜钱仍问同一件事。",
  "三爻。内卦到这里齐。",
  "四爻。从这里进入外卦。",
  "五爻。位置高了，手可以轻。",
  "上爻。最后一次。",
];
