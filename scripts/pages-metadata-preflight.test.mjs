import test from "node:test";
import assert from "node:assert/strict";
import { assessPagesMetadata, inspectPagesMetadata, SITE } from "./pages-metadata-preflight.mjs";

const SHA = "a".repeat(40);
const OTHER = "b".repeat(40);
function valid() {
  return {
    sha: SHA,
    repo: { has_pages: true },
    repoAfter: { has_pages: true },
    pages: { build_type: "workflow", html_url: SITE },
    pagesAfter: { build_type: "workflow", html_url: SITE },
    mainSHA: SHA,
    mainSHAAfter: SHA,
    runs: [{
      id: 9, name: "Publish Conde site", path: ".github/workflows/pages.yml@main",
      event: "push", head_branch: "main", head_sha: SHA,
      status: "completed", conclusion: "success", run_number: 9, run_attempt: 1
    }],
    runsAfter: [{
      id: 9, name: "Publish Conde site", path: ".github/workflows/pages.yml@main",
      event: "push", head_branch: "main", head_sha: SHA,
      status: "completed", conclusion: "success", run_number: 9, run_attempt: 1
    }],
    deployments: [{ id: 100, sha: SHA, environment: "github-pages", created_at: "2026-11-12T14:00:00Z" }],
    deploymentsAfter: [{ id: 100, sha: SHA, environment: "github-pages", created_at: "2026-11-12T14:00:00Z" }],
    statuses: { 100: [{ id: 501, state: "success" }] },
    statusesAfter: { 100: [{ id: 501, state: "success" }] }
  };
}
function refuse(edit, expected) {
  const input = valid();
  edit(input);
  const result = assessPagesMetadata(input);
  assert.equal(result.status, "NOT_VERIFIED");
  assert.ok(result.failures.some(failure => failure.includes(expected)), JSON.stringify(result.failures));
}
test("even complete metadata never asserts site publication", () => {
  const result = assessPagesMetadata(valid());
  assert.equal(result.status, "METADATA_ONLY_SITE_NOT_VERIFIED");
  assert.equal(result.failures.length, 0);
  assert.match(result.note, /never proves live HTTPS/i);
});
test("invalid SHA fails closed", () => refuse(i => { i.sha = "main"; }, "invalid expected SHA"));
test("Pages absent fails closed", () => refuse(i => { i.repo.has_pages = false; }, "has_pages"));
test("GitHub Pages must use workflow source", () => refuse(i => { i.pages.build_type = "legacy"; }, "source"));
test("Pages must point at this repository URL", () => refuse(i => { i.pages.html_url = "https://untrusted.test"; }, "URL"));
test("main must match expected commit", () => refuse(i => { i.mainSHA = OTHER; }, "main HEAD differs"));
test("run must come from push/main", () => refuse(i => { i.runs[0].event = "workflow_dispatch"; }, "no publish"));
test("run must come from intended publication workflow path", () => refuse(i => { i.runs[0].path = ".github/workflows/integration-head.yml@main"; }, "no publish"));
test("run must match the current commit", () => refuse(i => { i.runs[0].head_sha = OTHER; }, "run does not target"));
test("latest failed run overrides older green for same SHA", () => refuse(i => {
  const old = { ...i.runs[0], id: 1, run_number: 1 };
  i.runs = [old, { ...old, id: 2, run_number: 2, conclusion: "failure" }];
}, "not completed/success"));
test("deployment cannot be borrowed from different SHA", () => refuse(i => { i.deployments[0].sha = OTHER; }, "deployment does not target"));
test("most recent deployment overrides older successful deployment", () => refuse(i => {
  const old = i.deployments[0];
  i.deployments = [old, { ...old, id: 101, created_at: "2026-11-12T15:00:00Z" }];
  i.statuses[101] = [{ state: "pending" }];
}, "status is not success"));
test("missing deployment status fails closed", () => refuse(i => { i.statuses = {}; }, "status is not success"));
test("missing attempt identity fails closed", () => refuse(i => {
  delete i.runs[0].run_attempt;
}, "attempt is not identified"));
test("rerun attempt with same run ID and green conclusion invalidates scan", () => refuse(i => {
  i.runsAfter[0].run_attempt = 2;
}, "publish run changed"));
test("missing deployment status identity fails closed", () => refuse(i => {
  delete i.statuses[100][0].id;
}, "status ID is not identified"));
test("replacement green status with new ID invalidates scan", () => refuse(i => {
  i.statusesAfter[100][0].id = 502;
}, "deployment status changed"));

test("main moving during audit fails closed", () => refuse(i => { i.mainSHAAfter = OTHER; }, "changed during audit"));
test("wrong deployment environment cannot be accepted", () => refuse(i => { i.deployments[0].environment = "production"; }, "not github-pages"));
test("new failed publish attempt arriving during scan invalidates metadata", () => refuse(i => {
  i.runsAfter.unshift({ ...i.runs[0], id: 10, run_number: 10, conclusion: "failure" });
}, "publish run changed"));
test("running publish attempt changing status invalidates metadata", () => refuse(i => {
  i.runsAfter[0].status = "in_progress";
}, "publish run changed"));
test("newer deployment arriving during scan invalidates metadata", () => refuse(i => {
  i.deploymentsAfter.unshift({ ...i.deployments[0], id: 101, created_at: "2026-11-12T15:00:00Z" });
  i.statusesAfter[101] = [{ state: "success" }];
}, "Pages deployment changed"));
test("deployment status revoked during scan invalidates metadata", () => refuse(i => {
  i.statusesAfter[100] = [{ state: "failure" }];
}, "Pages deployment status changed"));
test("Pages source switching during scan invalidates metadata", () => refuse(i => {
  i.pagesAfter.build_type = "legacy";
}, "Pages source or URL changed"));
test("Pages feature disabled during scan invalidates metadata", () => refuse(i => {
  i.repoAfter.has_pages = false;
}, "repository Pages flag changed"));

test("read-only collection checks Pages, workflow, deployment and second HEAD", async () => {
  const responses = new Map([
    ["", { has_pages: true }],
    ["/pages", { build_type: "workflow", html_url: SITE }],
    ["/branches/main", { commit: { sha: SHA } }],
    ["/actions/workflows/pages.yml/runs?branch=main&event=push&per_page=30", { workflow_runs: valid().runs }],
    ["/deployments?environment=github-pages&per_page=30", valid().deployments],
    ["/deployments/100/statuses?per_page=1", [{ state: "success" }]]
  ]);
  const paths = [];
  const result = await inspectPagesMetadata({
    sha: SHA,
    fetchImpl: async (url, options) => {
      assert.equal(options.method, "GET");
      assert.ok(url.startsWith("https://api.github.com/repos/franklinbaldo/conde-incident"));
      const path = url.slice("https://api.github.com/repos/franklinbaldo/conde-incident".length);
      paths.push(path);
      return { ok: responses.has(path), json: async () => responses.get(path) };
    }
  });
  assert.equal(result.status, "METADATA_ONLY_SITE_NOT_VERIFIED");
  assert.equal(paths.filter(path => path === "/branches/main").length, 2);
  assert.equal(paths.filter(path => path === "/pages").length, 2);
  assert.equal(paths.filter(path => path.includes("/actions/workflows/pages.yml/runs")).length, 2);
  assert.equal(paths.filter(path => path === "/deployments/100/statuses?per_page=1").length, 2);
});
test("API failures are NOT_VERIFIED, not published", async () => {
  const result = await inspectPagesMetadata({
    sha: SHA,
    fetchImpl: async () => { throw Error("simulated rate limit"); }
  });
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /simulated rate limit/);
});
