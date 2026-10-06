// A clickable periodic table. Only elements listed in `groupOf` can be clicked; each is tinted with
// its group's color, and chosen elements get a thick outline. Clicking calls onPick(symbol).
const ROWS = [
  "H . . . . . . . . . . . . . . . . He",
  "Li Be . . . . . . . . . . B C N O F Ne",
  "Na Mg . . . . . . . . . . Al Si P S Cl Ar",
  "K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr",
  "Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe",
  "Cs Ba . Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn",
  "Fr Ra . Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og",
  "",
  ". . La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu .",
  ". . Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr .",
];

export default function PeriodicTable({ groupOf, colors, chosen, onPick }) {
  const cells = [];
  ROWS.forEach((row, r) =>
    row.split(" ").forEach((sym, c) => {
      if (!sym || sym === ".") return;
      const group = groupOf[sym];
      const classes = ["element", group ? "" : "inactive", chosen.includes(sym) ? "chosen" : ""];
      cells.push(
        <button key={sym} type="button" className={classes.join(" ").trim()}
                style={{ gridRow: r + 1, gridColumn: c + 1, background: group ? colors[group] : undefined }}
                title={group ? undefined : "Not part of this experiment"}
                aria-disabled={!group}
                onClick={group ? () => onPick(sym) : undefined}>
          {sym}
        </button>
      );
    })
  );
  return <div className="ptable">{cells}</div>;
}