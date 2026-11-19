// Renders react-icons to PNG data URIs for pptxgenjs.
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");

const cache = {};
async function icon(name, color = "#FFFFFF", size = 256) {
  const key = `${name}-${color}-${size}`;
  if (cache[key]) return cache[key];
  const Comp = fa[name];
  if (!Comp) throw new Error("no icon " + name);
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).resize(size, size, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toBuffer();
  cache[key] = "image/png;base64," + buf.toString("base64");
  return cache[key];
}
module.exports = { icon };
