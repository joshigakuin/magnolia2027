/* Build printable QR SVGs from the location-number table in ../index.html. */
const fs = require("node:fs");
const path = require("node:path");

global.window = {};
class SvgNode {
  constructor(tagName) {
    this.tagName = tagName;
    this.attributes = {};
    this.children = [];
  }
  setAttribute(name, value) {
    this.attributes[name] = String(value);
  }
  appendChild(child) {
    this.children.push(child);
    return child;
  }
}
global.document = {
  createElementNS: (_namespace, tagName) => new SvgNode(tagName),
  createElement: (tagName) => new SvgNode(tagName),
};

const { BrowserQRCodeSvgWriter } = require("./zxing-browser.min.js");
const writer = new BrowserQRCodeSvgWriter();
const projectRoot = path.join(__dirname, "..");
const source = fs.readFileSync(path.join(projectRoot, "index.html"), "utf8");
const locations = [
  ...source.matchAll(
    /\{\s*id:\s*"([^"]+)"\s*,\s*number:\s*"([^"]*)"\s*,\s*name:\s*"([^"]+)"/g,
  ),
]
  .filter(([, , number]) => number)
  .map(([, id, number, name]) => ({ id, number, name }));
const samples = [
  ...locations,
  { id: "unknown", number: "9999", name: "未登録テスト" },
];
const outputDirectory = path.join(projectRoot, "images", "qr-tests");
fs.mkdirSync(outputDirectory, { recursive: true });

function serialize(node) {
  const attributes = Object.entries(node.attributes)
    .map(([name, value]) => `${name}="${value.replaceAll('"', "&quot;")}"`)
    .join(" ");
  if (node.tagName === "rect") return `<rect ${attributes}/>`;
  return `<${node.tagName} ${attributes}>${node.children.map(serialize).join("")}</${node.tagName}>`;
}

for (const sample of samples) {
  const qr = writer.write(sample.number, 280, 280);
  const withBackground = serialize(qr).replace(
    ">",
    '><rect x="0" y="0" width="100%" height="100%" fill="#fff"/>',
  );
  const svg = withBackground.replace(
    "<svg ",
    '<svg xmlns="http://www.w3.org/2000/svg" ',
  );
  fs.writeFileSync(path.join(outputDirectory, `${sample.number}.svg`), svg);
}
console.log(
  `Generated ${samples.length} sample QR SVGs from the location table.`,
);
