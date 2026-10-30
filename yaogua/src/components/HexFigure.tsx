type Props = {
  bits: string;
  changing?: readonly boolean[];
  size?: "sm" | "md" | "lg";
  label?: string;
};

const POS = ["初", "二", "三", "四", "五", "上"];

export function HexFigure({ bits, changing, size = "md", label = "卦象" }: Props) {
  const order = [5, 4, 3, 2, 1, 0];
  return (
    <div className={`figure figure-${size}`} role="img" aria-label={label}>
      {order.map((index) => {
        const flag = bits[index];
        const yang = flag === "1";
        const known = flag === "1" || flag === "0";
        const moving = Boolean(changing?.[index]);
        return (
          <div
            key={index}
            className={`yao ${known ? (yang ? "yang" : "yin") : "ghost"} ${moving ? "move" : ""}`}
          >
            <span className="pos">{POS[index]}</span>
            <span className="bars" aria-hidden="true">
              {known && !yang ? (
                <>
                  <i />
                  <i />
                </>
              ) : (
                <i />
              )}
            </span>
            <span className="mark">{moving ? (yang ? "○" : "×") : ""}</span>
          </div>
        );
      })}
    </div>
  );
}
