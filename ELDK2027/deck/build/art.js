// Background art for the deck and the demo site: a Nordic night over harbour
// rooflines, an aurora in the event's light blue, and a faint node graph in the
// sky (the agent mesh). Generic silhouettes - no real landmark.
const sharp = require("sharp");
const fs = require("fs");

const W = 1920, H = 1080, HORIZON = 820;

function rng(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

function skyline() {
  const r = rng(27);
  let x = 0, d = "";
  while (x < W) {
    const w = 40 + r() * 90;
    const h = 40 + r() * 120;
    const top = HORIZON - h;
    const kind = r();
    if (kind < 0.12) {
      // spire
      const cx = x + w / 2;
      d += `M${x} ${HORIZON} L${x} ${top} L${cx - 8} ${top} L${cx} ${top - 90 - r() * 60} L${cx + 8} ${top} L${x + w} ${top} L${x + w} ${HORIZON} Z `;
    } else if (kind < 0.55) {
      // gabled roof
      d += `M${x} ${HORIZON} L${x} ${top + 24} L${x + w / 2} ${top - 10} L${x + w} ${top + 24} L${x + w} ${HORIZON} Z `;
    } else {
      d += `M${x} ${HORIZON} L${x} ${top} L${x + w} ${top} L${x + w} ${HORIZON} Z `;
    }
    x += w + (r() < 0.2 ? 6 : 0);
  }
  return d;
}

function windows() {
  const r = rng(91);
  let s = "";
  for (let i = 0; i < 140; i++) {
    const x = r() * W, y = HORIZON - 10 - r() * 90;
    s += `<rect x="${x.toFixed(0)}" y="${y.toFixed(0)}" width="5" height="7" fill="#F5C66B" opacity="${(0.25 + r() * 0.5).toFixed(2)}"/>`;
  }
  return s;
}

function mesh() {
  const r = rng(5);
  const pts = Array.from({ length: 26 }, () => [r() * W, 60 + r() * 520]);
  let s = "";
  pts.forEach((a, i) => pts.slice(i + 1).forEach((b) => {
    const dd = Math.hypot(a[0] - b[0], a[1] - b[1]);
    if (dd < 260) s += `<line x1="${a[0].toFixed(0)}" y1="${a[1].toFixed(0)}" x2="${b[0].toFixed(0)}" y2="${b[1].toFixed(0)}" stroke="#7FD0FF" stroke-opacity="0.10" stroke-width="1.5"/>`;
  }));
  pts.forEach((p) => (s += `<circle cx="${p[0].toFixed(0)}" cy="${p[1].toFixed(0)}" r="3" fill="#7FD0FF" fill-opacity="0.35"/>`));
  return s;
}

const svg = (city) => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#060B1F"/><stop offset="0.55" stop-color="#0E1A47"/>
      <stop offset="0.76" stop-color="#1D3380"/><stop offset="1" stop-color="#060B1F"/>
    </linearGradient>
    <linearGradient id="aur" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#008BD2" stop-opacity="0"/>
      <stop offset="0.35" stop-color="#008BD2" stop-opacity="0.55"/>
      <stop offset="0.6" stop-color="#3FD1C6" stop-opacity="0.40"/>
      <stop offset="1" stop-color="#008BD2" stop-opacity="0"/>
    </linearGradient>
    <filter id="blur"><feGaussianBlur stdDeviation="38"/></filter>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0B1538"/><stop offset="1" stop-color="#050916"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#sky)"/>
  <g filter="url(#blur)">
    <path d="M-100 360 C 300 220, 700 470, 1100 300 S 1800 200, 2050 330 L 2050 420 C 1700 330, 1400 520, 1000 420 S 300 360, -100 470 Z" fill="url(#aur)"/>
    <path d="M-100 250 C 400 160, 900 330, 1400 210 S 1900 170, 2050 230 L 2050 270 C 1600 250, 1300 340, 900 300 S 200 230, -100 300 Z" fill="url(#aur)" opacity="0.6"/>
  </g>
  ${mesh()}
  ${city ? `<path d="${skyline()}" fill="#050A1C"/>${windows()}` : ""}
  <rect y="${HORIZON}" width="${W}" height="${H - HORIZON}" fill="url(#water)"/>
  <rect y="${HORIZON}" width="${W}" height="3" fill="#008BD2" opacity="0.55"/>
  ${city ? `<g opacity="0.18">${windows().replace(/y="(\d+)"/g, (m, y) => `y="${2 * HORIZON - y + 12}"`)}</g>` : ""}
</svg>`;

(async () => {
  fs.mkdirSync("../../web/public/assets", { recursive: true });
  await sharp(Buffer.from(svg(true))).jpeg({ quality: 88 }).toFile("bg-title.jpg");
  await sharp(Buffer.from(svg(false))).jpeg({ quality: 85 }).toFile("bg-section.jpg");
  await sharp(Buffer.from(svg(true))).webp({ quality: 70 }).toFile("../../web/public/assets/nordic-night.webp");
  await sharp(Buffer.from(svg(true))).jpeg({ quality: 75 }).toFile("../../web/public/assets/nordic-night.jpg");
  fs.copyFileSync("logo-white.png", "../../web/public/assets/eldk-logo-white.png");
  console.log("done");
})();
