#!/usr/bin/env node
/** Read-only Pages metadata preflight. Never asserts that an HTTPS site was published. */
import { pathToFileURL } from "node:url";

export const REPOSITORY = "franklinbaldo/conde-incident";
export const SITE = "https://franklinbaldo.github.io/conde-incident/";
const API = "https://api.github.com/repos/" + REPOSITORY;

export function assessPagesMetadata(input) {
  const failures = [];
  const requireCheck = (condition, reason) => { if (!condition) failures.push(reason); };
  const sha = input?.sha;
  requireCheck(typeof sha === "string" && /^[a-f0-9]{40}$/.test(sha), "invalid expected SHA");
  requireCheck(input?.repo?.has_pages === true, "repository has_pages is not true");
  requireCheck(input?.pages?.build_type === "workflow", "Pages source is not GitHub Actions");
  requireCheck(input?.pages?.html_url === SITE, "Pages URL is not the expected project URL");
  requireCheck(input?.repoAfter?.has_pages === input?.repo?.has_pages && input?.repoAfter?.has_pages === true,
    "repository Pages flag changed during audit");
  requireCheck(input?.pagesAfter?.build_type === input?.pages?.build_type &&
    input?.pagesAfter?.html_url === input?.pages?.html_url,
    "Pages source or URL changed during audit");
  requireCheck(input?.mainSHA === sha, "main HEAD differs from expected SHA");

  // Consider the most recent publish attempt, not any older green run.
  const runs = Array.isArray(input?.runs) ? input.runs.filter(r =>
    r?.name === "Publish Conde site" && r?.event === "push" &&
    r?.head_branch === "main" && typeof r?.path === "string" &&
    /^\.github\/workflows\/pages\.yml(@main)?$/.test(r.path)
  ) : [];
  runs.sort((a, b) => (b.run_number || 0) - (a.run_number || 0));
  const latestRun = runs[0];
  requireCheck(Boolean(latestRun), "no publish push/main workflow run");
  requireCheck(latestRun?.head_sha === sha, "latest publish run does not target expected SHA");
  requireCheck(latestRun?.status === "completed" && latestRun?.conclusion === "success",
    "latest publish run is not completed/success");
  const runsAfter = Array.isArray(input?.runsAfter) ? input.runsAfter.filter(r =>
    r?.name === "Publish Conde site" && r?.event === "push" &&
    r?.head_branch === "main" && typeof r?.path === "string" &&
    /^\.github\/workflows\/pages\.yml(@main)?$/.test(r.path)
  ) : [];
  runsAfter.sort((a, b) => (b.run_number || 0) - (a.run_number || 0));
  const latestRunAfter = runsAfter[0];
  requireCheck(Boolean(latestRunAfter && latestRun) &&
    latestRunAfter.id === latestRun.id &&
    latestRunAfter.head_sha === latestRun.head_sha &&
    latestRunAfter.status === latestRun.status &&
    latestRunAfter.conclusion === latestRun.conclusion,
    "publish run changed during audit");

  // A green workflow is not a Pages deployment. Inspect the newest deployment AND its newest status.
  const deployments = Array.isArray(input?.deployments) ? [...input.deployments] : [];
  deployments.sort((a, b) => (Date.parse(b?.created_at || "") || 0) -
    (Date.parse(a?.created_at || "") || 0) || (Number(b?.id) || 0) - (Number(a?.id) || 0));
  const latestDeployment = deployments[0];
  requireCheck(latestDeployment?.environment === "github-pages", "latest deployment is not github-pages");
  requireCheck(latestDeployment?.sha === sha, "latest Pages deployment does not target expected SHA");
  const deploymentStatuses = input?.statuses?.[latestDeployment?.id] || [];
  requireCheck(Array.isArray(deploymentStatuses) && deploymentStatuses[0]?.state === "success",
    "latest Pages deployment status is not success");
  const deploymentsAfter = Array.isArray(input?.deploymentsAfter) ? [...input.deploymentsAfter] : [];
  deploymentsAfter.sort((a, b) => (Date.parse(b?.created_at || "") || 0) -
    (Date.parse(a?.created_at || "") || 0) || (Number(b?.id) || 0) - (Number(a?.id) || 0));
  const latestDeploymentAfter = deploymentsAfter[0];
  requireCheck(Boolean(latestDeploymentAfter && latestDeployment) &&
    latestDeploymentAfter.id === latestDeployment.id &&
    latestDeploymentAfter.sha === latestDeployment.sha &&
    latestDeploymentAfter.environment === latestDeployment.environment,
    "Pages deployment changed during audit");
  const statusesAfter = input?.statusesAfter?.[latestDeploymentAfter?.id] || [];
  requireCheck(Array.isArray(statusesAfter) && statusesAfter[0]?.state === "success",
    "Pages deployment status changed during audit");
  requireCheck(input?.mainSHAAfter === sha, "main HEAD changed during audit");

  return {
    status: failures.length ? "NOT_VERIFIED" : "METADATA_ONLY_SITE_NOT_VERIFIED",
    failures,
    sha,
    site: SITE,
    note: "This preflight never proves live HTTPS content, CSS, JavaScript or Markdown chapters."
  };
}

export async function inspectPagesMetadata({ sha, token, fetchImpl = fetch }) {
  if (!/^[a-f0-9]{40}$/.test(sha || "")) {
    return assessPagesMetadata({ sha });
  }
  const headers = { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" };
  if (token) headers.Authorization = "Bearer " + token;
  const get = async (path) => {
    const response = await fetchImpl(API + path, { method: "GET", headers, redirect: "error" });
    if (!response.ok) return null;
    return response.json();
  };
  try {
    const repo = await get("");
    const pages = await get("/pages");
    const main = await get("/branches/main");
    const workflow = await get("/actions/workflows/pages.yml/runs?branch=main&event=push&per_page=30");
    const deployments = await get("/deployments?environment=github-pages&per_page=30");
    const statuses = {};
    for (const deployment of Array.isArray(deployments) ? [...deployments].sort((a, b) => (Date.parse(b?.created_at || "") || 0) - (Date.parse(a?.created_at || "") || 0) || (Number(b?.id) || 0) - (Number(a?.id) || 0)).slice(0, 1) : []) {
      if (Number.isSafeInteger(deployment.id)) {
        statuses[deployment.id] = await get("/deployments/" + deployment.id + "/statuses?per_page=1") || [];
      }
    }
    // A new failed run/deployment or changed Pages setting can appear while scanning statuses.
    // Re-read the same control-plane sources before accepting even a metadata-only verdict.
    const repoAfter = await get("");
    const pagesAfter = await get("/pages");
    const workflowAfter = await get("/actions/workflows/pages.yml/runs?branch=main&event=push&per_page=30");
    const deploymentsAfter = await get("/deployments?environment=github-pages&per_page=30");
    const statusesAfter = {};
    for (const deployment of Array.isArray(deploymentsAfter) ? [...deploymentsAfter].sort((a, b) => (Date.parse(b?.created_at || "") || 0) - (Date.parse(a?.created_at || "") || 0) || (Number(b?.id) || 0) - (Number(a?.id) || 0)).slice(0, 1) : []) {
      if (Number.isSafeInteger(deployment.id)) {
        statusesAfter[deployment.id] = await get("/deployments/" + deployment.id + "/statuses?per_page=1") || [];
      }
    }
    const mainAfter = await get("/branches/main");
    return assessPagesMetadata({
      sha, repo, pages, mainSHA: main?.commit?.sha,
      runs: workflow?.workflow_runs, deployments, statuses,
      repoAfter, pagesAfter, runsAfter: workflowAfter?.workflow_runs, deploymentsAfter, statusesAfter,
      mainSHAAfter: mainAfter?.commit?.sha
    });
  } catch (error) {
    return {
      status: "NOT_VERIFIED", failures: ["GitHub read failed: " + String(error?.message || error)],
      sha, site: SITE, note: "No published-site verification was performed."
    };
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const sha = process.argv[2] || process.env.GITHUB_SHA;
  const result = await inspectPagesMetadata({ sha, token: process.env.GITHUB_TOKEN });
  console.log(JSON.stringify(result, null, 2));
  // Fail closed. Even a green metadata preflight does not authorize a publication claim.
  if (result.status === "NOT_VERIFIED") process.exitCode = 1;
}
