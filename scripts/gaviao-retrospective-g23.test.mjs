import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const audit = JSON.parse(readFileSync(new URL("../research/audits/gaviao-main-window-20261112-g23.json", import.meta.url), "utf8"));

test("G23: every first-parent merge has a unique SHA and exactly one previous parent", () => {
  assert.equal(audit.first_parent_integrations, 15);
  assert.equal(audit.commit_graph_total, 15);
  assert.equal(audit.direct_main_commits, 0);
  assert.equal(audit.entries.length, 15);
  let parent = audit.reviewed_from_main_sha;
  for (const entry of audit.entries) {
    assert.match(entry.main_sha, /^[a-f0-9]{40}$/);
    assert.equal(entry.first_parent, parent);
    assert.equal(entry.merge_style, "squash");
    assert.ok(Number.isInteger(entry.pr_number) && entry.pr_number > 0);
    assert.match(entry.author_head_sha, /^[a-f0-9]{40}$/);
    assert.ok(entry.files.length > 0);
    assert.equal(entry.author_head_ci.success + entry.author_head_ci.cancelled,
      entry.author_head_ci.total_returned);
    parent = entry.main_sha;
  }
  assert.equal(parent, audit.reviewed_through_main_sha);
});
test("G23: cancelled Pages is not reported as full author CI success", () => {
  const pr207 = audit.entries.find(x => x.pr_number === 207);
  assert.deepEqual({passed: pr207.author_head_ci.success, cancelled: pr207.author_head_ci.cancelled},
    {passed: 14, cancelled: 1});
  assert.equal(audit.entries.filter(x => x.author_head_ci.cancelled).length, 1);
});
test("G23: metadata/HTML finding cannot be promoted to physical identification", () => {
  assert.ok(audit.findings.some(x => x.id === "G23-F1"));
  assert.match(audit.scientific_status, /INDETERMINATE/);
  assert.ok(!/CONFIRMED_IMPACT|EXCLUDED_CONDE/.test(audit.scientific_status));
});
