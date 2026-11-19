const sharp = require('sharp');
const fs = require('fs');
(async () => {
  const logo = fs.readFileSync('../../web/public/assets/wpninjas-logo.svg');
  await sharp(logo, { density: 400 }).png().toFile('logo-white.png');
  // Background art: night desert, saguaro silhouettes, a shield-grid horizon.
  const W = 1920, H = 1080;
  const sag = (x, base, h, s = 1) => {
    const w = 26 * s;
    return `<g fill="#0A0D14">
      <rect x="${x - w / 2}" y="${base - h}" width="${w}" height="${h}" rx="${w / 2}"/>
      <rect x="${x - w / 2 - 70 * s}" y="${base - h * 0.62}" width="${w * 0.8}" height="${h * 0.32}" rx="${w * 0.4}"/>
      <rect x="${x - w / 2 - 70 * s}" y="${base - h * 0.36}" width="${70 * s + 4}" height="${w * 0.8}" rx="${w * 0.4}"/>
      <rect x="${x + w / 2 + 44 * s}" y="${base - h * 0.78}" width="${w * 0.8}" height="${h * 0.4}" rx="${w * 0.4}"/>
      <rect x="${x + w / 2 - 4}" y="${base - h * 0.44}" width="${48 * s + 8}" height="${w * 0.8}" rx="${w * 0.4}"/>
    </g>`;
  };
  let grid = '';
  for (let i = -20; i <= 20; i++) grid += `<line x1="${960 + i * 40}" y1="820" x2="${960 + i * 260}" y2="1080" stroke="#FF7A2F" stroke-opacity="0.10" stroke-width="2"/>`;
  for (let j = 0; j < 7; j++) { const y = 820 + Math.pow(j / 6, 1.7) * 260; grid += `<line x1="0" y1="${y}" x2="1920" y2="${y}" stroke="#FF7A2F" stroke-opacity="0.10" stroke-width="2"/>`; }
  const svg = (withSag) => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#0B0F1A"/><stop offset="0.55" stop-color="#151A2E"/>
        <stop offset="0.74" stop-color="#3A1E2C"/><stop offset="0.80" stop-color="#7A3324"/><stop offset="0.83" stop-color="#0E1220"/>
        <stop offset="1" stop-color="#0B0F1A"/>
      </linearGradient>
      <radialGradient id="sun" cx="0.5" cy="0.78" r="0.35">
        <stop offset="0" stop-color="#FF7A2F" stop-opacity="0.55"/><stop offset="1" stop-color="#FF7A2F" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#sky)"/>
    <rect width="100%" height="100%" fill="url(#sun)"/>
    <path d="M0 830 L180 760 L330 800 L520 720 L700 790 L860 745 L1040 805 L1220 735 L1400 795 L1600 740 L1780 790 L1920 760 L1920 840 L0 840Z" fill="#1A1424" opacity="0.95"/>
    <rect y="836" width="1920" height="244" fill="#0B0F1A"/>
    ${grid}
    ${withSag ? sag(1640, 840, 300, 1.25) + sag(1820, 840, 200, 0.9) + sag(150, 840, 170, 0.8) : ''}
  </svg>`;
  await sharp(Buffer.from(svg(true))).jpeg({ quality: 88 }).toFile('bg-title.jpg');
  await sharp(Buffer.from(svg(false))).jpeg({ quality: 85 }).resize(1920, 1080).toFile('bg-section.jpg');
  await sharp(Buffer.from(svg(true))).webp({ quality: 70 }).toFile('../../web/public/assets/desert-night.webp');
  await sharp(Buffer.from(svg(true))).jpeg({ quality: 75 }).toFile('../../web/public/assets/desert-night.jpg');
  console.log('done');
})();
