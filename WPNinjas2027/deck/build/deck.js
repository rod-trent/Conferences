// deck.js - builds "Defender for Agents - WPNinjas US 2027.pptx"
//
//   cd WPNinjas2027/deck/build && npm install && node deck.js
//
// Structured deck: theme -> layouts with placeholders -> sections -> slides.
// Facts are from Microsoft Learn as of 19 Nov 2026; see ../../SOURCES.md.

const path = require("path");
const pptxgen = require("pptxgenjs");
const { icon } = require("./icons");

const SKILL = process.env.PPTX_SKILL_DIR;   // optional: path to apply_theme.js
const OUT = path.resolve(__dirname, "../../SlideDecks/Defender for Agents - WPNinjas US 2027.pptx");
const SITE = "github.com/rod-trent/Conferences/tree/main/WPNinjas2027";
const DEMO_SITE = "wpninjas2027-demos.vercel.app";

const THEME = {
  name: "WPNinjas Night Desert",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0B0F1A", lt1: "FFFFFF", dk2: "151B2C", lt2: "D7DCE8",
    accent1: "FF7A2F", accent2: "6FB7FF", accent3: "5AD18F", accent4: "F5B841",
    accent5: "FF5C6C", accent6: "94A0BC", hlink: "6FB7FF", folHlink: "94A0BC",
  },
};
const HEX = { line: "2A3352", raised: "1E2740", ink: "0B0F1A" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Defender for Agents: Extending Threat Protection to Autonomous Workflows";
pres.subject = "Workplace Ninjas US 2027";
pres.author = "Rod Trent";
pres.company = "Workplace Ninjas US 2027";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
// Roles, in scheme terms
const INK = C.text1, PANEL = C.text2, WHITE = C.background1, BODY = C.background2;
const EMBER = C.accent1, STEEL = C.accent2, OK = C.accent3, AMBER = C.accent4, RED = C.accent5, MUTED = C.accent6;

const W = 13.333, H = 7.5, M = 0.6;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "TITLE",
  background: { path: path.join(__dirname, "bg-title.jpg") },
  objects: [
    { image: { x: M, y: 0.55, w: 3.3, h: 0.45, path: path.join(__dirname, "logo-white.png") } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.75, w: 9.6, h: 1.9, fontSize: 52, bold: true,
      color: WHITE, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 3.75, w: 9.6, h: 0.9, fontSize: 26, color: EMBER,
      valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECTION",
  background: { path: path.join(__dirname, "bg-section.jpg") },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.95, w: 11.8, h: 1.8, fontSize: 46, bold: true,
      color: WHITE, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 3.95, w: 10.5, h: 0.8, fontSize: 22, color: BODY,
      valign: "top", align: "left", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: INK },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.85, fontSize: 32,
      bold: true, color: WHITE, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "Defender for Agents  ·  Workplace Ninjas US 2027", options: { x: M, y: 7.02, w: 6, h: 0.3,
      fontSize: 10, color: MUTED, margin: 0 } } },
    { image: { x: W - M - 1.6, y: 7.05, w: 1.6, h: 0.22, path: path.join(__dirname, "logo-white.png") } },
  ],
  slideNumber: { x: W - M - 2.3, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: MUTED, align: "right" },
});

// ---------------------------------------------------------------- helpers
let sectionTitle = "Opening";
function section(title) { sectionTitle = title; pres.addSection({ title }); }
function content(title, notes) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function txt(s, text, o) { s.addText(text, { isTextBox: true, margin: 0, fontSize: 16, color: BODY, valign: "top", ...o }); }
function card(s, x, y, w, h, opts = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.fill || PANEL }, line: { color: opts.line || HEX.line, width: 1 },
    objectName: opts.name || "card" });
}
async function badge(s, x, y, d, name, fill = EMBER) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" }, objectName: "icon-circle" });
  const pad = d * 0.24;
  s.addImage({ data: await icon(name, "#FFFFFF"), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, objectName: "icon-" + name });
}
function pill(s, x, y, text, color, w) {
  const ww = w || (0.18 + text.length * 0.085);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: ww, h: 0.32, rectRadius: 0.16, fill: { color }, line: { type: "none" } });
  s.addText(text, { isTextBox: true, x, y, w: ww, h: 0.32, fontSize: 11, bold: true, color: INK, align: "center", valign: "middle", margin: 0 });
  return ww;
}
function code(s, x, y, w, h, text, size = 12) {
  card(s, x, y, w, h, { fill: INK, line: HEX.line, name: "code" });
  s.addText(text, { isTextBox: true, x: x + 0.2, y: y + 0.15, w: w - 0.4, h: h - 0.3, fontFace: "Consolas", fontSize: size,
    color: BODY, valign: "top", margin: 0 });
}
function kicker(s, text, y = 1.25) { txt(s, text, { x: M, y, w: W - 2 * M, h: 0.4, fontSize: 16, color: EMBER, italic: true }); }

async function demoSlide(n, title, id, watch, variants, cmd, notes) {
  const s = content(`Demo ${n}  ·  ${title}`, notes);
  pill(s, M, 1.3, "LIVE DEMO", EMBER, 1.3);
  txt(s, [{ text: "Runs in the browser:  ", options: { color: MUTED } },
          { text: `${DEMO_SITE}/?demo=${id}`, options: { color: STEEL, hyperlink: { url: `https://${DEMO_SITE}/?demo=${id}` } } }],
    { x: M + 1.45, y: 1.3, w: 10.5, h: 0.32, fontSize: 14, valign: "middle" });
  // Left: what to watch
  card(s, M, 1.9, 7.0, 4.85);
  txt(s, "What to watch", { x: M + 0.35, y: 2.1, w: 6.4, h: 0.4, fontSize: 18, bold: true, color: WHITE });
  for (let i = 0; i < watch.length; i++) {
    const y = 2.65 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: M + 0.35, y, w: 0.5, h: 0.5, fill: { color: EMBER }, line: { type: "none" } });
    s.addText(String(i + 1), { isTextBox: true, x: M + 0.35, y, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: INK, align: "center", valign: "middle", margin: 0 });
    txt(s, [{ text: watch[i][0], options: { bold: true, color: WHITE, breakLine: true } },
            { text: watch[i][1], options: { color: BODY, fontSize: 14 } }],
      { x: M + 1.05, y: y - 0.05, w: 5.75, h: 1.2, fontSize: 16 });
  }
  // Right: variants
  card(s, M + 7.3, 1.9, W - 2 * M - 7.3, 4.85);
  txt(s, "Variants to click", { x: M + 7.6, y: 2.1, w: 4.3, h: 0.4, fontSize: 18, bold: true, color: WHITE });
  txt(s, variants.map((v, i) => ({ text: v, options: { bullet: true, breakLine: i < variants.length - 1 } })),
    { x: M + 7.6, y: 2.6, w: 4.3, h: 2.6, fontSize: 15, paraSpaceAfter: 6 });
  txt(s, "Offline, from the repo:", { x: M + 7.6, y: 5.3, w: 4.3, h: 0.3, fontSize: 12, color: MUTED });
  code(s, M + 7.6, 5.62, 4.3, 0.92, cmd, 11);
  return s;
}

// ---------------------------------------------------------------- slides
(async () => {
  // 1 ── Title
  section("Opening");
  {
    const s = pres.addSlide({ masterName: "TITLE", sectionTitle });
    s.addText("Defender for Agents", { placeholder: "title" });
    s.addText("Extending Threat Protection to Autonomous Workflows", { placeholder: "body" });
    txt(s, [{ text: "Rod Trent", options: { bold: true, color: WHITE, breakLine: true } },
            { text: "Workplace Ninjas US 2027  ·  Scottsdale, AZ  ·  11–13 January", options: { color: BODY } }],
      { x: M, y: 4.85, w: 8, h: 0.8, fontSize: 18 });
    s.addNotes("~1 min. Welcome. This is a 60-minute, demo-heavy session: six demos, all of which run in a browser with no tenant, so you can replay every one of them tonight from the repo. The thesis in one line: agents don't just answer, they act - and Microsoft Defender now inspects the action before it happens.");
  }

  // 2 ── Hook
  {
    const s = content("The agent read the email",
      "~3 min. Tell it as a story. An accounts-payable clerk asks a Copilot Studio agent to process the new invoices. One email from a 'vendor' carries an instruction hidden in invisible styling. The clerk sees a normal invoice. The agent sees an order: send the vendor master list for 'reconciliation'. Nobody jailbroke anything. Nobody even talked to the agent. That is indirect prompt injection, and it is the attack that matters for autonomous workflows. We will run this exact scenario in Demo 2.");
    const beats = [
      ["FaUserTie", "An AP clerk asks an agent to process the new invoices.", "An ordinary request, from an authorized user."],
      ["FaEnvelopeOpenText", "One email carries an instruction the clerk can't see.", "Hidden markup. Invisible to a person, plain text to a model."],
      ["FaPaperPlane", "The agent emails the vendor master list to a look-alike domain.", "With the agent's own, perfectly valid permissions."],
    ];
    for (let i = 0; i < beats.length; i++) {
      const y = 1.75 + i * 1.75;
      await badge(s, M, y, 0.9, beats[i][0]);
      txt(s, [{ text: beats[i][1], options: { bold: true, color: WHITE, breakLine: true } },
              { text: beats[i][2], options: { fontSize: 15, color: BODY } }], { x: M + 1.2, y: y + 0.02, w: 6.2, h: 1.2, fontSize: 19 });
    }
    card(s, 8.3, 1.75, 4.43, 4.4, { fill: PANEL });
    txt(s, "No one attacked the agent.", { x: 8.65, y: 2.25, w: 3.8, h: 1.0, fontSize: 28, bold: true, color: WHITE });
    txt(s, "Someone wrote it an email.", { x: 8.65, y: 3.35, w: 3.8, h: 1.0, fontSize: 28, bold: true, color: EMBER });
    txt(s, "Today: how Microsoft Defender sees that tool call - and stops it - before it runs.",
      { x: 8.65, y: 4.65, w: 3.8, h: 1.0, fontSize: 15, color: BODY });
  }

  // 3 ── About
  {
    const s = content("About me",
      "~1 min. Keep it short. Everything in this session is in the Conferences repo on GitHub - slides, demo code and the browser demo site. QR code is on the last slide.");
    s.addImage({ path: path.join(__dirname, "rod.png"), x: M + 0.2, y: 1.7, w: 3.6, h: 3.6, objectName: "speaker-photo" });
    txt(s, "Rod Trent", { x: 5.0, y: 1.9, w: 7.5, h: 0.8, fontSize: 40, bold: true, color: WHITE });
    txt(s, "Sr. Program Manager / Security MVP Program Lead, Microsoft", { x: 5.0, y: 2.75, w: 7.5, h: 0.5, fontSize: 20, color: EMBER });
    const rows = [["FaLinkedin", "linkedin.com/in/rodtrent"], ["FaXTwitter", "@rodtrent"], ["FaGithub", "github.com/rod-trent"]];
    for (let i = 0; i < rows.length; i++) {
      await badge(s, 5.0, 3.6 + i * 0.75, 0.5, rows[i][0], PANEL);
      txt(s, rows[i][1], { x: 5.7, y: 3.6 + i * 0.75, w: 6, h: 0.5, fontSize: 18, valign: "middle" });
    }
  }

  // 4 ── Agenda
  {
    const s = content("What we'll cover",
      "~1 min. Five parts, six demos. The demos are where the detail lives; the slides are the map.");
    const items = [
      ["Why agents change the threat model", "Apps answer, agents act. UPIA vs XPIA.", ""],
      ["The Defender map for agents", "Who protects what - and what changed in 2026.", ""],
      ["Shield the model", "Prompt Shields, Foundry guardrails, Defender for AI Services.", "Demo 1"],
      ["Runtime protection for autonomous workflows", "Copilot Studio, Foundry and the agent on your laptop.", "Demos 2–3"],
      ["Know, hunt, prove", "Inventory, identity, hunting, red teaming.", "Demos 4–6"],
    ];
    for (let i = 0; i < items.length; i++) {
      const y = 1.55 + i * 1.03;
      card(s, M, y, W - 2 * M, 0.85);
      txt(s, String(i + 1).padStart(2, "0"), { x: M + 0.3, y, w: 0.9, h: 0.85, fontSize: 30, bold: true, color: EMBER, valign: "middle" });
      txt(s, [{ text: items[i][0], options: { bold: true, color: WHITE } }, { text: "   " + items[i][1], options: { color: BODY, fontSize: 15 } }],
        { x: M + 1.3, y, w: 8.6, h: 0.85, fontSize: 20, valign: "middle" });
      if (items[i][2]) pill(s, W - M - 1.55, y + 0.26, items[i][2], STEEL, 1.3);
    }
  }

  // 5 ── Section 1
  section("01 Threat model");
  {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
    txt(s, "01", { x: M, y: 1.05, w: 2, h: 0.9, fontSize: 54, bold: true, color: EMBER });
    s.addText("Why agents change the threat model", { placeholder: "title" });
    s.addText("The input is untrusted, the plan is generated, and the tools are real.", { placeholder: "body" });
    s.addNotes("~0.5 min. Transition.");
  }

  // 6 ── Apps answer, agents act
  {
    const s = content("Apps answer. Agents act.",
      "~3 min. Walk the rows. The key row is the last one: when a traditional app fails you get an error; when an agent is injected you get a confident, authorized, wrong action - and every log line looks legitimate because the agent used its real permissions.");
    const rows = [
      ["Input", "Fixed forms and validated fields", "Natural language from anyone - plus every email, page and file it reads"],
      ["Logic", "Code you reviewed and tested", "A plan the model writes at runtime, every turn"],
      ["Actions", "Fixed API calls", "Tools chosen per turn: email, files, records, payments, a shell"],
      ["Identity", "A service account", "The user, the maker, or its own agent identity"],
      ["Failure", "A bug throws an error", "An injection produces a confident, authorized, wrong action"],
    ];
    const x0 = M, cw = [1.9, 4.3, 5.9];
    txt(s, "Traditional app", { x: x0 + cw[0], y: 1.45, w: cw[1], h: 0.4, fontSize: 16, bold: true, color: MUTED });
    txt(s, "AI agent", { x: x0 + cw[0] + cw[1], y: 1.45, w: cw[2], h: 0.4, fontSize: 16, bold: true, color: EMBER });
    for (let i = 0; i < rows.length; i++) {
      const y = 1.95 + i * 0.95;
      card(s, x0, y, W - 2 * M, 0.82, { fill: i === 4 ? HEX.raised : PANEL });
      txt(s, rows[i][0], { x: x0 + 0.3, y, w: cw[0] - 0.3, h: 0.82, fontSize: 17, bold: true, color: WHITE, valign: "middle" });
      txt(s, rows[i][1], { x: x0 + cw[0], y, w: cw[1] - 0.3, h: 0.82, fontSize: 15, color: MUTED, valign: "middle" });
      txt(s, rows[i][2], { x: x0 + cw[0] + cw[1], y, w: cw[2] - 0.3, h: 0.82, fontSize: 15, color: i === 4 ? WHITE : BODY, bold: i === 4, valign: "middle" });
    }
  }

  // 7 ── Attack surface
  {
    const s = content("Anatomy of an agent's attack surface",
      "~3 min. Six places to attack. Point out that only one of them - the model endpoint - is where traditional AI safety controls sat. The other five are where autonomous workflows get hurt. Each card names the Defender or Microsoft control we'll see later.");
    const cx = W / 2, cy = 4.2;
    s.addShape(pres.shapes.OVAL, { x: cx - 1.05, y: cy - 1.05, w: 2.1, h: 2.1, fill: { color: EMBER }, line: { type: "none" }, objectName: "agent-core" });
    s.addImage({ data: await icon("FaRobot", "#0B0F1A"), x: cx - 0.45, y: cy - 0.75, w: 0.9, h: 0.9 });
    txt(s, "Agent", { x: cx - 1.0, y: cy + 0.2, w: 2.0, h: 0.4, fontSize: 18, bold: true, color: INK, align: "center" });
    const parts = [
      ["FaFileLines", "Instructions", "Leakage, weak boundaries"],
      ["FaBookOpen", "Knowledge", "Email, SharePoint, web: indirect injection"],
      ["FaToolbox", "Tools and MCP", "Excessive agency, exfiltration"],
      ["FaIdBadge", "Identity", "Whose permissions does it use?"],
      ["FaBolt", "Triggers", "An email starts it - no human in the loop"],
      ["FaMicrochip", "Model endpoint", "Jailbreak, recon, wallet abuse"],
    ];
    const pos = [[M, 1.55], [M, 3.55], [M, 5.55], [W - M - 4.0, 1.55], [W - M - 4.0, 3.55], [W - M - 4.0, 5.55]];
    for (let i = 0; i < parts.length; i++) {
      const [x, y] = pos[i];
      card(s, x, y, 4.0, 1.2);
      await badge(s, x + 0.25, y + 0.3, 0.6, parts[i][0], i < 3 ? STEEL : EMBER);
      txt(s, [{ text: parts[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: parts[i][2], options: { fontSize: 14 } }],
        { x: x + 1.05, y: y + 0.17, w: 2.8, h: 0.9, fontSize: 17 });

    }
  }

  // 8 ── UPIA vs XPIA
  {
    const s = content("Two ways in: UPIA and XPIA",
      "~3 min. Use Microsoft's own terms - Prompt Shields calls them user prompt attacks and document attacks; Copilot Studio calls them UPIA and XPIA. The punchline is the defaults: in Foundry, user prompt attack detection is on by default and document attack detection is off by default. For an agent that reads email, the default protects you from the wrong attacker.");
    const cols = [
      { x: M, ic: "FaUserSecret", col: STEEL, h: "User prompt attack (UPIA)", sub: "The user is the attacker",
        b: ["Attempt to change system rules", "Embedding a conversation mockup", "Role-Play", "Encoding Attacks"],
        foot: "Foundry default: ON", footCol: OK },
      { x: W / 2 + 0.15, ic: "FaEnvelopeOpenText", col: EMBER, h: "Document attack (XPIA)", sub: "The attacker writes what the agent reads",
        b: ["Manipulated Content", "Information Gathering", "Fraud, Malware, Availability", "Access to system infrastructure"],
        foot: "Foundry default: OFF", footCol: RED },
    ];
    for (const c of cols) {
      const w = W / 2 - M - 0.15;
      card(s, c.x, 1.5, w, 4.55);
      await badge(s, c.x + 0.35, 1.8, 0.8, c.ic, c.col);
      txt(s, [{ text: c.h, options: { bold: true, color: WHITE, breakLine: true } }, { text: c.sub, options: { color: c.col, fontSize: 15 } }],
        { x: c.x + 1.35, y: 1.8, w: w - 1.6, h: 0.9, fontSize: 21 });
      txt(s, c.b.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < c.b.length - 1 } })),
        { x: c.x + 0.4, y: 2.95, w: w - 0.8, h: 2.0, fontSize: 16, paraSpaceAfter: 6 });
      pill(s, c.x + 0.4, 5.4, c.foot, c.footCol, 2.4);
    }
    txt(s, "For autonomous workflows XPIA is the main event: the attacker never talks to your agent.",
      { x: M, y: 6.3, w: W - 2 * M, h: 0.45, fontSize: 17, bold: true, color: WHITE });
  }

  // 9 ── OWASP mapping
  {
    const s = content("Map the risks to controls",
      "~2 min. Anchor on OWASP's Top 10 for LLM Applications (2025) so the room has a shared vocabulary. Each row is a control we'll see. LLM10 is the sleeper: the Defender for AI 'Suspected wallet attack' alerts are an unbounded-consumption detection.");
    const rows = [
      ["LLM01", "Prompt Injection", "Prompt Shields  ·  Defender for AI Services alerts  ·  real-time tool-call protection"],
      ["LLM02", "Sensitive Information Disclosure", "'Secret exfiltration' detection  ·  Purview DLP  ·  redacted prompt evidence"],
      ["LLM06", "Excessive Agency", "Tool allow-lists  ·  custom BLOCK rules  ·  human-in-the-loop for MCP tool actions"],
      ["LLM07", "System Prompt Leakage", "Jailbreak detection  ·  'Weak Instructions' risk indicator"],
      ["LLM10", "Unbounded Consumption", "'Suspected wallet attack' alerts (recurring requests, volume anomaly)"],
    ];
    for (let i = 0; i < rows.length; i++) {
      const y = 1.5 + i * 1.0;
      card(s, M, y, W - 2 * M, 0.85);
      pill(s, M + 0.3, y + 0.26, rows[i][0], EMBER, 1.0);
      txt(s, rows[i][1], { x: M + 1.55, y, w: 3.6, h: 0.85, fontSize: 17, bold: true, color: WHITE, valign: "middle" });
      txt(s, rows[i][2], { x: M + 5.3, y, w: 6.6, h: 0.85, fontSize: 15, valign: "middle" });
    }
    txt(s, "Risk names: OWASP Top 10 for LLM Applications 2025.", { x: M, y: 6.55, w: 8, h: 0.3, fontSize: 11, color: MUTED });
  }

  // 10 ── Section 2
  section("02 Defender map");
  {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
    txt(s, "02", { x: M, y: 1.05, w: 2, h: 0.9, fontSize: 54, bold: true, color: EMBER });
    s.addText("The Defender map for agents", { placeholder: "title" });
    s.addText("Eight places Microsoft security meets an agent - and the 2026 changes that moved them.", { placeholder: "body" });
    s.addNotes("~0.5 min. Transition.");
  }

  // 11 ── Control map
  {
    const s = content("Where Microsoft security meets the agent",
      "~3 min. This is the map for the rest of the session. Left column is build and posture; right column is runtime and response. Note the split between MODEL protection (Defender for Cloud - Defender for AI Services) and AGENT protection (Defender XDR real-time protection, Agent 365-licensed since July). People confuse these constantly.");
    const items = [
      ["FaShieldHalved", "Model guardrails", "Prompt Shields + Foundry guardrails at user input, tool call, tool response, output"],
      ["FaCloud", "Model threat protection", "Defender for Cloud - Defender for AI Services (Azure OpenAI, Foundry Models)"],
      ["FaListCheck", "Inventory and posture", "Defender portal: Assets > AI agents  ·  Defender CSPM AI-SPM"],
      ["FaIdBadge", "Identity", "Microsoft Entra Agent ID, Conditional Access, ID Protection for agents"],
      ["FaBolt", "Agent runtime protection", "Defender XDR real-time protection rules: Copilot Studio, Foundry, Agent 365 tooling servers"],
      ["FaLaptopCode", "Endpoint agents", "Defender for Endpoint AI agent runtime protection (Preview)"],
      ["FaDatabase", "Data", "Microsoft Purview DSPM (AI observability), DLP, Insider Risk"],
      ["FaMagnifyingGlass", "SOC", "Defender XDR incidents and advanced hunting: AgentsInfo, BehaviorInfo, CloudAppEvents"],
    ];
    const colW = (W - 2 * M - 0.3) / 2;
    for (let i = 0; i < items.length; i++) {
      const col = i % 2, row = Math.floor(i / 2);
      const x = M + col * (colW + 0.3), y = 1.75 + row * 1.25;
      card(s, x, y, colW, 1.1);
      await badge(s, x + 0.25, y + 0.22, 0.65, items[i][0], col ? EMBER : STEEL);
      txt(s, [{ text: items[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: items[i][2], options: { fontSize: 13 } }],
        { x: x + 1.1, y: y + 0.1, w: colW - 1.3, h: 0.95, fontSize: 17 });
    }
    txt(s, "Build and posture", { x: M, y: 1.35, w: 3, h: 0.3, fontSize: 13, color: STEEL, bold: true });
    txt(s, "Runtime and response", { x: M + colW + 0.3, y: 1.35, w: 3, h: 0.3, fontSize: 13, color: EMBER, bold: true });
  }

  // 12 ── What changed in 2026
  {
    const s = content("What changed in 2026 - read this before you plan",
      "~3 min. This slide saves people from following 2025 blog posts. Big one: since July 1, 2026, agent security for Copilot Studio and Foundry agents requires a Microsoft Agent 365 license; Defender for AI Services still covers the MODELS. Second: the old Copilot Studio onboarding retires December 23, 2026 - three weeks before this event. If you set it up the old way and didn't create blocking rules, your agents are now in audit mode. Verify current status on Learn the week of the event.");
    const ev = [
      ["Feb 2", "Threat protection for AI agents (Preview) added to Defender for AI Services for Foundry agents"],
      ["Mar 18", "Copilot Studio agents created from here get Microsoft Entra agent IDs (tenant opt-in)"],
      ["Jul 1", "Agent security for Copilot Studio and Foundry agents requires Microsoft Agent 365. AIAgentsInfo replaced by AgentsInfo. One 'Security for AI Agents' toggle"],
      ["Nov 22", "Automatic tenant-level onboarding for real-time protection rolls out (public preview)"],
      ["Dec 23", "Legacy Copilot Studio onboarding retires. Agents without an enabled blocking rule run in audit mode"],
    ];
    s.addShape(pres.shapes.LINE, { x: M + 1.2, y: 1.6, w: 0, h: 4.6, line: { color: HEX.line, width: 2 } });
    for (let i = 0; i < ev.length; i++) {
      const y = 1.5 + i * 0.95;
      txt(s, ev[i][0], { x: M, y, w: 1.0, h: 0.5, fontSize: 17, bold: true, color: i >= 2 ? EMBER : STEEL, align: "right" });
      s.addShape(pres.shapes.OVAL, { x: M + 1.08, y: y + 0.1, w: 0.25, h: 0.25, fill: { color: i >= 2 ? EMBER : STEEL }, line: { type: "none" } });
      txt(s, ev[i][1], { x: M + 1.55, y, w: 6.3, h: 0.85, fontSize: 15, color: i === 2 || i === 4 ? WHITE : BODY, bold: i === 2 || i === 4 });
    }
    card(s, 8.75, 1.5, W - M - 8.75, 4.7, { fill: PANEL });
    await badge(s, 9.05, 1.8, 0.7, "FaTriangleExclamation", AMBER);
    txt(s, "What did not move", { x: 9.9, y: 1.9, w: 2.7, h: 0.5, fontSize: 19, bold: true, color: WHITE });
    txt(s, [
      { text: "Defender for AI Services still protects Foundry Models such as Azure OpenAI.", options: { bullet: true, breakLine: true } },
      { text: "Defender CSPM still discovers Foundry accounts and projects.", options: { bullet: true, breakLine: true } },
      { text: "Agent-level discovery, posture and threat detection now come with Agent 365.", options: { bullet: true } },
    ], { x: 9.05, y: 2.75, w: 3.5, h: 3.2, fontSize: 15, paraSpaceAfter: 8 });
    txt(s, "All dates 2026. Source: Microsoft Learn, checked 19 Nov 2026.", { x: M, y: 6.55, w: 8, h: 0.3, fontSize: 11, color: MUTED });
  }

  // 13 ── Section 3
  section("03 Shield the model");
  {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
    txt(s, "03", { x: M, y: 1.05, w: 2, h: 0.9, fontSize: 54, bold: true, color: EMBER });
    s.addText("Shield the model", { placeholder: "title" });
    s.addText("Prompt Shields annotates. Defender for AI Services alerts. The SOC acts.", { placeholder: "body" });
    s.addNotes("~0.5 min. Transition.");
  }

  // 14 ── Prompt Shields
  {
    const s = content("Prompt Shields: what comes back",
      "~3 min. Show the annotation shape - this is what your app and Defender both see. 'filtered' means the guardrail blocked; 'detected' means it noticed. The standalone Content Safety API takes one user prompt plus up to five documents and only returns attackDetected - it never blocks anything itself; your code decides. Spotlighting is useful for chat completions but is not supported for agents.");
    code(s, M, 1.5, 6.0, 4.4,
`"prompt_filter_results": [{
  "prompt_index": 0,
  "content_filter_results": {
    "jailbreak": {
      "filtered": true,
      "detected": true
    },
    "indirect_attack": {
      "filtered": false,
      "detected": true
    }
  }
}]`, 15);
    txt(s, "Azure OpenAI / Foundry annotation shape", { x: M, y: 6.0, w: 6, h: 0.3, fontSize: 12, color: MUTED });
    const facts = [
      ["FaCodeBranch", "Two ways to call it", "As a guardrail on the deployment (annotate or block), or the standalone API: 1 user prompt + up to 5 documents -> attackDetected."],
      ["FaEyeSlash", "Spotlighting (preview)", "Base64-encodes documents so the model treats them as lower trust. Chat Completions only; not supported for agents."],
      ["FaLanguage", "Know the limits", "Primarily trained and evaluated on English. It detects attacks - not harm, groundedness or policy."],
    ];
    for (let i = 0; i < facts.length; i++) {
      const y = 1.5 + i * 1.5;
      card(s, 6.95, y, W - M - 6.95, 1.33);
      await badge(s, 7.2, y + 0.3, 0.7, facts[i][0], i === 2 ? AMBER : STEEL);
      txt(s, [{ text: facts[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: facts[i][2], options: { fontSize: 13 } }],
        { x: 8.1, y: y + 0.12, w: W - M - 8.3, h: 1.15, fontSize: 16 });
    }
  }

  // 15 ── Guardrail intervention points
  {
    const s = content("Foundry guardrails: four places to stop an agent",
      "~3 min. The two middle boxes are the agent-specific ones - tool call and tool response, both preview and agents-only. The tool response point is where document attacks in tool output get scanned. Two rules people trip on: an agent guardrail fully overrides the model's guardrail, and agents only support 'annotate and block'.");
    const pts = [["FaKeyboard", "User input", ""], ["FaWrench", "Tool call", "Preview · agents only"], ["FaReply", "Tool response", "Preview · agents only"], ["FaCommentDots", "Output", ""]];
    const bw = 2.6, gap = (W - 2 * M - 4 * bw) / 3;
    for (let i = 0; i < pts.length; i++) {
      const x = M + i * (bw + gap), y = 1.6;
      card(s, x, y, bw, 1.9, { fill: i === 1 || i === 2 ? HEX.raised : PANEL, line: i === 1 || i === 2 ? "FF7A2F" : HEX.line });
      await badge(s, x + bw / 2 - 0.4, y + 0.25, 0.8, pts[i][0], i === 1 || i === 2 ? EMBER : STEEL);
      txt(s, pts[i][1], { x, y: y + 1.12, w: bw, h: 0.4, fontSize: 18, bold: true, color: WHITE, align: "center" });
      if (pts[i][2]) txt(s, pts[i][2], { x, y: y + 1.48, w: bw, h: 0.3, fontSize: 12, color: EMBER, align: "center" });
      if (i < 3) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + gap / 2 - 0.2, y: y + 0.8, w: 0.4, h: 0.3, fill: { color: MUTED }, line: { type: "none" } });
    }
    const facts = [
      ["Agent guardrails are in preview", "Apply to Foundry Agent Service agents - not to other agents registered in the Foundry Control Plane."],
      ["The agent guardrail wins", "It fully overrides the model deployment's guardrail. No custom guardrail? The agent inherits the model's (default: Microsoft.DefaultV2)."],
      ["Annotate and block only", "Agents don't support annotate-only. Risks include user prompt attacks, indirect attacks, PII and Task Adherence (preview)."],
    ];
    for (let i = 0; i < facts.length; i++) {
      const x = M + i * ((W - 2 * M + 0.3) / 3), w = (W - 2 * M - 0.6) / 3;
      card(s, x, 3.9, w, 2.55);
      txt(s, [{ text: facts[i][0], options: { bold: true, color: WHITE, breakLine: true } }, { text: facts[i][1], options: { fontSize: 14 } }],
        { x: x + 0.3, y: 4.1, w: w - 0.6, h: 2.2, fontSize: 17, paraSpaceAfter: 6 });
    }
  }

  // 16 ── Defender for AI Services
  {
    const s = content("Defender for AI Services: turn it on, then give it context",
      "~3 min. The plan is per subscription. Two settings matter for the SOC: suspicious prompt evidence (redacted, and if you turn it off Defender still analyses - you just can't see the prompt) and end-user context. Without UserSecurityContext, the alert shows your app server as the source - you can't act on the attacker. Demo 1 shows both.");
    txt(s, "Enable", { x: M, y: 1.45, w: 6, h: 0.4, fontSize: 18, bold: true, color: EMBER });
    txt(s, "Defender for Cloud > Environment settings > subscription > Defender plans > AI services = On",
      { x: M, y: 1.85, w: 6.0, h: 0.7, fontSize: 15, color: WHITE });
    const comps = [
      ["Suspicious prompt evidence", "Suspicious prompt and response segments on each alert, sensitive data redacted."],
      ["Data security for AI interactions", "Lets Purview see prompts and responses. A paid Purview feature."],
      ["AI model security (preview)", "Scans Azure Machine Learning models for malware and unsafe operators."],
    ];
    for (let i = 0; i < comps.length; i++) {
      const y = 2.7 + i * 1.05;
      card(s, M, y, 6.0, 0.92);
      txt(s, [{ text: comps[i][0], options: { bold: true, color: WHITE, breakLine: true } }, { text: comps[i][1], options: { fontSize: 13 } }],
        { x: M + 0.3, y: y + 0.08, w: 5.4, h: 0.8, fontSize: 15 });
    }
    txt(s, "Covers Azure OpenAI and Azure AI Model Inference models. Text tokens only. 30-day trial capped at 75 billion tokens scanned.",
      { x: M, y: 5.95, w: 6.0, h: 0.7, fontSize: 12, color: MUTED });
    txt(s, "Then tell it who the user is", { x: 7.0, y: 1.45, w: 5.7, h: 0.4, fontSize: 18, bold: true, color: EMBER });
    code(s, 7.0, 1.95, W - M - 7.0, 3.1,
`# Python SDK 1.61.1+, via extra_body
client.chat.completions.create(
  model="gpt-4.1-support",
  messages=messages,
  extra_body={"user_security_context": {
    "end_user_id": user.entra_object_id,
    "source_ip": request.remote_addr,
    "application_name": "TrailConcierge-Web",
  }})`, 13);
    txt(s, "REST: user_security_context { application_name, end_user_id, end_user_tenant_id (multitenant), source_ip }. All optional; end user + source IP is the useful minimum.",
      { x: 7.0, y: 5.2, w: W - M - 7.0, h: 0.9, fontSize: 13, color: BODY });
  }

  // 17 ── Alerts table
  {
    const s = content("The alerts that matter for agents",
      "~2 min. Read the names exactly - blocked versus detected is the difference between 'the guardrail stopped it' and 'the guardrail noticed it'. Anomalous tool invocation is the one that's most agent-shaped at the model layer. Not on the list: a stand-alone indirect-injection alert for model deployments - XPIA for agents is covered by Defender XDR runtime protection instead.");
    const hdr = ["Alert (verbatim)", "Alert type", "Severity"].map(t => ({ text: t, options: { bold: true, color: INK, fill: { color: EMBER } } }));
    const rows = [
      ["A Jailbreak attempt on an Azure AI model deployment was blocked by Azure AI Content Safety Prompt Shields", "AI.Azure_Jailbreak.ContentFiltering.BlockedAttempt", "Medium"],
      ["A Jailbreak attempt on an Azure AI model deployment was detected by Azure AI Content Safety Prompt Shields", "AI.Azure_Jailbreak.ContentFiltering.DetectedAttempt", "Medium"],
      ["ASCII Smuggling prompt injection detected", "AI.Azure_ASCIISmuggling", "High"],
      ["Anomalous tool invocation", "AI.Azure_AnomalousToolInvocation", "Low"],
      ["(Preview) LLM Reconnaissance Attempt Detected", "AI.Azure_LLMReconnaissance", "Low"],
      ["Detected credential theft attempts on an Azure AI model deployment", "AI.Azure_CredentialTheftAttempt", "Medium"],
      ["Suspected wallet attack - volume anomaly", "AI.Azure_DOWVolumeAnomaly", "Medium"],
      ["Corrupted AI application\\model\\data directed a phishing attempt at a user", "AI.Azure_MaliciousUrl.ModelResponse", "High"],
    ].map((r, i) => r.map((c, j) => ({ text: c, options: { color: j === 0 ? WHITE : BODY, fill: { color: i % 2 ? HEX.ink : "151B2C" },
      fontFace: j === 1 ? "Consolas" : undefined, fontSize: j === 1 ? 10.5 : 13 } })));
    s.addTable([hdr, ...rows], { x: M, y: 1.45, w: W - 2 * M, colW: [6.1, 5.0, 1.03], fontSize: 13, color: BODY,
      border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.5, valign: "middle", margin: [0.04, 0.1, 0.04, 0.1] });
    txt(s, "Defender for Cloud: alerts for AI services. Alerts flow to Defender XDR and correlate into incidents.",
      { x: M, y: 6.6, w: 10, h: 0.3, fontSize: 11, color: MUTED });
  }

  // 18 ── Demo 1
  await demoSlide(1, "Shield the Model, Alert the SOC", "shield",
    [["A jailbreak is blocked - and named exactly", "Annotation JSON, then the BlockedAttempt alert with user, IP and app."],
     ["Switch the guardrail to annotate-only", "Same prompt. Now it's DetectedAttempt - and the model answered."],
     ["ASCII smuggling, then no user context", "An invisible instruction caught; then the same alert with no one to act on."]],
    ["Jailbreak, guardrail blocks", "Annotate-only guardrail", "ASCII smuggling", "Attack in a grounding doc", "No user context", "Benign control"],
    "cd demos/01-shield-the-model\npython shield_and_alert.py --scenario smuggling",
    "~5 min. Run variant 1, pause at the WHY THIS MATTERS beats. Then annotate-only: point at the alert name changing from 'blocked' to 'detected'. Then ASCII smuggling: the prompt on screen looks clean - that's the point. If time is short skip 'Attack in a grounding doc'; it sets up Demo 2 anyway.");

  // 19 ── Section 4
  section("04 Runtime protection");
  {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
    txt(s, "04", { x: M, y: 1.05, w: 2, h: 0.9, fontSize: 54, bold: true, color: EMBER });
    s.addText("Runtime protection for autonomous workflows", { placeholder: "title" });
    s.addText("Judge the action, not just the words - before the tool runs.", { placeholder: "body" });
    s.addNotes("~0.5 min. Transition. Prompt filtering judges text. Runtime protection judges what the agent is about to DO.");
  }

  // 20 ── How a tool call gets a verdict
  {
    const s = content("How a tool call gets a verdict",
      "~3 min. Walk left to right. Every time the orchestrator considers a tool, it sends the plan - the user message, the agent's 'thought', previous tool outputs, the tool and its inputs - to Defender. Defender has under a second. Allowed: nothing visible happens. Blocked: the agent stops and tells the user the message was blocked, and an alert and behavior land in Defender. The trap: no answer within one second means ALLOW by default. Generative orchestration only - classic agents skip this entirely.");
    const steps = [
      ["FaUser", "User or trigger", "A request, or an email arriving"],
      ["FaBrain", "Orchestrator plans", "Chooses a tool and its inputs"],
      ["FaPaperPlane", "Plan sent to Defender", "POST /analyze-tool-execution"],
      ["FaScaleBalanced", "Verdict < 1,000 ms", "blockAction: true / false"],
    ];
    const bw = 2.7, gap = (W - 2 * M - 4 * bw) / 3;
    for (let i = 0; i < steps.length; i++) {
      const x = M + i * (bw + gap);
      card(s, x, 1.5, bw, 2.1);
      await badge(s, x + 0.3, 1.75, 0.7, steps[i][0], i === 3 ? EMBER : STEEL);
      txt(s, [{ text: steps[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: steps[i][2], options: { fontSize: 13 } }],
        { x: x + 0.3, y: 2.6, w: bw - 0.5, h: 0.9, fontSize: 16 });
      if (i < 3) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + gap / 2 - 0.2, y: 2.4, w: 0.4, h: 0.3, fill: { color: MUTED }, line: { type: "none" } });
    }
    const out = [
      [OK, "FaCircleCheck", "Allow", "The tool runs. Nothing visible to the user."],
      [RED, "FaBan", "Block", "The agent stops and tells the user their message was blocked. Behavior and alert in Defender."],
      [AMBER, "FaClock", "No answer in 1 second", "Default: ALLOW. Set error behavior to 'Block the query' to fail closed."],
    ];
    for (let i = 0; i < out.length; i++) {
      const x = M + i * ((W - 2 * M + 0.3) / 3), w = (W - 2 * M - 0.6) / 3;
      card(s, x, 3.95, w, 1.9);
      await badge(s, x + 0.3, 4.2, 0.6, out[i][1], out[i][0]);
      txt(s, [{ text: out[i][2], options: { bold: true, color: WHITE, breakLine: true } }, { text: out[i][3], options: { fontSize: 13 } }],
        { x: x + 1.1, y: 4.15, w: w - 1.3, h: 1.6, fontSize: 17 });
    }
    txt(s, "Body: plannerContext (userMessage, thought, chatHistory, previousToolOutputs), toolDefinition, inputValues, conversationMetadata. Generative orchestration only.",
      { x: M, y: 6.1, w: W - 2 * M, h: 0.55, fontSize: 12, color: MUTED });
  }

  // 21 ── Rules
  {
    const s = content("Rules decide: audit or block",
      "~3 min. The default rule audits everything - that's visibility, not protection. Custom rules block, and you scope them to agents - but only agents with a Microsoft Entra agent ID show up in the picker. That's the posture gap Demo 4 finds. Coverage differs by platform: Copilot Studio is tool invocations only. And the date: the legacy Copilot Studio onboarding retired December 23; agents without an enabled blocking rule are now in audit mode.");
    card(s, M, 1.5, 3.9, 2.4);
    pill(s, M + 0.3, 1.75, "DEFAULT RULE", AMBER, 1.6);
    txt(s, [{ text: "Audits all agents", options: { bold: true, color: WHITE, breakLine: true } },
            { text: "Records a behavior. Does not stop the action.", options: { fontSize: 14 } }], { x: M + 0.3, y: 2.25, w: 3.3, h: 1.5, fontSize: 18 });
    card(s, M + 4.1, 1.5, 3.9, 2.4, { fill: HEX.raised, line: "FF7A2F" });
    pill(s, M + 4.4, 1.75, "CUSTOM RULES", EMBER, 1.6);
    txt(s, [{ text: "Block before execution", options: { bold: true, color: WHITE, breakLine: true } },
            { text: "Scope: All, or specific agents - only agents with a Microsoft Entra agent ID appear.", options: { fontSize: 14 } }],
      { x: M + 4.4, y: 2.25, w: 3.3, h: 1.5, fontSize: 18 });
    txt(s, "Detection types", { x: M, y: 4.12, w: 8, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    const dt = ["Secret exfiltration", "Malicious content propagation", "Evasion techniques", "Unsafe email domain"];
    let px = M;
    for (let k = 0; k < dt.length; k++) {
      if (k === 2) px = M;
      px += pill(s, px, k < 2 ? 4.6 : 5.02, dt[k], STEEL, 3.0) + 0.15;
    }
    txt(s, "Settings > Security for AI > Policies & rules > Real-time protection > Create rule",
      { x: M, y: 5.45, w: 8, h: 0.4, fontSize: 14, color: BODY });
    txt(s, "Audit and block events are recorded as behaviors in BehaviorInfo.", { x: M, y: 5.75, w: 8, h: 0.4, fontSize: 14, color: BODY });
    card(s, 8.85, 1.5, W - M - 8.85, 4.4);
    txt(s, "Coverage", { x: 9.15, y: 1.7, w: 3.3, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    txt(s, [
      { text: "Agent 365 tooling servers (GA)", options: { bold: true, color: WHITE, breakLine: true } },
      { text: "Work IQ and custom MCP tools", options: { breakLine: true } },
      { text: " ", options: { fontSize: 6, breakLine: true } },
      { text: "Foundry agents (Preview)", options: { bold: true, color: WHITE, breakLine: true } },
      { text: "Requests, responses, tool invocations and responses", options: { breakLine: true } },
      { text: " ", options: { fontSize: 6, breakLine: true } },
      { text: "Copilot Studio agents (Preview)", options: { bold: true, color: WHITE, breakLine: true } },
      { text: "Tool invocations only", options: {} },
    ], { x: 9.15, y: 2.15, w: 3.3, h: 3.0, fontSize: 14 });
    card(s, M, 6.15, W - 2 * M, 0.6, { fill: HEX.raised, line: "F5B841" });
    txt(s, "Dec 23, 2026: legacy Copilot Studio onboarding retired. No enabled blocking rule = audit mode.",
      { x: M + 0.3, y: 6.15, w: W - 2 * M - 0.6, h: 0.6, fontSize: 15, bold: true, color: WHITE, valign: "middle" });
  }

  // 22 ── Demo 2
  await demoSlide(2, "Stop the Tool Call", "toolcall",
    [["The poisoned invoice email", "What the clerk sees vs what the agent reads. Then three tool calls, each sent to Defender."],
     ["SendEmail is blocked before it runs", "Unsafe email domain + Malicious content propagation. blockAction: true."],
     ["Now break it three ways", "Default rule (audit), no Entra agent ID, and a reply that arrives at 1.4 seconds."]],
    ["Custom block rule", "Default rule (audit)", "No Entra agent ID", "Late reply: fail-open", "Late reply: fail-closed", "Benign control"],
    "cd demos/02-stop-the-tool-call\npython runtime_protection.py --rule audit",
    "~6 min. The main demo. Run the block-rule variant fully. Then click 'Default rule (audit)' and stop on the verdict: the alert is accurate and the data is already gone. Then 'No Entra agent ID' - same outcome for a different reason. Finish with the fail-open variant - Defender would have blocked it but answered too late.");

  // 23 ── Endpoint agents
  {
    const s = content("The agent on your laptop",
      "~3 min. The autonomous workflow most of you already run isn't in the cloud - it's a coding agent in a developer's terminal with their tokens and a shell. Defender for Endpoint now inspects these (preview). Start in Audit as Microsoft recommends, but put a date on Block. And note the privacy difference: endpoint prompt evidence is not redacted, unlike the cloud setting. Also mention the identity angle: device-code phishing alerts for GitHub Copilot CLI with automatic disruption.");
    pill(s, M, 1.3, "PREVIEW", AMBER, 1.1);
    txt(s, "Microsoft Defender for Endpoint - AI agent runtime protection", { x: M + 1.25, y: 1.28, w: 9, h: 0.36, fontSize: 16, color: BODY, valign: "middle" });
    const how = [
      ["FaPlug", "Agent-native event inspection", "Through the vendor's event interface. Learn names Claude Code, Codex CLI and GitHub Copilot CLI."],
      ["FaNetworkWired", "Network inspection", "Agent-to-LLM traffic. Doesn't work with certificate pinning or HTTP/3."],
    ];
    for (let i = 0; i < how.length; i++) {
      const y = 1.9 + i * 1.45;
      card(s, M, y, 6.3, 1.3);
      await badge(s, M + 0.3, y + 0.3, 0.7, how[i][0], STEEL);
      txt(s, [{ text: how[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: how[i][2], options: { fontSize: 13 } }],
        { x: M + 1.25, y: y + 0.12, w: 4.85, h: 1.1, fontSize: 16 });
    }
    txt(s, "Modes", { x: M, y: 4.85, w: 3, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    let px = M;
    for (const [t, c] of [["Block", RED], ["Audit", AMBER], ["Disabled", MUTED]]) px += pill(s, px, 5.3, t, c, 1.2) + 0.15;
    txt(s, "Microsoft recommends starting in Audit. The setting is covered by tamper protection.", { x: M, y: 5.8, w: 6.3, h: 0.6, fontSize: 13 });
    card(s, 7.2, 1.9, W - M - 7.2, 1.45, { fill: HEX.raised, line: "FF7A2F" });
    txt(s, [{ text: "Alert: Suspicious AI prompt injection", options: { bold: true, color: WHITE, breakLine: true } },
            { text: "Block shows a message in the agent UI and a Windows toast. Correlated into incidents.", options: { fontSize: 14 } }],
      { x: 7.5, y: 2.05, w: W - M - 7.8, h: 1.2, fontSize: 18 });
    card(s, 7.2, 3.6, W - M - 7.2, 1.3);
    txt(s, [{ text: "Prompt evidence is NOT redacted", options: { bold: true, color: AMBER, breakLine: true } },
            { text: "Unlike the cloud-agent setting. Treat endpoint snippets as sensitive.", options: { fontSize: 13 } }],
      { x: 7.5, y: 3.75, w: W - M - 7.8, h: 1.0, fontSize: 16 });
    card(s, 7.2, 5.15, W - M - 7.2, 1.3);
    txt(s, [{ text: "Identity attacks on agents too", options: { bold: true, color: WHITE, breakLine: true } },
            { text: "'Suspected GitHub Copilot CLI device code phishing' (email, Teams), with automatic disruption.", options: { fontSize: 13 } }],
      { x: 7.5, y: 5.3, w: W - M - 7.8, h: 1.0, fontSize: 16 });
  }

  // 24 ── Demo 3
  await demoSlide(3, "The Agent on Your Laptop", "endpoint",
    [["A README the developer reviewed", "Clean in the editor. The agent receives an instruction in invisible Unicode tag characters."],
     ["Block, Audit, Disabled", "Same loop, three outcomes: stopped, recorded-after-the-fact, or nothing at all."],
     ["The agent ignores the block", "The documented preview issue - and why request-time checks still hold."]],
    ["Block mode", "Audit mode", "Disabled", "Agent ignores the block"],
    "cd demos/03-agent-on-the-endpoint\npython local_agent_protection.py --mode audit",
    "~4 min. Show Block first. Then Audit - pause on 'Audit told you exactly what happened. After it happened.' Then 'Agent ignores the block' - this models the documented known issue where an agent keeps processing a tool response after a post-response block; the curl|bash and the exfil are still stopped at request time.");

  // 25 ── Section 5
  section("05 Know, hunt, prove");
  {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
    txt(s, "05", { x: M, y: 1.05, w: 2, h: 0.9, fontSize: 54, bold: true, color: EMBER });
    s.addText("Know, hunt, prove", { placeholder: "title" });
    s.addText("You can't block an agent you can't find, can't scope, or never tested.", { placeholder: "body" });
    s.addNotes("~0.5 min. Transition.");
  }

  // 26 ── Inventory and risk
  {
    const s = content("Find every agent - then rank them",
      "~3 min. Assets > AI agents is the inventory across Copilot Studio, Foundry, Microsoft 365, supported non-Microsoft platforms and local agents. Each agent gets a risk level and the indicators behind it. The indicator to hunt for first is Indirect Prompt Injection Exposure combined with Privileged Business-system Access - an outsider can write to it and it can change a system of record.");
    txt(s, "Defender portal > Assets > AI agents > Agents", { x: M, y: 1.35, w: 8, h: 0.4, fontSize: 16, color: EMBER });
    txt(s, "Risk level", { x: M, y: 1.95, w: 4, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    const lv = [["High", RED], ["Medium", AMBER], ["Low", STEEL], ["No known risk", OK], ["Not evaluated", MUTED]];
    let px = M;
    for (const [t, c] of lv) px += pill(s, px, 2.4, t, c) + 0.15;
    txt(s, "Risk indicators (examples)", { x: M, y: 3.0, w: 6, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    const ind = [
      ["FaFileCircleExclamation", "Weak Instructions", "No explicit boundaries in the agent's instructions"],
      ["FaEnvelopeOpenText", "Indirect Prompt Injection Exposure", "Reads content an outsider can write"],
      ["FaBuildingColumns", "Privileged Business-system Access", "Can act on a system of record"],
      ["FaChartLine", "High-usage Agent", "Blast radius by volume"],
      ["FaBug", "Active Threat", "Has open alerts"],
    ];
    for (let i = 0; i < ind.length; i++) {
      const y = 3.5 + i * 0.62;
      await badge(s, M, y, 0.48, ind[i][0], i === 1 || i === 2 ? EMBER : PANEL);
      txt(s, [{ text: ind[i][1], options: { bold: true, color: WHITE } }, { text: "   " + ind[i][2], options: { fontSize: 13, color: BODY } }],
        { x: M + 0.65, y, w: 7.4, h: 0.48, fontSize: 15, valign: "middle" });
    }
    card(s, 8.75, 1.95, W - M - 8.75, 4.6);
    txt(s, "Hunting the same data", { x: 9.05, y: 2.15, w: 3.4, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    code(s, 9.05, 2.65, W - M - 9.35, 1.75, "AgentsInfo\n| summarize arg_max(\n    Timestamp, *) by AgentId\n| where LifecycleStatus\n    != \"Deleted\"", 12);
    txt(s, "AgentsInfo replaced AIAgentsInfo. Useful columns: EntraAgentId, Owners, SharedWith, Instructions, DeclaredTools, DeclaredDataSources, McpServers, Guardrails, ToolsAuthenticationType.",
      { x: 9.05, y: 4.55, w: W - M - 9.35, h: 1.9, fontSize: 13 });
  }

  // 27 ── Demo 4
  await demoSlide(4, "Find Every Agent", "posture",
    [["Eight agents, five platforms, one table", "AgentsInfo scored into risk levels and indicators by their Learn names."],
     ["The gaps posture doesn't show", "No Entra agent ID, no owner, maker credentials, shared with everyone."],
     ["Drill into one, then the KQL", "Every indicator explained - then the four queries behind the view."]],
    ["Inventory and risk", "Protection gaps only", "Drill into Vendor Desk", "The KQL behind it"],
    "cd demos/04-find-every-agent\npython agent_posture.py --gaps",
    "~3 min. Run inventory, pause on the High agents. Then 'Protection gaps only': Invoice Matcher and Q3 Promo Bot have no Entra agent ID - they can never appear in a custom block rule. Remember Q3 Promo Bot; it's the villain in Demo 5.");

  // 28 ── Identity
  {
    const s = content("Give agents an identity - then govern it",
      "~3 min. Entra Agent ID is how an agent becomes something you can target. It's available to all Entra customers; extending Entra security features to agents needs Agent 365 (in M365 E7 or as an add-on). Conditional Access targeting depends on how the agent signs in. ID Protection has risky-agent detections and a Risky Agents report. The Zero Trust page's line is the best summary of why risk-based CA matters.");
    const cols = [
      ["FaIdBadge", "Microsoft Entra Agent ID", ["Agent identities and agent identity blueprints", "Available to all Entra customers", "Security features via Agent 365 (M365 E7, or add-on to E5, A5, Business Premium)"]],
      ["FaUserLock", "Conditional Access for agents", ["Assignments > Users, agents, or workload identities > Agents", "On-behalf-of flows: policy targets the user", "Not applied when an agent uses API keys"]],
      ["FaUserSecret", "ID Protection: risky agents", ["Detections include Sign-in spike, Unfamiliar resource access, Suspicious credential usage", "Risky Agents report: Confirm compromise, Confirm safe, Dismiss risk, Disable"]],
    ];
    const w = (W - 2 * M - 0.6) / 3;
    for (let i = 0; i < cols.length; i++) {
      const x = M + i * (w + 0.3);
      card(s, x, 1.5, w, 4.1);
      await badge(s, x + 0.3, 1.8, 0.7, cols[i][0], i === 0 ? EMBER : STEEL);
      txt(s, cols[i][1], { x: x + 0.3, y: 2.65, w: w - 0.6, h: 0.5, fontSize: 18, bold: true, color: WHITE });
      txt(s, cols[i][2].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < cols[i][2].length - 1 } })),
        { x: x + 0.3, y: 3.2, w: w - 0.6, h: 2.3, fontSize: 14, paraSpaceAfter: 6 });
    }
    txt(s, [{ text: "“The logs say ‘compromised’ while the resource still says ‘yes.’”", options: { italic: true, color: WHITE } },
            { text: "   - Microsoft Learn, Zero Trust for AI", options: { fontSize: 12, color: MUTED } }],
      { x: M, y: 5.9, w: W - 2 * M, h: 0.7, fontSize: 18 });
  }

  // 29 ── Hunting + Demo 5
  await demoSlide(5, "Hunt the Agent Kill Chain", "hunt",
    [["Every AI and agent alert, one table", "AlertInfo: model alerts and endpoint agent alerts side by side."],
     ["Blocked vs audited behaviors", "BehaviorInfo - then CloudAppEvents shows the audited SendEmail succeeded."],
     ["Pivot and enrich", "The jailbreak IP probed two more agents. AgentsInfo shows why one leaked."]],
    ["Full hunt", "Hunt 3: after the audit", "Hunt 4: IP pivot", "KQL only (to paste)"],
    "cd demos/05-hunt-the-agent-kill-chain\npython hunt_agents.py --kql",
    "~5 min. Tables: AlertInfo, AlertEvidence, BehaviorInfo, CloudAppEvents (agent ActionTypes InvokeAgent, InferenceCall, ExecuteToolBySDK / ByGateway / ByMCPServer), AgentsInfo. The story: two controls held; the agent that leaked had no owner and no Entra agent ID, so it could never be in a block rule. Hand out the KQL variant - it's paste-ready. Column values in the sample are illustrative; check them in your tenant.");

  // 30 ── Red team + Demo 6
  {
    const s = content("Prove it: red-team every agent release",
      "~3 min, then demo ~4 min. The AI Red Teaming Agent in Foundry is built on PyRIT and reports Attack Success Rate. It can test agent-only risks - prohibited actions, sensitive data leakage, task adherence - and does XPIA by injecting into mock tool outputs. Supported targets are Foundry hosted agents; workflow agents and non-Foundry agents aren't. Then Demo 6: our own corpus through four layers, including the attacks that get through.");
    const facts = [
      ["FaCrosshairs", "AI Red Teaming Agent", "Microsoft Foundry, built on PyRIT. Key metric: Attack Success Rate (ASR)."],
      ["FaRobot", "Agent-only risk categories", "Prohibited actions, Sensitive data leakage, Task adherence (cloud only). XPIA via mock tool outputs."],
      ["FaChessKnight", "Attack strategies", "Jailbreak (UPIA), Indirect Jailbreak, AsciiSmuggler, Base64, Crescendo, Multi turn and more."],
      ["FaCircleExclamation", "Know the scope", "Foundry hosted prompt and container agents. Not workflow agents or non-Foundry agents."],
    ];
    for (let i = 0; i < facts.length; i++) {
      const y = 1.45 + i * 1.3;
      card(s, M, y, 6.6, 1.15);
      await badge(s, M + 0.25, y + 0.25, 0.65, facts[i][0], i === 3 ? AMBER : STEEL);
      txt(s, [{ text: facts[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: facts[i][2], options: { fontSize: 13 } }],
        { x: M + 1.1, y: y + 0.1, w: 5.3, h: 1.0, fontSize: 16 });
    }
    card(s, 7.5, 1.45, W - M - 7.5, 5.05, { fill: HEX.raised, line: "FF7A2F" });
    pill(s, 7.8, 1.7, "DEMO 6", EMBER, 1.0);
    txt(s, "Red-Team Your Agent", { x: 7.8, y: 2.15, w: 4.5, h: 0.5, fontSize: 21, bold: true, color: WHITE });
    txt(s, [
      { text: "12 attacks + 2 benign controls through 4 layers", options: { bullet: true, breakLine: true } },
      { text: "ASR per layer and overall", options: { bullet: true, breakLine: true } },
      { text: "Turn document shields off - the Foundry default - and watch a fraudulent refund get through", options: { bullet: true, breakLine: true } },
      { text: "Reports what it misses on purpose: Crescendo, non-English, a polite injection to an unknown domain", options: { bullet: true } },
    ], { x: 7.8, y: 2.75, w: 4.6, h: 2.6, fontSize: 14, paraSpaceAfter: 6 });
    txt(s, [{ text: `${DEMO_SITE}/?demo=redteam`, options: { hyperlink: { url: `https://${DEMO_SITE}/?demo=redteam` } } }],
      { x: 7.8, y: 5.05, w: 4.6, h: 0.35, fontSize: 13, color: STEEL });
    code(s, 7.8, 5.5, 4.6, 0.8, "cd demos/06-red-team-your-agent\npython red_team_agent.py --doc-shields-off", 11);
  }

  // 31 ── Monday morning
  section("Close");
  {
    const s = content("Monday morning: six moves",
      "~3 min. Leave them with a checklist. Order matters: inventory and identity first, because a block rule can only scope agents that have an Entra agent ID. Number 4 is time-critical: the December 23 retirement already happened, so any agent set up the old way without a blocking rule is in audit mode right now.");
    const items = [
      ["FaListCheck", "Inventory", "Open Assets > AI agents. Give every published agent an owner and an Entra agent ID - or retire it."],
      ["FaFileShield", "Shield documents", "Turn on Prompt Shields for document attacks for any agent that reads email, web pages or files."],
      ["FaCloud", "Enable and enrich", "Defender for AI Services with suspicious prompt evidence; pass UserSecurityContext from your apps."],
      ["FaBan", "Block, don't audit", "Create a custom real-time BLOCK rule for your High-risk agents. Decide fail-open vs fail-closed."],
      ["FaLaptopCode", "Cover the endpoint", "AI agent runtime protection in Audit on developer devices - with a date to move to Block."],
      ["FaCrosshairs", "Red-team releases", "Track ASR per release. Keep every miss as a regression test."],
    ];
    const colW = (W - 2 * M - 0.3) / 2;
    for (let i = 0; i < items.length; i++) {
      const col = i % 2, row = Math.floor(i / 2);
      const x = M + col * (colW + 0.3), y = 1.45 + row * 1.7;
      card(s, x, y, colW, 1.5);
      await badge(s, x + 0.3, y + 0.35, 0.75, items[i][0], i === 3 ? EMBER : STEEL);
      txt(s, [{ text: `${i + 1}. ${items[i][1]}`, options: { bold: true, color: WHITE, breakLine: true } }, { text: items[i][2], options: { fontSize: 14 } }],
        { x: x + 1.3, y: y + 0.15, w: colW - 1.55, h: 1.25, fontSize: 18 });
    }
  }

  // 32 ── Resources
  {
    const s = content("Take it home",
      "~1 min. Everything is in the repo: deck, six demos that run offline with no dependencies, the browser demo site, the KQL, and a sources file listing every Learn page used.");
    s.addImage({ path: path.join(__dirname, "qr-repo.png"), x: M, y: 1.5, w: 3.4, h: 3.4, objectName: "qr-repo" });
    txt(s, [{ text: "github.com/rod-trent/Conferences", options: { breakLine: true } }, { text: "  /tree/main/WPNinjas2027" }], { x: M, y: 5.05, w: 4.1, h: 0.6, fontSize: 13, color: STEEL });
    txt(s, [{ text: "Run the demos in your browser:", options: { color: MUTED, breakLine: true } },
            { text: DEMO_SITE, options: { color: EMBER, bold: true, hyperlink: { url: "https://" + DEMO_SITE } } }],
      { x: M, y: 5.8, w: 4.2, h: 0.6, fontSize: 13 });
    const links = [
      ["Threat protection for AI services", "learn.microsoft.com/azure/defender-for-cloud/ai-threat-protection"],
      ["Alerts for AI services", "learn.microsoft.com/azure/defender-for-cloud/alerts-ai-workloads"],
      ["Real-time protection for AI agents", "learn.microsoft.com/defender-xdr/security-for-ai/ai-agent-real-time-protection"],
      ["AI agent runtime protection (endpoint)", "learn.microsoft.com/defender-endpoint/ai-agent-runtime-protection-overview"],
      ["Prompt Shields", "learn.microsoft.com/azure/ai-services/content-safety/concepts/jailbreak-detection"],
      ["AgentsInfo table", "learn.microsoft.com/defender-xdr/advanced-hunting-agentsinfo-table"],
      ["AI Red Teaming Agent", "learn.microsoft.com/azure/foundry/concepts/ai-red-teaming-agent"],
    ];
    for (let i = 0; i < links.length; i++) {
      const y = 1.5 + i * 0.72;
      txt(s, [{ text: links[i][0], options: { bold: true, color: WHITE, breakLine: true } },
              { text: links[i][1], options: { color: STEEL, fontSize: 12, hyperlink: { url: "https://" + links[i][1] } } }],
        { x: 5.0, y, w: W - M - 5.0, h: 0.65, fontSize: 15 });
    }
  }

  // 33 ── Thanks
  {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
    s.addText("Thank you. Questions?", { placeholder: "title" });
    s.addText("Agents act. Defender now checks the action first - if you let it block.", { placeholder: "body" });
    txt(s, "Rod Trent  ·  linkedin.com/in/rodtrent  ·  @rodtrent", { x: M, y: 4.85, w: 10, h: 0.5, fontSize: 18, color: EMBER });
    s.addImage({ path: path.join(__dirname, "logo-white.png"), x: M, y: 0.6, w: 3.3, h: 0.45 });
    s.addNotes("Q&A. Remind them the demo site works offline once loaded, and the repo's SOURCES.md lists every Learn page so they can check for changes - this area moved a lot in 2026.");
  }

  await pres.writeFile({ fileName: OUT });
  if (SKILL) {
    const { applyTheme } = require(path.join(SKILL, "scripts/apply_theme.js"));
    await applyTheme(OUT, THEME);
  }
  console.log("wrote", OUT);
})().catch(e => { console.error(e); process.exit(1); });
