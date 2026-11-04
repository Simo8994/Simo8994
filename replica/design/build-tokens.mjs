// Genera tokens.css e tailwind.tokens.cjs da tokens.json. Uso: node replica/design/build-tokens.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const dir = dirname(fileURLToPath(import.meta.url));
const t = JSON.parse(readFileSync(join(dir, "tokens.json"), "utf8"));
const css = [":root {"];
for (const [k, v] of Object.entries(t.color)) css.push(`  --color-${k}: ${v};`);
for (const [k, v] of Object.entries(t.font)) css.push(`  --font-${k}: ${v};`);
for (const [k, v] of Object.entries(t.type)) {
  css.push(`  --text-${k}: ${v.size / 16}rem;`, `  --text-${k}-line: ${v.line / 16}rem;`, `  --text-${k}-weight: ${v.weight};`);
}
t.space.forEach((v, i) => css.push(`  --space-${i}: ${v / 16}rem;`));
for (const [k, v] of Object.entries(t.radius)) css.push(`  --radius-${k}: ${v}px;`);
for (const [k, v] of Object.entries(t.shadow)) css.push(`  --shadow-${k}: ${v};`);
css.push(`  --motion-fast: ${t.motion.fast};`, `  --motion-base: ${t.motion.base};`, `  --motion-ease: ${t.motion.ease};`);
css.push(`  --layout-header: ${t.layout.header}px;`, `  --layout-sidebar: ${t.layout.sidebar}px;`,
         `  --layout-content-max: ${t.layout["content-max"]}px;`, `  --layout-board-column-min: ${t.layout["board-column-min"]}px;`);
css.push("}", "");
writeFileSync(join(dir, "tokens.css"), "/* Generato da tokens.json: non modificare a mano. */\n" + css.join("\n"));

const tw = {
  colors: Object.fromEntries(Object.keys(t.color).map((k) => [k, `var(--color-${k})`])),
  fontFamily: { sans: ["var(--font-sans)"], mono: ["var(--font-mono)"] },
  fontSize: Object.fromEntries(Object.keys(t.type).map((k) => [k, [`var(--text-${k})`, { lineHeight: `var(--text-${k}-line)`, fontWeight: `var(--text-${k}-weight)` }]])),
  spacing: Object.fromEntries(t.space.map((_, i) => [String(i), `var(--space-${i})`])),
  borderRadius: Object.fromEntries(Object.keys(t.radius).map((k) => [k, `var(--radius-${k})`])),
  boxShadow: Object.fromEntries(Object.keys(t.shadow).map((k) => [k, `var(--shadow-${k})`])),
  transitionDuration: { fast: "var(--motion-fast)", base: "var(--motion-base)" },
  transitionTimingFunction: { DEFAULT: "var(--motion-ease)" },
  screens: Object.fromEntries(Object.entries(t.layout.breakpoints).map(([k, v]) => [k, `${v}px`])),
};
writeFileSync(join(dir, "tailwind.tokens.cjs"),
  "// Generato da tokens.json. In tailwind.config: theme: require('./replica/design/tailwind.tokens.cjs')\n" +
  "module.exports = " + JSON.stringify(tw, null, 2) + ";\n");
console.log("ok: tokens.css, tailwind.tokens.cjs");
