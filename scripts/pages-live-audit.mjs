#!/usr/bin/env node
/** Read-only, fail-closed live Pages audit; requires the metadata gate to pass first. */
import { pathToFileURL } from "node:url";
import { inspectPagesMetadata, SITE } from "./pages-metadata-preflight.mjs";

const BASE = new URL(SITE);
const PREFIX = BASE.pathname;

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

function elements(html, tag, attribute) {
  const found = [];
  const tags = html.match(new RegExp("<" + tag + "\\b[^>]*>", "gi")) || [];
  const attributePattern = new RegExp("(?:^|\\s)" + attribute + "\\s*=\\s*(?:\"([^\"]+)\"|'([^']+)')", "i");
  for (const item of tags) {
    const match = item.match(attributePattern);
    if (match) found.push(match[1] || match[2]);
  }
  return found;
}

function looksHtml(body) {
  return /<!doctype\s+html|<html[\s>]/i.test(body);
}

export async function auditPublishedSite({
  sha, chapterPath, token, fetchImpl = fetch, metadataInspector = inspectPagesMetadata
}) {
  const failures = [];
  const metadata = await metadataInspector({ sha, token, fetchImpl });
  if (metadata?.status !== "METADATA_ONLY_SITE_NOT_VERIFIED" ||
      !Array.isArray(metadata.failures) || metadata.failures.length) {
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
      if (!body || (kind === "html" && !looksHtml(body)))
        failures.push("missing " + kind + " body: " + url);
      return body;
    } catch (error) {
      failures.push("read failed for " + url + ": " + String(error?.message || error));
      return "";
    }
  }

  const home = await get(SITE, "html");
  const homeLinks = elements(home, "a", "href").map(x => internal(x)).filter(Boolean);
  const lab = internal("lab/");
  if (!homeLinks.includes(lab)) failures.push("homepage has no laboratory link");
  if (!homeLinks.includes(chapter)) failures.push("homepage has no link to audited chapter");
  const styles = elements(home, "link", "href").map(x => internal(x)).filter(Boolean)
    .filter(x => /\.css(?:\?|$)/i.test(x));
  if (!styles.length) failures.push("homepage has no local CSS asset");
  const chapterHtml = await get(chapter, "html");
  if (!/<article[\s>]/i.test(chapterHtml))
    failures.push("chapter has no rendered article");
  const labHtml = await get(lab, "html");
  const scripts = elements(labHtml, "script", "src").map(x => internal(x, lab)).filter(Boolean)
    .filter(x => /\.m?js(?:\?|$)/i.test(x));
  if (!scripts.length) failures.push("laboratory has no local JS asset");
  for (const css of [...new Set(styles)]) await get(css, "css");
  for (const js of [...new Set(scripts)]) await get(js, "js");

  return {
    status: failures.length ? "NOT_VERIFIED" : "VERIFIED_PUBLICATION",
    phase: "content", failures, site: SITE, sha, chapter,
    note: "Verifies current HTTPS content, not historical claims or permanence of deployment."
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const sha = process.argv[2] || process.env.GITHUB_SHA;
  const chapterPath = process.argv[3];
  const result = await auditPublishedSite({
    sha, chapterPath, token: process.env.GITHUB_TOKEN
  });
  console.log(JSON.stringify(result, null, 2));
  if (result.status !== "VERIFIED_PUBLICATION") process.exitCode = 1;
}
