// Run by tests/test_web_parity.py. Prints search results from the web code as JSON.
// Usage: node tests/parity.js '<json list of cases>'
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "..");
const S = require(path.join(root, "web", "search.js"));
const records = JSON.parse(fs.readFileSync(path.join(root, "data", "sample.json"), "utf8"));
const model = S.makeModel(JSON.parse(fs.readFileSync(path.join(root, "web", "model.json"), "utf8")));
const docVecs = S.buildIndex(model, records);
const cases = JSON.parse(process.argv[2]);
const out = cases.map((c) =>
  S.search(model, records, docVecs, c.q, c.neg, c.w, c.method, 10)
    .map((r) => [r.record.id, r.score])
);
process.stdout.write(JSON.stringify(out));
