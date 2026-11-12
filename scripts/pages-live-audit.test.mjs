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
  const metadataReads = [];
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
  return { reads, metadataReads, args: {
    sha: SHA, chapterPath: CHAPTER, fetchImpl,
    metadataInspector: async () => {
      const index = metadataReads.length;
      metadataReads.push(index);
      return overrides.metadataResponses?.[index] ?? {
        status: overrides.metadataStatus || "METADATA_ONLY_SITE_NOT_VERIFIED",
        failures: overrides.metadataFailures || [],
        evidence: { runId: 9, attempt: 1, deploymentId: 100, statusId: 501 }
      };
    }
  } };
}

test("green metadata plus live content still does not attest artifact bytes", async () => {
  const f = fixture();
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "LIVE_CONTENT_PRESENT_UNATTESTED");
  assert.equal(result.failures.length, 0);
  assert.deepEqual(new Set(f.reads), new Set([SITE, CHAPTER, LAB, CSS, JS]));
  assert.equal(f.metadataReads.length, 2, "must recheck metadata after HTTPS");
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


test("G21: comment/template-only navigation and asset references cannot verify publication", async () => {
  const f = fixture({ content: {
    [SITE]: ["text/html", '<!doctype html><html><!--<a href="/conde-incident/stories/chapter-one/">Caderno</a><a href="/conde-incident/lab/">Lab</a><link href="/conde-incident/assets/site.css">--><template><a href="/conde-incident/lab/">Lab</a></template></html>'],
    [LAB]: ["text/html", '<html><!--<script src="/conde-incident/lab/assets/main.js"></script>--></html>'],
    [CHAPTER]: ["text/html", '<html><article><h1>Real page</h1></article></html>'],
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /homepage has no laboratory link/);
  assert.match(result.failures.join(), /homepage has no link to audited chapter/);
  assert.match(result.failures.join(), /homepage has no local CSS asset/);
  assert.match(result.failures.join(), /laboratory has no local JS asset/);
});

test("G21: script string and comment cannot masquerade as a rendered article", async () => {
  const chapter = '<!doctype html><html><script>const ghost = "<article>fake</article>";</script><!--<article>also fake</article>--><template><article>hidden</article></template></html>';
  const f = fixture({ content: { [CHAPTER]: ["text/html", chapter] } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /chapter has no rendered article/);
});

test("G21: whitespace-only CSS and JS are not deployed bundles", async () => {
  for (const [path, mime] of [[CSS, "text/css"], [JS, "application/javascript"]]) {
    const f = fixture({ content: { [path]: [mime, " \n\t "] } });
    const result = await auditPublishedSite(f.args);
    assert.equal(result.status, "NOT_VERIFIED", path);
    assert.match(result.failures.join(), /missing (css|js) body/);
  }
});

test("G21: homepage links embedded in script strings do not count as navigation", async () => {
  const f = fixture({ content: {
    [SITE]: ["text/html", '<!doctype html><html><link rel="stylesheet" href="/conde-incident/assets/site.css"><script>const fake = \'<a href="/conde-incident/lab/">Lab</a><a href="/conde-incident/stories/chapter-one/">Story</a>\';</script></html>'],
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /homepage has no laboratory link/);
  assert.match(result.failures.join(), /homepage has no link to audited chapter/);
});

test("G22: quoted HTML attribute payloads cannot impersonate navigation, CSS, article or JS", async () => {
  const fakeHome = `<!doctype html><html><div data-snapshot='<a href="/conde-incident/stories/chapter-one/">ghost</a><a href="/conde-incident/lab/">ghost</a><link href="/conde-incident/assets/site.css">'>No links</div></html>`;
  const fakeChapter = `<!doctype html><html><p title='<article>not rendered</article>'>Text only</p></html>`;
  const fakeLab = `<!doctype html><html><div data-snapshot='<script src="/conde-incident/lab/assets/main.js"></script>'>No script</div></html>`;
  const f = fixture({ content: {
    [SITE]: ["text/html", fakeHome],
    [CHAPTER]: ["text/html", fakeChapter],
    [LAB]: ["text/html", fakeLab]
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(" | "), /homepage has no laboratory link/);
  assert.match(result.failures.join(" | "), /homepage has no link to audited chapter/);
  assert.match(result.failures.join(" | "), /homepage has no local CSS asset/);
  assert.match(result.failures.join(" | "), /chapter has no rendered article/);
  assert.match(result.failures.join(" | "), /laboratory has no local JS asset/);
  assert.deepEqual(new Set(f.reads), new Set([SITE, CHAPTER, LAB]));
});

test("G22: real tags following a quoted fake tag remain inspectable", async () => {
  const fake = `<div data-snapshot='<a href="/conde-incident/lab/">ghost</a>'>metadata only</div>`;
  const f = fixture({ content: {
    [SITE]: ["text/html", pages[SITE][1].replace("<body>", "<body>" + fake)]
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "LIVE_CONTENT_PRESENT_UNATTESTED");
  assert.equal(result.failures.length, 0);
});

const GREEN = {
  status: "METADATA_ONLY_SITE_NOT_VERIFIED",
  failures: [], evidence: { runId: 9, attempt: 1, deploymentId: 100, statusId: 501 }
};
test("G21-F2: newer deployment during HTTPS scan invalidates live verdict", async () => {
  const f = fixture({ metadataResponses: [
    GREEN, { ...GREEN, evidence: { ...GREEN.evidence, deploymentId: 101, statusId: 502 } }
  ] });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /identity changed/);
  assert.equal(f.metadataReads.length, 2);
});
test("G21-F2: failed replacement run discovered after HTTPS invalidates verdict", async () => {
  const f = fixture({ metadataResponses: [
    GREEN, { status: "NOT_VERIFIED", failures: ["latest publish run is not completed/success"],
      evidence: null }
  ] });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /gate failed after HTTPS scan/);
  assert.match(result.failures.join(), /not completed\/success/);
});
test("G21-F2: post-HTTPS metadata read error fails closed", async () => {
  const f = fixture();
  let calls = 0;
  const result = await auditPublishedSite({ ...f.args, metadataInspector: async () => {
    if (calls++ === 0) return GREEN;
    throw Error("postscan unavailable");
  } });
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /postscan unavailable/);
});
test("G21-F2: missing deploy identity cannot verify content", async () => {
  const f = fixture({ metadataResponses: [{ ...GREEN, evidence: null }] });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.equal(f.reads.length, 0);
});


test("G23: href/src text inside quoted data attributes does not provide navigation or assets", async () => {
  const fakeHome = `<!doctype html><html><head><link data-snapshot='href="/conde-incident/assets/site.css"'></head><body><a data-snapshot='href="/conde-incident/stories/chapter-one/"'>Caderno</a><a data-snapshot='href="/conde-incident/lab/"'>Laboratório</a></body></html>`;
  const fakeLab = `<!doctype html><html><script data-snapshot='src="/conde-incident/lab/assets/main.js"'></script></html>`;
  const f = fixture({ content: {
    [SITE]: ["text/html", fakeHome],
    [LAB]: ["text/html", fakeLab]
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(" | "), /homepage has no laboratory link/);
  assert.match(result.failures.join(" | "), /homepage has no link to audited chapter/);
  assert.match(result.failures.join(" | "), /homepage has no local CSS asset/);
  assert.match(result.failures.join(" | "), /laboratory has no local JS asset/);
  assert.deepEqual(new Set(f.reads), new Set([SITE, CHAPTER, LAB]));
});

test("G23: genuine quoted attributes survive adjacent fake attribute values", async () => {
  const f = fixture({ content: {
    [SITE]: ["text/html", pages[SITE][1]
      .replace('<link rel="stylesheet"', `<link data-note='href="/wrong.css"' rel="stylesheet"`)
      .replace('<a href="/conde-incident/lab/"', `<a data-note='href="/wrong"' href="/conde-incident/lab/"`)],
    [LAB]: ["text/html", `<!doctype html><html><script data-note='src="/wrong.js"' src="/conde-incident/lab/assets/main.js"></script></html>`]
  } });
  const result = await auditPublishedSite(f.args);
  assert.equal(result.status, "LIVE_CONTENT_PRESENT_UNATTESTED");
  assert.equal(result.failures.length, 0);
  assert.equal(f.metadataReads.length, 2);
});
