import test from "node:test";
import assert from "node:assert/strict";
import { assessPagesMetadata, inspectPagesMetadata, SITE } from "./pages-metadata-preflight.mjs";

const SHA = "a".repeat(40);
const OTHER = "b".repeat(40);
function valid() {
  return {
    sha: SHA,
    repo: { has_pages: true },
    pages: { build_type: "workflow", html_url: SITE },
    mainSHA: SHA,
    mainSHAAfter: SHA,
    runs: [{
      id: 9, name: "Publish Conde site", path: ".github/workflows/pages.yml@main",
      event: "push", head_branch: "main", head_sha: SHA,
      status: "completed", conclusion: "success", run_number: 9
    }],
    deployments: [{ id: 100, sha: SHA, environment: "github-pages", created_at: "2026-11-12T14:00:00Z" }],
    statuses: { 100: [{ state: "success" }] }
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
test("main moving during audit fails closed", () => refuse(i => { i.mainSHAAfter = OTHER; }, "changed during audit"));
test("wrong deployment environment cannot be accepted", () => refuse(i => { i.deployments[0].environment = "production"; }, "not github-pages"));

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
  assert.ok(paths.includes("/deployments/100/statuses?per_page=1"));
});
test("API failures are NOT_VERIFIED, not published", async () => {
  const result = await inspectPagesMetadata({
    sha: SHA,
    fetchImpl: async () => { throw Error("simulated rate limit"); }
  });
  assert.equal(result.status, "NOT_VERIFIED");
  assert.match(result.failures.join(), /simulated rate limit/);
});
