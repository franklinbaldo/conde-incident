#!/usr/bin/env node
/** Read-only, fail-closed live Pages audit; requires the metadata gate to pass first. */
import { pathToFileURL } from "node:url";
import { inspectPagesMetadata, SITE } from "./pages-metadata-preflight.mjs";

const BASE = new URL(SITE);
const PREFIX = BASE.pathname;

function evidenceKey(value) {
  const keys = ["runId", "attempt", "deploymentId", "statusId"];
  if (!value || !keys.every(key => Number.isSafeInteger(value[key]) && value[key] > 0))
    return null;
  return keys.map(key => value[key]).join(":");
}

function internal(raw, base = SITE) {
  try {
    const url = new URL(raw, base);
    if (url.origin !== BASE.origin || !url.pathname.startsWith(PREFIX)) return null;
    if (url.username || url.password) return null;
    url.hash = "";
    return url.href;
  } catch {
    return null;
  }
}

// A comment, template or JS string is not a visible HTML link or article.
// This lightweight check is conservative, not a substitute for DOM parsing.
function inspectableMarkup(html) {
  return html
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<template\b[^>]*>[\s\S]*?<\/template\s*>/gi, "")
    .replace(/<(script|style|textarea)\b([^>]*)>[\s\S]*?<\/\1\s*>/gi,
      (_, tag, attributes) => `<${tag}${attributes}></${tag}>`);
}

// Attribute strings containing "<a ...>" or "<article>" are not elements.
// Read real start tags only, finding '>' outside HTML attribute quotes.
// This remains a conservative tokenizer, not a complete HTML parser.
function tagsNamed(html, name) {
  const found = [];
  let cursor = 0;
  while (cursor < html.length) {
    const start = html.indexOf("<", cursor);
    if (start < 0) break;
    const match = /^<([A-Za-z][\w:-]*)(?=[\s/>])/i.exec(html.slice(start));
    if (!match) { cursor = start + 1; continue; }
    let quote = null, end = start + match[0].length;
    for (; end < html.length; end++) {
      const ch = html[end];
      if (quote) { if (ch === quote) quote = null; }
      else if (ch === "'" || ch === '"') quote = ch;
      else if (ch === ">") break;
    }
    if (end >= html.length) break; // An unclosed tag proves nothing.
    if (match[1].toLowerCase() === name.toLowerCase()) {
      found.push(html.slice(start, end + 1));
    }
    cursor = end + 1;
  }
  return found;
}

// Match attributes only where the HTML tokenizer is between attribute values.
// A real <a data-note='href="/lab/"> is not a navigable anchor.
function quotedAttribute(startTag, wanted) {
  const opener = /^<[A-Za-z][\w:-]*(?=[\s/>])/.exec(startTag);
  if (!opener) return null;
  let cursor = opener[0].length;
  while (cursor < startTag.length) {
    while (/\s/.test(startTag[cursor] || "")) cursor++;
    if (startTag[cursor] === ">" ||
        (startTag[cursor] === "/" && startTag[cursor + 1] === ">")) break;
    const name = /^[A-Za-z_:][A-Za-z0-9_.:-]*/.exec(startTag.slice(cursor));
    if (!name) { cursor++; continue; }
    cursor += name[0].length;
    while (/\s/.test(startTag[cursor] || "")) cursor++;
    if (startTag[cursor] !== "=") continue; // Boolean attribute.
    cursor++;
    while (/\s/.test(startTag[cursor] || "")) cursor++;
    const quote = startTag[cursor];
    if (quote !== "'" && quote !== '"') {
      // Unquoted values are intentionally not accepted as proof of a link.
      while (cursor < startTag.length && !/[\s>]/.test(startTag[cursor])) cursor++;
      continue;
    }
    const end = startTag.indexOf(quote, ++cursor);
    if (end < 0) break;
    const value = startTag.slice(cursor, end);
    cursor = end + 1;
    if (name[0].toLowerCase() === wanted.toLowerCase() && value) return value;
  }
  return null;
}

function elements(html, tag, attribute) {
  return tagsNamed(html, tag)
    .map(item => quotedAttribute(item, attribute))
    .filter(Boolean);
}

function looksHtml(body) {
  return /<!doctype\s+html|<html[\s>]/i.test(body);
}

export async function auditPublishedSite({
  sha, chapterPath, token, fetchImpl = fetch, metadataInspector = inspectPagesMetadata
}) {
  const failures = [];
  const metadata = await metadataInspector({ sha, token, fetchImpl });
  const beforeKey = evidenceKey(metadata?.evidence);
  if (metadata?.status !== "METADATA_ONLY_SITE_NOT_VERIFIED" ||
      !Array.isArray(metadata.failures) || metadata.failures.length || !beforeKey) {
    return {
      status: "NOT_VERIFIED", phase: "metadata",
      failures: ["Pages metadata/deploy gate has not passed", ...(metadata?.failures || [])],
      site: SITE, sha
    };
  }

  const chapter = internal(chapterPath || "");
  if (!chapterPath || !chapter || chapter === SITE ||
      chapter === internal("lab/")) {
    return { status: "NOT_VERIFIED", phase: "content",
      failures: ["explicit same-origin chapterPath under /conde-incident/ is required"],
      site: SITE, sha };
  }

  async function get(url, kind) {
    try {
      const response = await fetchImpl(url, {
        method: "GET", redirect: "error", cache: "no-store",
        headers: { Accept: kind === "html" ? "text/html" : "*/*" }
      });
      if (!response?.ok || response.status !== 200) {
        failures.push("HTTP 200 missing: " + url);
        return "";
      }
      if (response.url && response.url !== url) {
        failures.push("redirect/final URL mismatch: " + url);
        return "";
      }
      const mime = response.headers?.get?.("content-type") || "";
      const expected = kind === "html" ? /text\/html/i :
        kind === "css" ? /text\/css/i : /javascript|ecmascript/i;
      if (!expected.test(mime)) failures.push("unexpected " + kind + " content-type: " + url);
      const body = await response.text();
      if (!body?.trim() || (kind === "html" && !looksHtml(body)))
        failures.push("missing " + kind + " body: " + url);
      return body;
    } catch (error) {
      failures.push("read failed for " + url + ": " + String(error?.message || error));
      return "";
    }
  }

  const home = await get(SITE, "html");
  const homeLinks = elements(inspectableMarkup(home), "a", "href").map(x => internal(x)).filter(Boolean);
  const lab = internal("lab/");
  if (!homeLinks.includes(lab)) failures.push("homepage has no laboratory link");
  if (!homeLinks.includes(chapter)) failures.push("homepage has no link to audited chapter");
  const styles = elements(inspectableMarkup(home), "link", "href").map(x => internal(x)).filter(Boolean)
    .filter(x => /\.css(?:\?|$)/i.test(x));
  if (!styles.length) failures.push("homepage has no local CSS asset");
  const chapterHtml = await get(chapter, "html");
  if (!tagsNamed(inspectableMarkup(chapterHtml), "article").length)
    failures.push("chapter has no rendered article");
  const labHtml = await get(lab, "html");
  const scripts = elements(inspectableMarkup(labHtml), "script", "src").map(x => internal(x, lab)).filter(Boolean)
    .filter(x => /\.m?js(?:\?|$)/i.test(x));
  if (!scripts.length) failures.push("laboratory has no local JS asset");
  for (const css of [...new Set(styles)]) await get(css, "css");
  for (const js of [...new Set(scripts)]) await get(js, "js");

  // A new publish/deploy during the HTTPS scan invalidates the live-content check.
  // Rechecking metadata limits this race but does NOT bind bytes to an artifact digest.
  try {
    const after = await metadataInspector({ sha, token, fetchImpl });
    const afterKey = evidenceKey(after?.evidence);
    if (after?.status !== "METADATA_ONLY_SITE_NOT_VERIFIED" ||
        !Array.isArray(after.failures) || after.failures.length) {
      failures.push("Pages metadata/deploy gate failed after HTTPS scan");
      if (Array.isArray(after?.failures)) failures.push(...after.failures);
    }
    if (!afterKey || afterKey !== beforeKey)
      failures.push("publish run or deployment identity changed during HTTPS scan");
  } catch (error) {
    failures.push("post-HTTPS metadata read failed: " + String(error?.message || error));
  }

  return {
    // Until the site bytes are compared with an authenticated deploy artifact,
    // current HTTPS availability must NOT be called VERIFIED_PUBLICATION.
    status: failures.length ? "NOT_VERIFIED" : "LIVE_CONTENT_PRESENT_UNATTESTED",
    phase: "content", failures, site: SITE, sha, chapter,
    note: "HTTPS content is present at audit time, but bytes are not attested against the deploy artifact."
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const sha = process.argv[2] || process.env.GITHUB_SHA;
  const chapterPath = process.argv[3];
  const result = await auditPublishedSite({
    sha, chapterPath, token: process.env.GITHUB_TOKEN
  });
  console.log(JSON.stringify(result, null, 2));
  // Fail closed as a release attestation until artifact-to-HTTPS binding exists.
  if (result.status !== "VERIFIED_PUBLICATION") process.exitCode = 1;
}
