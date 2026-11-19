// deck.js - builds "The Agentic SOC - Experts Live Denmark 2027.pptx"
//
//   cd ELDK2027/deck/build && npm install && node deck.js
//
// Structured deck: theme -> layouts with placeholders -> sections -> slides.
// Facts are from Microsoft Learn as of 19 Nov 2026; see ../../SOURCES.md.

const path = require("path");
const pptxgen = require("pptxgenjs");
const { icon } = require("./icons");

const SKILL = process.env.PPTX_SKILL_DIR;   // optional: path to apply_theme.js
const OUT = path.resolve(__dirname, "../../SlideDecks/The Agentic SOC - Experts Live Denmark 2027.pptx");
const SITE = "github.com/rod-trent/Conferences/tree/main/ELDK2027";
const DEMO_SITE = "eldk2027-demos.vercel.app";

const SPEAKERS = [
  { name: "Rod Trent", title: "Sr. Program Manager, Microsoft", photo: "rod.png",
    links: [["FaLinkedin", "linkedin.com/in/rodtrent", "https://www.linkedin.com/in/rodtrent/"],
            ["FaXTwitter", "@rodtrent", "https://x.com/rodtrent"],
            ["FaGithub", "github.com/rod-trent", "https://github.com/rod-trent"]] },
];
const SPEAKER_NAMES = SPEAKERS.map(p => p.name).join("  ·  ");

const THEME = {
  name: "Experts Live Denmark Nordic Night",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "060B1F", lt1: "FFFFFF", dk2: "0F1A42", lt2: "D9E2F5",
    accent1: "2FA8E6", accent2: "7FD0FF", accent3: "5AD18F", accent4: "F5B841",
    accent5: "F0576B", accent6: "93A3CC", hlink: "7FD0FF", folHlink: "93A3CC",
  },
};
const HEX = { line: "23336E", raised: "16245A", ink: "060B1F", elblue: "1D3380" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "The Agentic SOC: Best Practices for Custom Agents, Role Handoffs, and Why Microsoft Perception Is More Supportable and Cost-Effective";
pres.subject = "Experts Live Denmark 2027";
pres.author = "Rod Trent";
pres.company = "Experts Live Denmark 2027";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const INK = C.text1, PANEL = C.text2, WHITE = C.background1, BODY = C.background2;
const BLUE = C.accent1, ICE = C.accent2, OK = C.accent3, AMBER = C.accent4, RED = C.accent5, MUTED = C.accent6;
const TEAM = { red: RED, blue: BLUE, green: OK };

const W = 13.333, H = 7.5, M = 0.6;
const LOGO_AR = 526 / 90;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "TITLE",
  background: { path: path.join(__dirname, "bg-title.jpg") },
  objects: [
    { image: { x: M, y: 0.55, w: 3.0, h: 3.0 / LOGO_AR, path: path.join(__dirname, "logo-white.png") } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.35, w: 9.4, h: 1.5, fontSize: 60, bold: true,
      color: WHITE, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 2.95, w: 9.4, h: 1.25, fontSize: 21, color: ICE,
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
    { text: { text: "The Agentic SOC  ·  Experts Live Denmark 2027", options: { x: M, y: 7.02, w: 6, h: 0.3,
      fontSize: 10, color: MUTED, margin: 0 } } },
    { image: { x: W - M - 1.55, y: 7.03, w: 1.55, h: 1.55 / LOGO_AR, path: path.join(__dirname, "logo-white.png") } },
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
function divider(n, title, sub, notes) {
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
  txt(s, n, { x: M, y: 1.05, w: 2, h: 0.9, fontSize: 54, bold: true, color: BLUE });
  s.addText(title, { placeholder: "title" });
  s.addText(sub, { placeholder: "body" });
  s.addNotes(notes);
  return s;
}
function txt(s, text, o) { s.addText(text, { isTextBox: true, margin: 0, fontSize: 16, color: BODY, valign: "top", ...o }); }
function card(s, x, y, w, h, opts = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.fill || PANEL }, line: { color: opts.line || HEX.line, width: 1 },
    objectName: opts.name || "card" });
}
async function badge(s, x, y, d, name, fill = BLUE) {
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
function bullets(s, items, o) {
  txt(s, items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { paraSpaceAfter: 6, ...o });
}
function arrow(s, x, y, w, color = BLUE) {
  s.addShape(pres.shapes.RIGHT_ARROW, { x, y, w, h: 0.32, fill: { color }, line: { type: "none" }, objectName: "arrow" });
}
async function iconCard(s, x, y, w, h, ic, head, body, col = BLUE, size = 14) {
  card(s, x, y, w, h);
  await badge(s, x + 0.25, y + 0.25, 0.62, ic, col);
  txt(s, head, { x: x + 1.05, y: y + 0.25, w: w - 1.3, h: 0.62, fontSize: 17, bold: true, color: WHITE, valign: "middle" });
  if (Array.isArray(body)) bullets(s, body, { x: x + 0.3, y: y + 1.05, w: w - 0.6, h: h - 1.2, fontSize: size });
  else txt(s, body, { x: x + 0.3, y: y + 1.05, w: w - 0.6, h: h - 1.2, fontSize: size });
}
function source(s, text) { txt(s, text, { x: M, y: 6.62, w: W - 2 * M, h: 0.3, fontSize: 10, color: MUTED, italic: true }); }

async function demoSlide(n, title, id, watch, variants, cmd, notes) {
  const s = content(`Demo ${n}  ·  ${title}`, notes);
  pill(s, M, 1.3, "LIVE DEMO", BLUE, 1.3);
  txt(s, [{ text: "Runs in the browser:  ", options: { color: MUTED } },
          { text: `${DEMO_SITE}/?demo=${id}`, options: { color: ICE, hyperlink: { url: `https://${DEMO_SITE}/?demo=${id}` } } }],
    { x: M + 1.45, y: 1.3, w: 10.5, h: 0.32, fontSize: 14, valign: "middle" });
  card(s, M, 1.9, 7.0, 4.85);
  txt(s, "What to watch", { x: M + 0.35, y: 2.1, w: 6.4, h: 0.4, fontSize: 18, bold: true, color: WHITE });
  for (let i = 0; i < watch.length; i++) {
    const y = 2.65 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: M + 0.35, y, w: 0.5, h: 0.5, fill: { color: BLUE }, line: { type: "none" } });
    s.addText(String(i + 1), { isTextBox: true, x: M + 0.35, y, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: INK, align: "center", valign: "middle", margin: 0 });
    txt(s, [{ text: watch[i][0], options: { bold: true, color: WHITE, breakLine: true } },
            { text: watch[i][1], options: { color: BODY, fontSize: 14 } }],
      { x: M + 1.05, y: y - 0.05, w: 5.75, h: 1.2, fontSize: 16 });
  }
  card(s, M + 7.3, 1.9, W - 2 * M - 7.3, 4.85);
  txt(s, "Variants to click", { x: M + 7.6, y: 2.1, w: 4.3, h: 0.4, fontSize: 18, bold: true, color: WHITE });
  bullets(s, variants, { x: M + 7.6, y: 2.6, w: 4.3, h: 2.6, fontSize: 15 });
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
    s.addText("The Agentic SOC", { placeholder: "title" });
    s.addText("Best Practices for Custom Agents, Role Handoffs, and Why Microsoft Perception Is More Supportable and Cost-Effective",
      { placeholder: "body" });
    txt(s, [{ text: SPEAKER_NAMES, options: { bold: true, color: WHITE, breakLine: true } },
            { text: "Experts Live Denmark 2027  ·  Bella Center Copenhagen  ·  #ELDK27", options: { color: BODY } }],
      { x: M, y: 4.45, w: 8, h: 0.8, fontSize: 18 });
    const tq = 1.9, tx = W - M - tq;
    s.addImage({ path: path.join(__dirname, "qr-demo-site.png"), x: tx, y: 0.55, w: tq, h: tq, objectName: "qr-demo-site",
      hyperlink: { url: "https://" + DEMO_SITE } });
    txt(s, [{ text: "Follow along", options: { bold: true, color: BLUE, breakLine: true } },
            { text: DEMO_SITE, options: { color: BODY, fontSize: 11, hyperlink: { url: "https://" + DEMO_SITE } } }],
      { x: tx - 0.4, y: 2.52, w: tq + 0.4, h: 0.6, fontSize: 15, align: "right" });
    s.addNotes("~1 min. Welcome. Point at the QR code: the demo site runs all six demos in the browser - real Python, no tenant - so the room can follow on their phones and replay everything tonight. Experts Live asks for less PowerPoint, more demos: six demos in 50 minutes, and they show the bad side as often as the good. The thesis: agents in the SOC are a design and operations problem before they are a model problem - and once you see what running your own costs, the build-vs-buy question answers itself for most teams.");
  }

  // 2 ── About
  {
    const s = content("About me",
      "~0.5 min. One line. Everything in this session is in the Conferences repo on GitHub - slides, the six demos, the browser demo site and a SOURCES file listing every Microsoft Learn page used.");
    const sp = SPEAKERS[0], x = M, y = 1.55, cw = 7.2;
    card(s, x, y, cw, 4.9);
    s.addImage({ path: path.join(__dirname, sp.photo), x: x + 0.4, y: y + 0.45, w: 2.5, h: 2.5, objectName: "speaker-photo" });
    txt(s, sp.name, { x: x + 3.2, y: y + 0.6, w: cw - 3.4, h: 0.6, fontSize: 30, bold: true, color: WHITE });
    txt(s, sp.title, { x: x + 3.2, y: y + 1.3, w: cw - 3.4, h: 0.5, fontSize: 17, color: BLUE });
    for (let j = 0; j < sp.links.length; j++) {
      const [ic, label, url] = sp.links[j], ly = y + 3.2 + j * 0.52;
      await badge(s, x + 0.4, ly, 0.42, ic, HEX.raised);
      txt(s, [{ text: label, options: { hyperlink: { url } } }], { x: x + 1.0, y: ly, w: cw - 1.3, h: 0.42, fontSize: 16, color: BODY, valign: "middle" });
    }
    s.addImage({ path: path.join(__dirname, "badge.png"), x: 8.75, y: 1.75, w: 3.4, h: 3.4, objectName: "eldk-badge" });
    txt(s, "Where the Microsoft Community Meets", { x: 7.9, y: 5.35, w: 5.1, h: 0.4, fontSize: 15, italic: true, color: MUTED, align: "center" });
  }

  // 3 ── Hook
  {
    const s = content("Every agent did its job",
      "~3 min. Tell it as a story; it's Demo 3's free-text variant. Two people in Finance and Procurement clicked a link in a genuine partner SharePoint share that chained to an adversary-in-the-middle page. The triage agent got it right. It handed off a nicely written summary. The investigation agent investigated every user it could resolve from that summary - one. Remediation contained one. Nobody made a mistake you could point at, and the attacker kept the other session. That's the session in one picture: in a multi-agent SOC the risk moves from the agents to the gaps between them.");
    const beats = [
      ["FaFilter", "Triage: true positive. Two users clicked.", "It handed off a well-written paragraph."],
      ["FaMagnifyingGlass", "Investigation: one user found and scoped.", "'Someone from procurement' is not an entity."],
      ["FaShieldHalved", "Remediation: one account contained.", "Approved, audited, correct - and incomplete."],
    ];
    for (let i = 0; i < beats.length; i++) {
      const y = 1.75 + i * 1.75;
      await badge(s, M, y, 0.9, beats[i][0]);
      txt(s, [{ text: beats[i][1], options: { bold: true, color: WHITE, breakLine: true } },
              { text: beats[i][2], options: { fontSize: 15, color: BODY } }], { x: M + 1.2, y: y + 0.02, w: 6.2, h: 1.2, fontSize: 19 });
    }
    card(s, 8.3, 1.75, 4.43, 4.4, { fill: PANEL });
    txt(s, "The attacker kept the second session.", { x: 8.65, y: 2.2, w: 3.8, h: 1.3, fontSize: 27, bold: true, color: WHITE });
    txt(s, "Multi-agent SOCs fail in the handoffs.", { x: 8.65, y: 3.55, w: 3.8, h: 1.0, fontSize: 24, bold: true, color: BLUE });
    txt(s, "Today: how to design the agents, the handoffs between them - and when to stop building them yourself.",
      { x: 8.65, y: 4.75, w: 3.8, h: 1.2, fontSize: 15, color: BODY });
  }

  // 4 ── Agenda
  {
    const s = content("What we'll cover",
      "~1 min. Four parts, six demos. The demos carry the detail; the slides are the map.");
    const items = [
      ["Design agents you can govern", "Identity, least privilege, evaluation, human in the loop, lifecycle.", "Demos 1–2"],
      ["Build your own SOC agents", "Triage → investigation → detection engineering → posture remediation.", "Demos 3–4"],
      ["Microsoft Perception", "Red, blue and green team agents, playbooks, supervision.", "Demo 5"],
      ["Build vs. buy", "Supportability, maintenance, three-year cost - and a framework.", "Demo 6"],
    ];
    for (let i = 0; i < items.length; i++) {
      const y = 1.6 + i * 1.25;
      card(s, M, y, W - 2 * M, 1.05);
      txt(s, String(i + 1).padStart(2, "0"), { x: M + 0.3, y, w: 0.9, h: 1.05, fontSize: 32, bold: true, color: BLUE, valign: "middle" });
      txt(s, [{ text: items[i][0], options: { bold: true, color: WHITE, breakLine: true } }, { text: items[i][1], options: { color: BODY, fontSize: 15 } }],
        { x: M + 1.3, y, w: 8.8, h: 1.05, fontSize: 21, valign: "middle" });
      pill(s, W - M - 1.6, y + 0.36, items[i][2], ICE, 1.35);
    }
  }

  // 5 ── Part 1
  section("01 Design");
  divider("01", "Design agents you can govern", "Decide identity, permissions, gates and tests before you write the prompt.",
    "~0.3 min. Transition. Everything in this part applies whether you build or buy - Perception's agents are judged by the same controls.");

  // 6 ── Identity
  {
    const s = content("Every agent is an identity",
      "~3 min. Entra Agent ID is GA and available to all Entra customers. A sponsor is required when you create an agent identity or blueprint - that's the person accountable for the agent, and they can disable it. Owners are the technical admins. Best practices page: don't create agents as plain app registrations; managed identity or certificates, not secrets; agents can't do MFA, so give them their own Conditional Access, report-only first. The gap to call out: in Security Copilot, 'Create an agent identity' is currently only for Microsoft-built agents. A custom agent runs as a user account and inherits that person's access - so make it a dedicated, least-privileged account, never your own.");
    await iconCard(s, M, 1.5, 3.85, 4.35, "FaIdBadge", "Microsoft Entra Agent ID",
      ["GA, available to all Entra customers", "A sponsor is required for every agent identity or blueprint", "Owners administer; sponsors are accountable and can disable", "Sponsors attest every 6–12 months"]);
    await iconCard(s, M + 4.1, 1.5, 3.85, 4.35, "FaKey", "How it signs in",
      ["Not a plain app registration", "Managed identity or certificate - not a client secret", "Agents can't satisfy MFA: agent-specific Conditional Access, report-only first", "CA for agents: M365 E7, or Agent 365 + Entra P1 / M365 E3"]);
    card(s, M + 8.2, 1.5, W - 2 * M - 8.2, 4.35, { fill: HEX.raised, line: "F5B841" });
    pill(s, M + 8.5, 1.8, "THE GAP", AMBER, 1.2);
    txt(s, "Custom Security Copilot agents", { x: M + 8.5, y: 2.3, w: 3.5, h: 0.5, fontSize: 17, bold: true, color: WHITE });
    txt(s, [{ text: "“Create an agent identity” is currently only available for Microsoft-built agents.", options: { italic: true, breakLine: true } },
            { text: " ", options: { breakLine: true } },
            { text: "The alternative - connect an existing user account - inherits that user's access. Use a dedicated, least-privileged account. Never your own.", options: {} }],
      { x: M + 8.5, y: 2.85, w: 3.5, h: 2.9, fontSize: 14 });
    source(s, "Sources: Entra Agent ID - what are agent identities; owners, sponsors and managers; best practices; Conditional Access for agents; Security Copilot agents overview.");
  }

  // 7 ── Least privilege + hard actions
  {
    const s = content("Least privilege, and a gate on every hard action",
      "~3 min. Use Microsoft's own agent as the template. The Phishing Triage Agent's documented permissions are read-mostly and scoped: it can manage alerts, and it can read email content only for emails associated with alerts. Then the rule: any agent that reads untrusted input - email, alerts, URLs, files - should be assumed injectable, so what you grant it is what an attacker gets. Hard actions are the irreversible or business-stopping ones; the Architecture Center says scope human-in-the-loop gates to sensitive tool invocations - not to everything, or the humans rubber-stamp.");
    card(s, M, 1.5, 5.9, 4.95);
    txt(s, "The template: Phishing Triage Agent", { x: M + 0.35, y: 1.7, w: 5.3, h: 0.45, fontSize: 18, bold: true, color: WHITE });
    const perms = [["Security data basics", "read"], ["Alerts", "manage"], ["Security Copilot", "read"],
                   ["Email & collaboration metadata", "read"], ["Emails associated with alerts", "read"]];
    for (let i = 0; i < perms.length; i++) {
      const y = 2.3 + i * 0.62;
      card(s, M + 0.35, y, 5.2, 0.5, { fill: INK });
      txt(s, perms[i][0], { x: M + 0.55, y, w: 3.8, h: 0.5, fontSize: 15, color: WHITE, valign: "middle" });
      pill(s, M + 4.45, y + 0.09, perms[i][1], perms[i][1] === "manage" ? AMBER : OK, 0.95);
    }
    txt(s, "Email content: only the emails tied to an alert. Not the mailbox.", { x: M + 0.35, y: 5.55, w: 5.2, h: 0.7, fontSize: 14, italic: true, color: ICE });
    const x2 = M + 6.2, w2 = W - M - x2;
    card(s, x2, 1.5, w2, 4.95);
    txt(s, "Hard actions need a human", { x: x2 + 0.35, y: 1.7, w: w2 - 0.7, h: 0.45, fontSize: 18, bold: true, color: WHITE });
    const hard = ["Isolate device", "Disable user", "Delete email", "Change Conditional Access", "Enable a detection rule"];
    for (let i = 0; i < hard.length; i++) pill(s, x2 + 0.35 + (i % 2) * 2.75, 2.3 + Math.floor(i / 2) * 0.48, hard[i], RED, 2.55);
    bullets(s, ["Assume any agent that reads email, alerts or URLs can be injected", "Grant what it uses - measure it from the audit log",
                "Gate the hard actions only; soft actions (tag, comment, block a URL) run", "Approvals carry the evidence, not just the request"],
      { x: x2 + 0.35, y: 3.85, w: w2 - 0.7, h: 2.5, fontSize: 15 });
    source(s, "Sources: Phishing Triage Agent (Defender XDR); AI agent orchestration patterns (Azure Architecture Center).");
  }

  // 8 ── Evaluation
  {
    const s = content("Evaluation is a release gate, not a report",
      "~3 min. Foundry's agent evaluators: Tool Call Accuracy, Tool Selection and Tool Input Accuracy carry no preview label; Task Adherence, Intent Resolution and Task Completion are preview. Intent Resolution and Tool Call Accuracy score 1-5 with a default pass threshold of 3. The AI Red Teaming Agent is built on PyRIT, reports Attack Success Rate, and has agent-only risk categories. The point of the slide is the right-hand card: average accuracy hides the error you cannot afford. For a triage agent that is a closed true positive. Make that the gate, zero, and re-run it on every prompt, model, tool or memory change. Demo 2 shows the threshold that breaks it.");
    await iconCard(s, M, 1.5, 3.85, 4.4, "FaListCheck", "Foundry agent evaluators",
      ["Tool Call Accuracy, Tool Selection, Tool Input Accuracy", "Task Adherence, Intent Resolution, Task Completion (preview)", "1–5 scale; default pass threshold 3"]);
    await iconCard(s, M + 4.1, 1.5, 3.85, 4.4, "FaCrosshairs", "AI Red Teaming Agent",
      ["Built on PyRIT; headline metric is Attack Success Rate (ASR)", "Agent risks: prohibited actions, sensitive data leakage, task adherence", "Indirect prompt injection (XPIA)"], ICE);
    card(s, M + 8.2, 1.5, W - 2 * M - 8.2, 4.4, { fill: HEX.raised, line: "2FA8E6" });
    txt(s, "Gate on the error you can't afford", { x: M + 8.5, y: 1.75, w: 3.5, h: 0.8, fontSize: 19, bold: true, color: WHITE });
    txt(s, "0", { x: M + 8.5, y: 2.6, w: 3.5, h: 1.2, fontSize: 80, bold: true, color: BLUE });
    txt(s, "true positives auto-closed - for a triage agent. Re-run on every prompt, model, tool or memory change.",
      { x: M + 8.5, y: 3.85, w: 3.5, h: 1.6, fontSize: 15 });
    source(s, "Sources: Agent evaluators (Microsoft Foundry); AI Red Teaming Agent (Microsoft Foundry).");
  }

  // 9 ── Lifecycle
  {
    const s = content("Operate it like a product",
      "~3 min. Five things nobody puts in the prototype. A kill switch someone can find. A sponsor who re-attests. A consumption cap: overage SCUs can be capped or unlimited - choose capped. An audit trail in Purview, not stdout. And the calendar: two retirements on the same day, 31 March 2027 - Foundry classic connected agents, and Sentinel in the Azure portal. If you built on either, you have migration work this quarter that has nothing to do with security. The Cloud Adoption Framework's advice: start with a single agent unless the use case crosses boundaries.");
    const items = [
      ["FaPowerOff", "Kill switch", "A documented way to stop it - disabling the agent identity is one sponsors can use."],
      ["FaUserCheck", "Sponsor attestation", "Every 6–12 months; quarterly sweeps for orphaned agents."],
      ["FaGaugeHigh", "Consumption cap", "Provisioned SCUs refresh hourly; overage SCUs can be capped - or unlimited."],
      ["FaClipboardList", "Audit you can query", "Agent actions in Microsoft Purview audit logs, not a container's stdout."],
    ];
    for (let i = 0; i < items.length; i++) {
      const y = 1.5 + i * 1.18;
      card(s, M, y, 6.9, 1.02);
      await badge(s, M + 0.22, y + 0.2, 0.62, items[i][0]);
      txt(s, [{ text: items[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: items[i][2], options: { fontSize: 13 } }],
        { x: M + 1.05, y: y + 0.1, w: 5.7, h: 0.9, fontSize: 16 });
    }
    const x2 = M + 7.2, w2 = W - M - x2;
    card(s, x2, 1.5, w2, 4.55, { fill: HEX.raised, line: "F0576B" });
    txt(s, "31 March 2027", { x: x2 + 0.3, y: 1.75, w: w2 - 0.6, h: 0.7, fontSize: 32, bold: true, color: RED });
    txt(s, "Two retirements, one day", { x: x2 + 0.3, y: 2.45, w: w2 - 0.6, h: 0.4, fontSize: 16, color: WHITE, bold: true });
    bullets(s, ["Foundry classic connected agents - move to Foundry workflows", "Microsoft Sentinel in the Azure portal - Defender portal only"],
      { x: x2 + 0.3, y: 3.0, w: w2 - 0.6, h: 1.5, fontSize: 15 });
    txt(s, "Platform churn is a maintenance cost of building - and it lands on your calendar, not the vendor's.",
      { x: x2 + 0.3, y: 4.55, w: w2 - 0.6, h: 1.2, fontSize: 14, italic: true, color: ICE });
    source(s, "Sources: Security Copilot SCU capacity; Entra Agent ID best practices; Foundry connected agents; Sentinel automation rules; Cloud Adoption Framework - AI agents.");
  }

  // 10 ── Demo 1
  await demoSlide(1, "Design Review for SOC Agents", "design",
    [["Four agents, twelve controls", "One Microsoft-built, three custom - scored on identity, sponsor, least privilege, gates, evaluation, lifecycle."],
     ["Why the worst one scores zero", "App registration, client secret, ungated isolate/disable, a dependency retiring 31 March 2027."],
     ["Rebuild it - same model, same prompt", "The least-privilege diff, then 0 → 100 without changing a word of the prompt."]],
    ["Scorecard", "Least-privilege rebuild", "Drill into Nordlys Enrichment"],
    "cd demos/01-design-the-agent\npython agent_review.py --fix \"Auto-Containment Bot\"",
    "~4 min. Run the scorecard; pause on the table. The Microsoft-built triage agent passes everything - that's the bar. Nordlys Enrichment is the realistic one: built in agent builder, runs as Mads's account because custom agents can't get an Entra Agent ID yet, and Mads is a Security Administrator. Then the rebuild: every failure was a design decision, not a model problem.");

  // 11 ── HITL that scales
  {
    const s = content("A human in the loop that scales",
      "~3 min. The Phishing Triage Agent is the best documented example of HITL done well, so steal its design. It assigns the alert to itself and tags the incident 'Agent', so nobody double-works it. It auto-resolves false positives; true positives stay open for an analyst. And the teach loop: Change classification, a natural-language reason, 'Use this feedback to teach the agent', then 'Evaluate feedback' runs safety and conflict checks before anything lands in memory. Statuses are In use, Conflict, Not in use. Feedback is once per alert and only TP/FP. The Security Alert Triage Agent extends the same agent to cloud and identity alerts in preview; email is GA.");
    const steps = [
      ["FaHandPointer", "Claims the work", "Assigns the alert to itself; tags the incident Agent"],
      ["FaCircleCheck", "Resolves only FPs", "False positives closed; true positives stay open for an analyst"],
      ["FaChalkboardUser", "Learns from you", "Change classification → teach → Evaluate feedback"],
      ["FaScaleBalanced", "Checks the lesson", "Safety and conflict checks: In use, Conflict, Not in use"],
    ];
    const w = (W - 2 * M - 0.9) / 4;
    for (let i = 0; i < steps.length; i++) {
      const x = M + i * (w + 0.3);
      card(s, x, 1.55, w, 3.0);
      await badge(s, x + 0.3, 1.8, 0.75, steps[i][0], i === 3 ? AMBER : BLUE);
      txt(s, [{ text: steps[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: steps[i][2], options: { fontSize: 14 } }],
        { x: x + 0.3, y: 2.75, w: w - 0.6, h: 1.7, fontSize: 18 });
      if (i < 3) arrow(s, x + w + 0.02, 2.9, 0.26, MUTED);
    }
    card(s, M, 4.8, W - 2 * M, 1.2, { fill: HEX.raised });
    txt(s, [{ text: "Measure it: ", options: { bold: true, color: WHITE } },
            { text: "the Performance tab shows mean time to triage and SCU consumption; the usage dashboard shows cost per email processed. ", options: {} },
            { text: "Scope it: ", options: { bold: true, color: WHITE } },
            { text: "the Security Alert Triage Agent (preview) adds cloud and identity alerts - email and collaboration alerts are GA.", options: {} }],
      { x: M + 0.35, y: 4.95, w: W - 2 * M - 0.7, h: 1.0, fontSize: 15, valign: "middle" });
    source(s, "Sources: Phishing Triage Agent; Security Copilot agents in Defender (page dated 12 Nov 2026).");
  }

  // 12 ── Demo 2
  await demoSlide(2, "Triage, With a Human in the Loop", "triage",
    [["Seventeen emails, threshold 0.90", "It resolves the FPs it's sure of and leaves the rest open - no attack closed."],
     ["Lower the bar to 0.60", "The queue shrinks - and a real AiTM link inside a genuine partner share is auto-closed."],
     ["Teach it", "A narrow lesson goes In use. A broad one hits Conflict with the bank-details rule."]],
    ["Threshold 0.90", "Threshold 0.60", "Teach the agent"],
    "cd demos/02-triage-and-teach\npython triage_agent.py --threshold 0.6",
    "~4 min. Default run first: 41% of the queue handled, no attack closed. Then 0.60 - the thing someone will ask for when the queue is long. E-1017 closes: the partner tenant was compromised, so every 'trust' signal is genuine. That alert is the incident we follow through Demo 3. Then --teach: the conflict check stops 'invoices from vendors we pay are always safe'.");

  // 13 ── Part 2
  section("02 Build");
  divider("02", "Build your own SOC agents", "Four roles, three handoffs - and the places they break.",
    "~0.3 min. Transition. We follow the E-1017 incident through four specialised agents.");

  // 14 ── Roles and handoffs
  {
    const s = content("Four roles, three handoffs",
      "~3 min. These are the abstract's four roles. Read the bottom row: each arrow is a contract, not a chat message. Triage hands over a verdict, entities and evidence. Investigation hands over scope, timeline and indicators. Detection engineering hands over a rule plus its back-test - not just a rule. Remediation receives a plan and returns approvals. Each role needs different tools and different permissions, which is the only good reason to split agents at all - the Architecture Center warns against agents that add no real specialization.");
    const roles = [
      ["FaFilter", "Alert triage", "TP / FP verdict", "Alerts (manage), email metadata"],
      ["FaMagnifyingGlass", "Investigation", "Scope, timeline, pivots", "Hunting (read), entity analysis"],
      ["FaCode", "Detection engineering", "Rule + back-test", "Hunting (read), custom detections (write, disabled)"],
      ["FaWrench", "Posture remediation", "Plan + approvals", "Proposes changes; humans approve hard actions"],
    ];
    const w = 2.65, gap = (W - 2 * M - 4 * w) / 3;
    for (let i = 0; i < roles.length; i++) {
      const x = M + i * (w + gap);
      card(s, x, 1.6, w, 3.2);
      await badge(s, x + (w - 0.85) / 2, 1.85, 0.85, roles[i][0], i === 3 ? OK : BLUE);
      txt(s, roles[i][1], { x: x + 0.15, y: 2.85, w: w - 0.3, h: 0.45, fontSize: 18, bold: true, color: WHITE, align: "center" });
      txt(s, roles[i][2], { x: x + 0.15, y: 3.3, w: w - 0.3, h: 0.4, fontSize: 15, color: BLUE, align: "center" });
      txt(s, roles[i][3], { x: x + 0.2, y: 3.75, w: w - 0.4, h: 0.95, fontSize: 12, color: MUTED, align: "center" });
      if (i < 3) arrow(s, x + w + 0.08, 3.05, gap - 0.16);
    }
    const hand = ["verdict + entities + evidence refs", "scope + indicators + timeline", "rule + back-test report"];
    for (let i = 0; i < 3; i++) {
      const x = M + i * (w + gap) + w / 2 + 0.2;
      card(s, x, 5.1, w + gap - 0.4, 0.75, { fill: HEX.raised });
      txt(s, hand[i], { x: x + 0.1, y: 5.1, w: w + gap - 0.6, h: 0.75, fontSize: 13, color: ICE, align: "center", valign: "middle" });
    }
    txt(s, "Split agents only where the tools and permissions differ. Every split adds a handoff.",
      { x: M, y: 6.1, w: W - 2 * M, h: 0.4, fontSize: 16, bold: true, color: WHITE });
  }

  // 15 ── Building blocks
  {
    const s = content("What you build with",
      "~3 min. Three building blocks. Security Copilot custom agents: NL2Agent, agent builder, YAML upload or MCP tools from your IDE - every route converges on a YAML manifest. Components: tools (skills), triggers, orchestrators, instructions, feedback. Tool formats API, GPT, KQL, AGENT and MCP. Triggers poll with DefaultPeriodSeconds, FetchSkill and ProcessSkill. The Sentinel MCP server is fully hosted, uses Entra identity, and has three collections - data exploration, Security Copilot agent creation, triage; the server is free, data lake queries and graph meters are charged. Microsoft Agent Framework is the successor to Semantic Kernel and AutoGen and ships the five orchestration patterns, human-in-the-loop requests and checkpoints. And note again: Foundry classic connected agents are deprecated - use workflows.");
    await iconCard(s, M, 1.5, 3.85, 4.95, "FaRobot", "Security Copilot custom agents",
      ["NL2Agent, agent builder, YAML upload, or MCP tools - all become a YAML manifest", "Tools: API, GPT, KQL, AGENT, MCP", "Triggers: DefaultPeriodSeconds, FetchSkill → ProcessSkill", "Publish: Myself only, or For everyone in workspace"], BLUE, 13);
    await iconCard(s, M + 4.1, 1.5, 3.85, 4.95, "FaDatabase", "Sentinel MCP server",
      ["Hosted, Entra identity, no infrastructure", "Collections: data exploration, agent creation, triage", "query_lake, search_tables, analyze_user_entity; graph tools in preview", "Server is free; data lake and graph meters are charged"], ICE, 13);
    await iconCard(s, M + 8.2, 1.5, W - 2 * M - 8.2, 4.95, "FaDiagramProject", "Microsoft Agent Framework",
      ["Successor to Semantic Kernel and AutoGen", "Sequential, concurrent, group chat, handoff, magentic", "Human-in-the-loop requests and tool approvals", "Checkpoints at the end of each superstep"], OK, 13);
    source(s, "Sources: Security Copilot custom agents overview and agent components; Sentinel MCP overview, tools and billing; Agent Framework overview, human-in-the-loop, checkpoints.");
  }

  // 16 ── Patterns
  {
    const s = content("Pick the simplest pattern that works",
      "~3 min. The Architecture Center's five orchestration patterns, and its first piece of advice: use the lowest level of complexity that reliably meets your requirements - a single agent with tools is often the right default. The SOC chain we build is sequential with a handoff for routing. Group chat is the maker-checker loop - keep it to three or fewer agents and cap the iterations. Magentic is the one to choose when a human must review the plan before it runs, and the one to avoid when work is time-sensitive - which is most of incident response.");
    const rows = [
      ["Sequential", "Fixed stages, each builds on the last", "Stages could run in parallel; you need backtracking"],
      ["Concurrent", "Independent analyses, fan-out / fan-in", "Agents share mutable state; no conflict resolution"],
      ["Group chat", "Maker-checker review (≤ 3 agents)", "Unbounded iterations"],
      ["Handoff", "Routing to the right specialist", "Routing is deterministic; risk of infinite handoff loops"],
      ["Magentic", "Open-ended work with a reviewable plan", "Time-sensitive work"],
    ];
    const cw = [2.2, 4.8, 5.13];
    txt(s, "Use when", { x: M + cw[0], y: 1.45, w: cw[1], h: 0.4, fontSize: 15, bold: true, color: OK });
    txt(s, "Avoid when", { x: M + cw[0] + cw[1], y: 1.45, w: cw[2], h: 0.4, fontSize: 15, bold: true, color: RED });
    for (let i = 0; i < rows.length; i++) {
      const y = 1.9 + i * 0.86;
      card(s, M, y, W - 2 * M, 0.74, { fill: i === 3 ? HEX.raised : PANEL });
      txt(s, rows[i][0], { x: M + 0.3, y, w: cw[0] - 0.3, h: 0.74, fontSize: 17, bold: true, color: WHITE, valign: "middle" });
      txt(s, rows[i][1], { x: M + cw[0], y, w: cw[1] - 0.3, h: 0.74, fontSize: 15, valign: "middle" });
      txt(s, rows[i][2], { x: M + cw[0] + cw[1], y, w: cw[2] - 0.3, h: 0.74, fontSize: 15, color: MUTED, valign: "middle" });
    }
    txt(s, [{ text: "“Use the lowest level of complexity that reliably meets your requirements.”", options: { italic: true, color: WHITE } },
            { text: "   - Azure Architecture Center", options: { fontSize: 12, color: MUTED } }],
      { x: M, y: 6.25, w: W - 2 * M, h: 0.4, fontSize: 17 });
  }

  // 17 ── Handoff contract
  {
    const s = content("The handoff contract",
      "~3 min. This is the most important slide in the build section. Agents should hand each other a typed envelope, not a paragraph. Schema version so receivers can reject what they don't understand. Entities as identifiers, not names. Evidence as references to rows the next agent can re-check. A version number on every write. A hop counter the orchestrator enforces. And the receiver validates before it acts - the Architecture Center's 'validate each agent's output before passing it on'. Checkpoints in Agent Framework give you the durable version of this.");
    code(s, M, 1.5, 6.1, 4.9, `{
  "schema": "soc.handoff/v1",
  "incident": "INC-4471",
  "version": 2,
  "hop": 2,
  "from": "Investigation",
  "to": "Detection Engineering",
  "entities": {
    "users": ["freja.nielsen@…", "jonas.berg@…"],
    "ips":   ["203.0.113.77", "203.0.113.91"]
  },
  "findings": ["token replay: jonas.berg …"],
  "evidence": ["E-1017", "S-2", "S-3", "X-1"],
  "requested_action": null
}`, 13);
    const rules = [
      ["FaCubes", "Typed and versioned", "A schema the receiver can reject"],
      ["FaAt", "Identifiers, not names", "UPNs and IPs survive; 'someone in procurement' doesn't"],
      ["FaLink", "Evidence by reference", "Claims cite rows the next agent can re-query"],
      ["FaCodeBranch", "Version every write", "Conditional writes catch the lost update"],
      ["FaRepeat", "Hop limit", "The orchestrator ends loops, then escalates to a human"],
    ];
    for (let i = 0; i < rules.length; i++) {
      const y = 1.5 + i * 0.99;
      await badge(s, M + 6.45, y + 0.1, 0.6, rules[i][0], BLUE);
      txt(s, [{ text: rules[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: rules[i][2], options: { fontSize: 13 } }],
        { x: M + 7.25, y, w: W - M - (M + 7.25), h: 0.9, fontSize: 17 });
    }
  }

  // 18 ── Where it breaks
  {
    const s = content("Where multi-agent systems break",
      "~2 min. Each of these is named in the Architecture Center guidance, and each is a variant in Demo 3 - so the next demo is a tour of failures. Context growth isn't in the demo; the fix is to compact or summarise between agents - but summarise into the envelope, not instead of it.");
    const fails = [
      ["FaFileLines", "Lossy handoff", "A prose summary drops an entity", "--free-text"],
      ["FaRotate", "Infinite handoff loop", "Two agents each wait for the other", "--loop"],
      ["FaPeopleArrows", "Shared mutable state", "Concurrent writers, last write wins", "--race"],
      ["FaHand", "Ungated hard action", "Right about the threat, wrong about the fix", "--no-gate"],
      ["FaLayerGroup", "Context growth", "Every hop appends; compact into the envelope", "-"],
      ["FaCopy", "No real specialization", "An agent that adds a hop and nothing else", "-"],
    ];
    const colW = (W - 2 * M - 0.3) / 2;
    for (let i = 0; i < fails.length; i++) {
      const col = i % 2, row = Math.floor(i / 2);
      const x = M + col * (colW + 0.3), y = 1.5 + row * 1.62;
      card(s, x, y, colW, 1.42);
      await badge(s, x + 0.3, y + 0.33, 0.75, fails[i][0], fails[i][3] === "-" ? MUTED : RED);
      txt(s, [{ text: fails[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: fails[i][2], options: { fontSize: 14 } }],
        { x: x + 1.3, y: y + 0.2, w: colW - 3.0, h: 1.1, fontSize: 18 });
      if (fails[i][3] !== "-") pill(s, x + colW - 1.6, y + 0.55, fails[i][3], AMBER, 1.35);
    }
  }

  // 19 ── Demo 3
  await demoSlide(3, "The Handoff Chain", "handoff",
    [["Four agents, one AiTM incident", "Typed envelope, receiver validation, evidence refs, two attacker IPs pivoted."],
     ["The approval gate does its job", "Revoke both sessions: approved. Disable the payroll service account: rejected - 1,400 payslips."],
     ["Then break it", "Prose handoff loses Jonas. A loop hits the hop limit. A race loses a user. No gate stops payroll."]],
    ["Structured + gate", "Free-text handoff", "Handoff loop", "Two writers", "No approval gate"],
    "cd demos/03-hand-off\npython soc_handoffs.py --free-text",
    "~6 min. This is the centrepiece. Run the structured version first and pause at each handoff line. At the gate, read the payroll rejection aloud: the agent was right that the attacker touched svc-payroll, wrong about what to do. Then free-text: the hook slide, live. If time, loop and race in 30 seconds each.");

  // 20 ── Demo 4
  await demoSlide(4, "The Detection Engineering Agent", "detection",
    [["Three candidates from one handoff", "IOC, broad and behavioural rules drafted from the INC-4471 envelope."],
     ["Back-test before asking", "Seven days of telemetry: recall, false positives per day, and the 150-alerts-per-run cap."],
     ["Create disabled, then ask", "Enabling a custom detection is a hard action. Then: what 'ship first' does to the queue."]],
    ["Back-test, then ask", "Ship first", "The KQL"],
    "cd demos/04-detection-engineering\npython detection_agent.py --ship-first",
    "~4 min. Facts to drop: custom detection rules run continuously (NRT) or every 1, 3, 12 or 24 hours, and a run produces at most 150 alerts. The IOC rule misses the earlier attack from a different AiTM node; the broad rule pages 18 times a day. Only C passes, and the agent still asks. Ship-first: 23 alerts on day one, zero real - and that's how analysts learn to close a rule without reading it.");

  // 21 ── Part 3
  section("03 Perception");
  divider("03", "Microsoft Perception", "Microsoft's multi-agent system for the security operations center.",
    "~0.3 min. Transition. Same problems - roles, handoffs, gates, audit - solved as a product.");

  // 22 ── What it is
  {
    const s = content("What Microsoft Perception is",
      "~3 min. Learn describes it as Microsoft's multi-agent system for the security operations center, in the Defender portal. Timeline: announced 27 July 2026 as Project Perception, public preview from 3 August; at Ignite (17 Nov 2026) it became Microsoft Perception and Microsoft said it will be generally available. Be precise on stage: some Learn pages still describe a limited, invitation-only preview - check status before you plan around it. It is not a Security Copilot rebrand; they're complementary and priced separately. The architecture is the Cyber Stack: the Harness layer is the orchestrator that decides which agent runs next and passes findings between them - exactly the job your custom orchestrator does.");
    const stack = ["Actuators", "Agents", "Harness", "Models", "Context", "Signals and sensors"];
    for (let i = 0; i < stack.length; i++) {
      const y = 1.5 + i * 0.78, hot = stack[i] === "Harness";
      card(s, M, y, 4.6, 0.66, { fill: hot ? HEX.raised : PANEL, line: hot ? "2FA8E6" : HEX.line });
      txt(s, stack[i], { x: M + 0.3, y, w: 4.0, h: 0.66, fontSize: 17, bold: hot, color: hot ? BLUE : WHITE, valign: "middle" });
    }
    txt(s, "The Cyber Stack", { x: M, y: 6.2, w: 4.6, h: 0.35, fontSize: 13, italic: true, color: MUTED });
    const x2 = M + 5.0, w2 = W - M - x2;
    const facts = [
      ["Where", "The Microsoft Defender portal - Perception in the navigation."],
      ["Status", "Announced 27 Jul 2026; renamed and announced for GA at Ignite 2026. Some Learn pages still say limited preview - check."],
      ["Not Security Copilot", "“Not a Security Copilot rebrand” - complementary, and priced separately."],
      ["The Harness", "Runs coordinated playbooks, “deciding which agent runs next and passing findings between them.”"],
      ["Shared context", "A near-real-time view of assets, identities, relationships, risks and activities."],
    ];
    for (let i = 0; i < facts.length; i++) {
      const y = 1.5 + i * 0.97;
      card(s, x2, y, w2, 0.85);
      txt(s, facts[i][0], { x: x2 + 0.25, y, w: 2.0, h: 0.85, fontSize: 15, bold: true, color: BLUE, valign: "middle" });
      txt(s, facts[i][1], { x: x2 + 2.3, y, w: w2 - 2.5, h: 0.85, fontSize: 14, valign: "middle" });
    }
  }

  // 23 ── Agents by team
  {
    const s = content("Red, blue and green team agents",
      "~3 min. Read the three columns. Red simulates the attacker: the Recon Agent maps attack paths, choke points and excess permissions - read-only, and Azure environments only. Blue detects, triages and investigates - note the Detection Authoring Agent writes KQL rules, the same job as our Demo 4 agent. Green remediates and hardens. The Ignite post also names a Web App Pen Test Agent on the red team; it isn't in the Learn table of contents yet, so I've left it off the slide. Each agent gets its own Microsoft Entra Agent ID when you set it up - the identity control from slide 6, done for you.");
    const teams = [
      ["red", "Red team", "Simulate attacker behavior to expose vulnerabilities", [["Recon Agent", "Attack paths, choke points, excess permissions - read-only, Azure only"]]],
      ["blue", "Blue team", "Detect, triage and investigate", [["Triage Agent", "Alert queue; can self-trigger and resolve FPs"], ["Threat Intelligence Agent", ""], ["Attack Investigation Agent", "Tier-2 incident investigation"], ["Detection Authoring Agent", "Writes KQL detection rules"]]],
      ["green", "Green team", "Remediate and harden", [["Posture Prioritization Agent", ""], ["Identity Risk Reduction Agent", "Recommends Conditional Access changes"], ["Risk Reduction Agent", "Remediation plans, shielding, Intune patching"]]],
    ];
    const w = (W - 2 * M - 0.6) / 3;
    for (let i = 0; i < teams.length; i++) {
      const [key, name, role, agents] = teams[i], x = M + i * (w + 0.3), col = TEAM[key];
      card(s, x, 1.5, w, 5.0);
      s.addShape(pres.shapes.RECTANGLE, { x: x + 0.3, y: 1.75, w: 0.12, h: 0.75, fill: { color: col }, line: { type: "none" } });
      txt(s, [{ text: name, options: { bold: true, color: WHITE, breakLine: true } }, { text: role, options: { fontSize: 13, color: col } }],
        { x: x + 0.6, y: 1.72, w: w - 0.85, h: 0.85, fontSize: 20 });
      for (let j = 0; j < agents.length; j++) {
        const y = 2.8 + j * 0.9;
        txt(s, [{ text: agents[j][0], options: { bold: true, color: WHITE, breakLine: !!agents[j][1] } },
                ...(agents[j][1] ? [{ text: agents[j][1], options: { fontSize: 12, color: MUTED } }] : [])],
          { x: x + 0.3, y, w: w - 0.6, h: 0.85, fontSize: 15 });
      }
    }
    source(s, "Source: Microsoft Learn - agentic security: agent categories and agents (checked 19 Nov 2026).");
  }

  // 24 ── Playbooks
  {
    const s = content("Playbooks: Microsoft's handoffs, pre-built",
      "~3 min. A playbook is a reusable template that defines how agents respond to a scenario - in other words, the handoff contract and the orchestration, written and maintained by Microsoft. The documented example: Protect against a threat runs Threat Intelligence, then Recon, then Posture Prioritization, then Detection Authoring and Attack Investigation, each output becoming a structured input for the next. Two constraints to state clearly: the playbook list is preset and read-only - no custom playbooks in this release - and a playbook runs only when every agent it needs is enabled. Start them from incident, alert, case and threat intelligence pages, or, per the Ignite post, from ITSM, SIEM or SOAR through APIs and MCP.");
    const seq = [["Threat Intelligence", "blue"], ["Recon", "red"], ["Posture Prioritization", "green"], ["Detection Authoring  ·  Attack Investigation", "blue"]];
    txt(s, "Protect against a threat", { x: M, y: 1.45, w: 8, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    const bw = [2.35, 1.4, 2.55, 3.95];
    let x = M;
    for (let i = 0; i < seq.length; i++) {
      card(s, x, 1.95, bw[i], 0.85, { fill: HEX.raised, line: THEME.colors[{ red: "accent5", blue: "accent1", green: "accent3" }[seq[i][1]]] });
      txt(s, seq[i][0], { x: x + 0.1, y: 1.95, w: bw[i] - 0.2, h: 0.85, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle" });
      x += bw[i];
      if (i < seq.length - 1) { arrow(s, x + 0.06, 2.22, 0.3); x += 0.42; }
    }
    card(s, M, 3.1, 5.9, 3.35);
    txt(s, "The library (read-only)", { x: M + 0.3, y: 3.25, w: 5.3, h: 0.4, fontSize: 16, bold: true, color: WHITE });
    const pbs = ["Triage alert", "Protect against a threat", "Investigate attack", "Extract threat intelligence", "Identify attack paths",
                 "Plan for posture remediation", "Assess identity risks", "Reduce credential phishing risk", "Close identity attack paths used in your environment"];
    bullets(s, pbs, { x: M + 0.3, y: 3.7, w: 5.4, h: 2.7, fontSize: 12, paraSpaceAfter: 2 });
    const x2 = M + 6.2, w2 = W - M - x2;
    const rules = [
      ["FaLock", "Preset by Microsoft", "“You can't create custom playbooks in this release.”", AMBER],
      ["FaPuzzlePiece", "All agents, or none", "A playbook runs only when every agent it needs is enabled.", AMBER],
      ["FaPlug", "Start it from anywhere", "Incident, alert, case and TI pages - or ITSM, SIEM and SOAR via APIs and MCP.", BLUE],
    ];
    for (let i = 0; i < rules.length; i++) {
      const y = 3.1 + i * 1.13;
      card(s, x2, y, w2, 1.0);
      await badge(s, x2 + 0.22, y + 0.19, 0.62, rules[i][0], rules[i][3]);
      txt(s, [{ text: rules[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: rules[i][2], options: { fontSize: 13 } }],
        { x: x2 + 1.05, y: y + 0.08, w: w2 - 1.25, h: 0.9, fontSize: 16 });
    }
  }

  // 25 ── Supervision
  {
    const s = content("Supervision is built in",
      "~3 min. Map this back to Part 1 - it's the same control list. Approval gates: when a playbook reaches one, the session shows Waiting for input, and you can Approve, Reject, Suggest an alternative, or Stop - and Stop can't be undone. Microsoft's examples of approval-worthy actions are disabling a user account or isolating a device. Sessions are immutable records that serve as an audit trail; agent actions are also in Purview audit logs. Each agent has its own RBAC for who can run, steer or view it. And Microsoft's own guidance is the one I'd give you for a custom build: introduce autonomy gradually. The exception to know: the Triage Agent can trigger itself on new alerts and auto-resolve false positives.");
    card(s, M, 1.5, 5.6, 4.95, { fill: HEX.raised, line: "F5B841" });
    pill(s, M + 0.35, 1.8, "WAITING FOR INPUT", AMBER, 2.1);
    txt(s, "Disable user account svc-legacy-ftp", { x: M + 0.35, y: 2.3, w: 4.9, h: 0.45, fontSize: 17, bold: true, color: WHITE });
    const opts = [["Approve", OK], ["Reject", RED], ["Suggest an alternative", BLUE], ["Stop", MUTED]];
    for (let i = 0; i < opts.length; i++) pill(s, M + 0.35, 2.95 + i * 0.52, opts[i][0], opts[i][1], 2.6);
    txt(s, "Stop cannot be undone.", { x: M + 3.15, y: 4.52, w: 2.2, h: 0.32, fontSize: 12, italic: true, color: MUTED, valign: "middle" });
    txt(s, "Examples Microsoft gives of actions that need approval: disabling a user account, isolating a device.",
      { x: M + 0.35, y: 5.25, w: 4.9, h: 0.9, fontSize: 13 });
    const x2 = M + 5.9, w2 = W - M - x2;
    const items = [
      ["FaBookBookmark", "Immutable sessions", "Every step recorded - “an audit trail” - plus Purview audit logs"],
      ["FaIdCard", "An identity per agent", "The setup wizard creates a Microsoft Entra Agent ID for each agent"],
      ["FaUsersGear", "RBAC per agent", "Who can run it, steer it, and view its sessions"],
      ["FaStairs", "Autonomy, gradually", "Microsoft's own guidance. The Triage Agent may self-trigger and resolve FPs"],
    ];
    for (let i = 0; i < items.length; i++) {
      const y = 1.5 + i * 1.25;
      card(s, x2, y, w2, 1.1);
      await badge(s, x2 + 0.22, y + 0.22, 0.65, items[i][0], BLUE);
      txt(s, [{ text: items[i][1], options: { bold: true, color: WHITE, breakLine: true } }, { text: items[i][2], options: { fontSize: 13 } }],
        { x: x2 + 1.1, y: y + 0.1, w: w2 - 1.3, h: 0.95, fontSize: 16 });
    }
  }

  // 26 ── Integrations and prerequisites
  {
    const s = content("How it fits the Microsoft security stack",
      "~3 min. Left: integrations. Defender is native. Entra gives every agent an Agent ID. In Security Copilot, the Perception Triage Agent replaces the Phishing Triage Agent - only one triage agent can be active at a time. Intune executes Risk Reduction patch plans. Purview holds the audit. Exposure Management, Defender CSPM and Defender Vulnerability Management feed the green team. Sentinel is a signal source - I found nothing on Learn yet about the Sentinel data lake, graph or MCP for Perception. Right: prerequisites. URBAC across all Defender workloads; Security Admin to set up; Security Reader to run and view; some agents need more, like 'Approve hard actions'. Pricing: consumption-based - pay-as-you-go or AI Flex, counts toward MACC. There's no public rate card, which is why Demo 6 computes a break-even instead of inventing a price.");
    const ints = [
      ["Microsoft Defender", "Native - playbooks start from incidents, alerts, cases, TI"],
      ["Microsoft Entra", "An Agent ID per agent; Entra ID P2 for identity alert triage"],
      ["Security Copilot", "Perception Triage Agent replaces the Phishing Triage Agent - one active"],
      ["Microsoft Intune", "Risk Reduction Agent patch plans"],
      ["Microsoft Purview", "Agent actions in the audit log"],
      ["Exposure Mgmt · Defender CSPM · MDVM", "Signals for the red and green teams"],
    ];
    for (let i = 0; i < ints.length; i++) {
      const y = 1.5 + i * 0.82;
      card(s, M, y, 6.6, 0.7);
      txt(s, ints[i][0], { x: M + 0.25, y, w: 2.6, h: 0.7, fontSize: 14, bold: true, color: WHITE, valign: "middle" });
      txt(s, ints[i][1], { x: M + 2.9, y, w: 3.55, h: 0.7, fontSize: 12.5, valign: "middle" });
    }
    const x2 = M + 6.9, w2 = W - M - x2;
    card(s, x2, 1.5, w2, 2.6);
    txt(s, "Before you start", { x: x2 + 0.3, y: 1.65, w: w2 - 0.6, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    bullets(s, ["URBAC enabled across all Defender workloads", "Security Admin sets agents up; Security Reader runs them and views sessions",
                "Some agents need more - e.g. “Approve hard actions”"], { x: x2 + 0.3, y: 2.1, w: w2 - 0.6, h: 1.9, fontSize: 14 });
    card(s, x2, 4.3, w2, 2.15, { fill: HEX.raised, line: "2FA8E6" });
    txt(s, "Pricing", { x: x2 + 0.3, y: 4.45, w: w2 - 0.6, h: 0.4, fontSize: 17, bold: true, color: WHITE });
    bullets(s, ["Consumption-based: pay-as-you-go or AI Flex plan; counts toward MACC", "Usage dashboard and cost calculator announced at Ignite", "No public rate card - ask for your number"],
      { x: x2 + 0.3, y: 4.9, w: w2 - 0.6, h: 1.5, fontSize: 14 });
  }

  // 27 ── Demo 5
  await demoSlide(5, "A Microsoft Perception Playbook", "perception",
    [["The documented sequence", "Threat Intelligence → Recon → Posture Prioritization → Detection Authoring / Attack Investigation."],
     ["Waiting for input", "Approve, Reject, Suggest an alternative, Stop - and an immutable session that records each."],
     ["The trade-off, shown", "Disable a required agent and the playbook won't start. Try to write your own: read-only."]],
    ["Approve", "Suggest an alternative", "Reject  ·  Stop", "Recon Agent disabled", "Custom playbook?"],
    "cd demos/05-perception-playbook\npython perception_playbook.py --decision suggest",
    "~5 min. Say it once: this is a model of the documented flow - names, sequence and controls from Learn; the agents' reasoning is a stand-in. Pause on the Recon warning: Azure only, and it says so. Run 'Suggest an alternative' - the human changes the plan, the agent revises, both are in the record. End on 'Custom playbook?' - that's the honest limit of buying, and the bridge to Part 4.");

  // 28 ── Part 4
  section("04 Decide");
  divider("04", "Build vs. buy", "Supportability, maintenance and three-year cost - with your numbers.",
    "~0.3 min. Transition. Now the comparison the abstract promised.");

  // 29 ── Comparison
  {
    const s = content("Custom agents vs. Microsoft Perception",
      "~4 min. Be fair here - the room will trust the conclusion more. Perception wins on who maintains the agents, prompts and handoffs; who absorbs platform changes like the two March 2027 retirements; identity and audit out of the box. Custom wins on flexibility: if your scenario isn't in the playbook library, you build it - and Perception has real limits today: read-only playbooks, Recon is Azure-only, triage covers a limited set of alert types, and status differs across Learn pages. Pricing transparency is a draw: neither side has a number until you do the work - your engineering costs, or Microsoft's cost calculator.");
    const rows = [
      ["Agents, prompts, handoffs", "You write and maintain them", "Microsoft-published agents and playbooks", "p"],
      ["Platform and model changes", "Your migration backlog (e.g. 31 Mar 2027)", "Absorbed by the product", "p"],
      ["Identity and audit", "You build it (custom SCU agents: user account today)", "Entra Agent ID per agent, sessions, Purview", "p"],
      ["Approval gates", "You design and enforce them", "Waiting for input: Approve, Reject, Suggest, Stop", "p"],
      ["Your unique scenarios", "Anything you can build", "Preset playbooks only - no custom in this release", "c"],
      ["Coverage limits", "Whatever you integrate", "Recon: Azure only; triage: limited alert types", "c"],
      ["Cost", "Engineering time + SCUs", "Consumption; no public rate card", "="],
    ];
    const cw = [3.0, 4.55, 4.58];
    txt(s, "Custom build", { x: M + cw[0], y: 1.4, w: cw[1], h: 0.4, fontSize: 16, bold: true, color: ICE });
    txt(s, "Microsoft Perception", { x: M + cw[0] + cw[1], y: 1.4, w: cw[2], h: 0.4, fontSize: 16, bold: true, color: BLUE });
    for (let i = 0; i < rows.length; i++) {
      const y = 1.82 + i * 0.68, win = rows[i][3];
      card(s, M, y, W - 2 * M, 0.6);
      txt(s, rows[i][0], { x: M + 0.25, y, w: cw[0] - 0.3, h: 0.6, fontSize: 14, bold: true, color: WHITE, valign: "middle" });
      txt(s, rows[i][1], { x: M + cw[0], y, w: cw[1] - 0.25, h: 0.6, fontSize: 13, valign: "middle", color: win === "c" ? WHITE : BODY, bold: win === "c" });
      txt(s, rows[i][2], { x: M + cw[0] + cw[1], y, w: cw[2] - 0.25, h: 0.6, fontSize: 13, valign: "middle", color: win === "p" ? WHITE : BODY, bold: win === "p" });
    }
    txt(s, "Bold marks the side that's ahead on that row.", { x: M, y: 6.62, w: 6, h: 0.3, fontSize: 10, italic: true, color: MUTED });
  }

  // 30 ── Where the money goes
  {
    const s = content("Where the money goes",
      "~3 min. These are Demo 6's mid-size numbers: 2,000 E5 users, five custom agents, a fully loaded engineer week at $3,000. Every input except Microsoft's facts is an assumption you replace. The shape is what matters and it holds across all three profiles: building is about 12% of the three-year bill; maintenance, on-call, evaluation and migrations are the rest. Microsoft's facts in the model: $6 per overage SCU, and E5/E7 include 400 SCUs a month per 1,000 user licences, capped at 10,000. Because there's no Perception rate card, the model computes the break-even - $17,050 a month here - and you compare it with the number from the cost calculator.");
    s.addChart(pres.charts.BAR, [{ name: "Build path, 3 years (USD)",
      labels: ["Build", "Maintenance", "On-call", "SCU overage", "Evaluation + red team", "Migrations"],
      values: [90000, 360000, 117000, 108000, 54000, 18000] }], {
      x: M, y: 1.45, w: 7.4, h: 4.9, barDir: "bar", chartColors: ["2FA8E6"],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "$#,##0", dataLabelColor: "D9E2F5", dataLabelFontSize: 12,
      dataLabelFontFace: "+mn-lt",
      catAxisLabelColor: "D9E2F5", catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt", catAxisOrientation: "maxMin",
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false,
      showTitle: true, title: "Custom build, mid-size SOC, 3 years", titleColor: "FFFFFF", titleFontSize: 15, titleFontFace: "+mn-lt",
    });
    const x2 = M + 7.7, w2 = W - M - x2;
    card(s, x2, 1.45, w2, 2.2, { fill: HEX.raised });
    txt(s, "88%", { x: x2 + 0.3, y: 1.6, w: w2 - 0.6, h: 1.0, fontSize: 60, bold: true, color: BLUE });
    txt(s, "of a three-year custom build is running it, not building it.", { x: x2 + 0.3, y: 2.65, w: w2 - 0.6, h: 0.9, fontSize: 15 });
    card(s, x2, 3.85, w2, 2.5, { fill: HEX.raised, line: "2FA8E6" });
    txt(s, "$17,050 / month", { x: x2 + 0.3, y: 4.0, w: w2 - 0.6, h: 0.7, fontSize: 30, bold: true, color: WHITE });
    txt(s, "Break-even. Below this Perception consumption, buying is cheaper - for these assumptions. Get your number from the cost calculator.",
      { x: x2 + 0.3, y: 4.7, w: w2 - 0.6, h: 1.5, fontSize: 14 });
    source(s, "Facts: Security Copilot pricing ($6 overage SCU) and E5/E7 inclusion (400 SCU per 1,000 users, cap 10,000). Everything else: assumptions in demos/06-build-vs-buy/assumptions.json.");
  }

  // 31 ── Demo 6
  await demoSlide(6, "Build vs. Buy: the Three-Year View", "tco",
    [["Facts vs. assumptions", "Microsoft's published numbers are labelled; every other input is yours to change."],
     ["No invented price", "There's no public Perception rate card, so the model computes the break-even instead."],
     ["What actually moves the answer", "Sensitivity: maintenance weeks per agent - not build cost - is the biggest lever."]],
    ["Mid-size SOC", "Sensitivity", "Small SOC  ·  Large SOC", "With a $12k/month quote"],
    "cd demos/06-build-vs-buy\npython build_vs_buy.py --sensitivity",
    "~4 min. Run mid-size, pause on step 1 and the 88%. Then supportability: eight things you own at 02:00 versus three. Then Sensitivity: the argument to have with your leadership is about maintenance, from your own history of keeping automations alive. Small SOC: break-even is ~$3.5k/month - for a small team that's the honest answer, check it. Edit assumptions.json with your numbers; it's meant to be forked.");

  // 32 ── Decision framework
  {
    const s = content("Buy what's standard. Build what's yours.",
      "~3 min. The framework. Five questions, in order. If a playbook covers the workflow, start there - your custom effort goes on what's left. The second question is the one people skip: not 'can we build it' but 'who maintains it in year three'. Third, the break-even against the cost calculator. Fourth, if you build, prove the Part 1 controls - the same ones Perception ships with. Fifth: whatever is genuinely unique to you - vendor bank-detail fraud, your SAP payment run - is a custom agent on both paths. That's why the answer for most SOCs is both, with Perception as the backbone.");
    const qs = [
      ["Does a Perception playbook already cover it?", "Start there. Custom effort goes to the gap."],
      ["Who maintains it in year three?", "Model upgrades, API changes, migrations, on-call - by name."],
      ["What's your break-even?", "Your three-year build cost vs. the cost calculator."],
      ["Can you prove the controls?", "Identity, least privilege, gates, evaluation, audit - on your build."],
      ["What's left that's truly yours?", "Build that - it's a custom agent on both paths."],
    ];
    for (let i = 0; i < qs.length; i++) {
      const y = 1.5 + i * 0.98;
      card(s, M, y, 8.1, 0.86);
      txt(s, String(i + 1), { x: M + 0.25, y, w: 0.5, h: 0.86, fontSize: 26, bold: true, color: BLUE, valign: "middle" });
      txt(s, [{ text: qs[i][0], options: { bold: true, color: WHITE, breakLine: true } }, { text: qs[i][1], options: { fontSize: 13 } }],
        { x: M + 0.85, y: y + 0.06, w: 7.1, h: 0.8, fontSize: 17 });
    }
    const x2 = M + 8.4, w2 = W - M - x2;
    card(s, x2, 1.5, w2, 4.78, { fill: HEX.raised, line: "2FA8E6" });
    txt(s, "For most SOCs: both", { x: x2 + 0.3, y: 1.75, w: w2 - 0.6, h: 0.5, fontSize: 20, bold: true, color: WHITE });
    bullets(s, ["Perception as the backbone - Microsoft maintains the agents and handoffs", "Custom agents for the scenarios that are yours", "One control standard for both"],
      { x: x2 + 0.3, y: 2.4, w: w2 - 0.6, h: 2.4, fontSize: 15 });
    txt(s, "The cost of an agent is the years you run it.", { x: x2 + 0.3, y: 5.0, w: w2 - 0.6, h: 1.0, fontSize: 16, italic: true, color: BLUE });
  }

  // 33 ── Monday morning
  section("Close");
  {
    const s = content("Monday morning: six moves",
      "~2 min. A checklist. Order matters: inventory and identity first, because nothing else is governable until every agent has a sponsor and its own identity. Number 4 is time-critical - the 31 March 2027 retirements.");
    const items = [
      ["FaListCheck", "Inventory your agents", "Every agent: a sponsor, an owner, and its own identity - or a dedicated least-privileged account."],
      ["FaHand", "Gate the hard actions", "List them: isolate, disable, delete, CA changes, enable rules. Approval on those only."],
      ["FaVial", "Write the gate test", "The error you can't afford, as a zero-tolerance eval - run on every change."],
      ["FaCalendarXmark", "Check 31 March 2027", "Connected agents or Sentinel in the Azure portal? Plan the migration now."],
      ["FaFileContract", "Type your handoffs", "Schema, identifiers, evidence refs, versions, a hop limit."],
      ["FaCalculator", "Run the numbers", "Fork Demo 6's assumptions; get a Perception figure from the cost calculator."],
    ];
    const colW = (W - 2 * M - 0.3) / 2;
    for (let i = 0; i < items.length; i++) {
      const col = i % 2, row = Math.floor(i / 2);
      const x = M + col * (colW + 0.3), y = 1.45 + row * 1.7;
      card(s, x, y, colW, 1.5);
      await badge(s, x + 0.3, y + 0.35, 0.75, items[i][0], i === 3 ? RED : BLUE);
      txt(s, [{ text: `${i + 1}. ${items[i][1]}`, options: { bold: true, color: WHITE, breakLine: true } }, { text: items[i][2], options: { fontSize: 14 } }],
        { x: x + 1.3, y: y + 0.15, w: colW - 1.55, h: 1.25, fontSize: 18 });
    }
  }

  // 34 ── Resources
  {
    const s = content("Take it home",
      "~1 min. Everything is in the repo: the deck, six demos that run offline with only the Python standard library, the browser demo site, and SOURCES.md listing every Learn page used - Perception's docs are moving fast, so check them before you rely on a detail.");
    const qr = 2.2, qrGap = 0.35;
    const qrs = [
      { img: "qr-demo-site.png", name: "qr-demo-site", head: "Run the demos", col: BLUE, lines: ["eldk2027-demos", ".vercel.app"], url: "https://" + DEMO_SITE },
      { img: "qr-repo.png", name: "qr-repo", head: "Get the code", col: ICE, lines: ["github.com/rod-trent", "/Conferences"], url: "https://" + SITE },
    ];
    for (let i = 0; i < qrs.length; i++) {
      const q = qrs[i], x = M + i * (qr + qrGap);
      s.addImage({ path: path.join(__dirname, q.img), x, y: 1.6, w: qr, h: qr, objectName: q.name, hyperlink: { url: q.url } });
      txt(s, q.head, { x, y: 3.95, w: qr, h: 0.4, fontSize: 17, bold: true, color: q.col });
      txt(s, [{ text: q.lines[0], options: { breakLine: true, hyperlink: { url: q.url } } }, { text: q.lines[1], options: { hyperlink: { url: q.url } } }],
        { x, y: 4.35, w: qr, h: 0.6, fontSize: 12, color: BODY });
    }
    txt(s, "Six offline demos, the browser demo site, and every Learn source.", { x: M, y: 5.35, w: 2 * qr + qrGap, h: 0.7, fontSize: 13, color: MUTED });
    const links = [
      ["Microsoft Perception (agentic security)", "learn.microsoft.com/security/agentic-security/agentic-security-overview"],
      ["Perception playbooks", "learn.microsoft.com/security/agentic-security/agentic-security-playbooks"],
      ["Security Copilot custom agents", "learn.microsoft.com/copilot/security/developer/custom-agent-overview"],
      ["Microsoft Entra Agent ID best practices", "learn.microsoft.com/entra/agent-id/best-practices-agent-id"],
      ["AI agent orchestration patterns", "learn.microsoft.com/azure/architecture/ai-ml/guide/ai-agent-design-patterns"],
      ["Sentinel MCP server", "learn.microsoft.com/azure/sentinel/datalake/sentinel-mcp-overview"],
      ["Phishing Triage Agent", "learn.microsoft.com/defender-xdr/phishing-triage-agent"],
    ];
    for (let i = 0; i < links.length; i++) {
      const y = 1.5 + i * 0.72;
      txt(s, [{ text: links[i][0], options: { bold: true, color: WHITE, breakLine: true } },
              { text: links[i][1], options: { color: ICE, fontSize: 11, hyperlink: { url: "https://" + links[i][1] } } }],
        { x: 5.8, y, w: W - M - 5.8, h: 0.65, fontSize: 15 });
    }
  }

  // 35 ── Thanks
  {
    const s = pres.addSlide({ masterName: "SECTION", sectionTitle });
    s.addText("Tak! Questions?", { placeholder: "title" });
    s.addText("Design the controls first. Type the handoffs. Buy what's standard; build what's yours.", { placeholder: "body" });
    txt(s, "Rod Trent  ·  linkedin.com/in/rodtrent  ·  #ELDK27", { x: M, y: 4.95, w: 10, h: 0.5, fontSize: 18, color: BLUE });
    s.addImage({ path: path.join(__dirname, "logo-white.png"), x: M, y: 0.6, w: 3.0, h: 3.0 / LOGO_AR });
    s.addNotes("Q&A. Remind them the demo site works offline once loaded, and SOURCES.md lists every Learn page - Perception's docs changed weekly through late 2026, so check the status lines before quoting them.");
  }

  await pres.writeFile({ fileName: OUT });
  if (SKILL) {
    const { applyTheme } = require(path.join(SKILL, "scripts/apply_theme.js"));
    await applyTheme(OUT, THEME);
  }
  console.log("wrote", OUT);
})().catch(e => { console.error(e); process.exit(1); });
