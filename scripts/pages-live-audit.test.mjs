import test from "node:test";
import assert from "node:assert/strict";
import { auditPublishedSite } from "./pages-live-audit.mjs";
import { SITE } from "./pages-metadata-preflight.mjs";

const SHA = "a".repeat(40);
const CHAPTER = SITE + "stories/chapter-one/";
const LAB = SITE + "lab/";
const CSS = SITE + "assets/site.css";
const JS = SITE + "lab/assets/main.js";

const pages = {
  [SITE]: ["text/html", '<!doctype html><html><head><link rel="stylesheet" href="/conde-incident/assets/site.css"></head><body><a href="/conde-incident/stories/chapter-one/">Caderno</a><a href="/conde-incident/lab/">Laboratório</a></body></html>'],
  [CHAPTER]: ["text/html", "<!doctype html><html><article><h1>Capítulo</h1></article></html>"],
  [LAB]: ["text/html", '<!doctype html><html><script type="module" src="/conde-incident/lab/assets/main.js"></script></html>'],
  [CSS]: ["text/css", "body { color: black; }"],
  [JS]: ["application/javascript", "console.log('lab');"]
};

function fixture(overrides = {}) {
  const content = { ...pages, ...(overrides.content || {}) };
  const reads = [];
  const fetchImpl = async (url, opts) => {
    assert.equal(opts.method, "GET");
    assert.equal(opts.redirect, "error");
    reads.push(url);
    const record = content[url];
    if (!record) return { ok: false, status: 404, url,
      headers: { get: () => "text/html" }, text: async () => "" };
    return { ok: true, status: 200, url: overrides.redirect === url ? "https://untrusted.test/" : url,
      headers: { get: () => record[0] }, text: async () => record[1] };
  };
  return { reads, args: {
    sha: SHA, chapterPath: CHAPTER, fetchImpl,
    metadataInspector: async () => ({
      status: overrides.metadataStatus || "METADATA_ONLY_SITE_NOT_VERIFIED",
      failures: overrides.metadataFailures || []
    })
  } };
}

test("live HTML, chapter, lab, CSS and JS after green metadata yield verified", async () => {
  const f = fixture();
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "VERIFIED_PUBLICATION");
  assert.equal(result.failures.length, 0);
  assert.deepEqual(new Set(f.reads), new Set([SITE, CHAPTER, LAB, CSS, JS]));
});

test("never fetch public site if publish metadata/deployment gate failed", async () => {
  const f = fixture({ metadataStatus: "NOT_VERIFIED", metadataFailures: ["no deployment"] });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.equal(result.phase, "metadata");
  assert.match(result.failures.join(), /no deployment/);
  assert.equal(f.reads.length, 0);
});

test("refuse absent chapter URL instead of guessing a chapter", async () => {
  const f = fixture();
  const result = await auditPublishedSite({ ...f.args, chapterPath: undefined });
  assert.equal(result.status, "NOT_VERIFIED");
  assert.equal(f.reads.length, 0);
});

test("refuse external and path-escaped chapter URLs", async () => {
  for (const path of ["https://evil.example/story/", SITE + "../other/", "/other/review/"]) {
    const f = fixture();
    const result = await auditPublishedSite({ ...f.args, chapterPath: path });
    assert.equal(result.status, "NOT_VERIFIED", path);
    assert.equal(f.reads.length, 0);
  }
});

test("missing chapter on published homepage fails even if direct URL responds", async () => {
  const f = fixture({ content: {
    [SITE]: ["text/html", '<html><link href="/conde-incident/assets/site.css"><a href="/conde-incident/lab/">Lab</a></html>']
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /homepage has no link to audited chapter/);
});

test("no laboratory navigation fails closed", async () => {
  const f = fixture({ content: {
    [SITE]: ["text/html", '<html><link href="/conde-incident/assets/site.css"><a href="/conde-incident/stories/chapter-one/">Chapter</a></html>']
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /no laboratory link/);
});

test("200 HTML with no rendered article is not enough", async () => {
  const f = fixture({ content: { [CHAPTER]: ["text/html", "<html>Not rendered yet</html>"] } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /rendered article/);
});

test("missing HTML body or MIME mismatch does not count as published", async () => {
  const f = fixture({ content: { [CHAPTER]: ["application/json", "{}"] } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /content-type/);
});

test("missing CSS and JS cannot be accepted just from HTML", async () => {
  const f = fixture({ content: {
    [SITE]: ["text/html", '<html><a href="/conde-incident/stories/chapter-one/">Chapter</a><a href="/conde-incident/lab/">Lab</a></html>'],
    [LAB]: ["text/html", "<html></html>"]
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /no local CSS asset/);
  assert.match(result.failures.join(), /no local JS asset/);
});

test("an asset 404 invalidates otherwise complete publication", async () => {
  const f = fixture({ content: { [JS]: null } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /HTTP 200 missing/);
});

test("redirect and other final URL invalidate published verdict", async () => {
  const f = fixture({ redirect: CHAPTER });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /redirect\/final URL mismatch/);
});

test("network failure rejects publication safely", async () => {
  const f = fixture();
  const result = await auditPublishedSite({ ...f.args,
    fetchImpl: async () => { throw Error("offline"); } });
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /offline/);
});

test("missing status 200 even when response.ok is truthy fails", async () => {
  const f = fixture();
  const result = await auditPublishedSite({ ...f.args,
    fetchImpl: async () => ({
      ok: true, status: 206, url: SITE,
      headers: { get: () => "text/html" }, text: async () => "<html></html>"
    })
  });
  assert.equal(result.status, "NOT_VERIFIED");
});
