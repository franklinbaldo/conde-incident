/** Conde GIS contracts: always deterministic offline; official IBGE ZIP replay opt-in.
 * Live absence is NOT_RUN_REMOTE_SOURCE, never evidence of successful retrieval.
 * Bytes/SHAs of the official sources remain pinned in tools/conde_gis.py.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { appendFileSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const root = process.cwd();
const cli = join(root, "tools", "conde_gis.py");
const sourced = (y) =>
  `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_${y}/UFs/BA/BA_Municipios_${y}.zip`;

function report(year, status, detail) {
  const record = `CGEO_LIVE_REPLAY edition=${year} status=${status} detail=${detail}`;
  console.log(record);
  if (process.env.GITHUB_STEP_SUMMARY) {
    appendFileSync(process.env.GITHUB_STEP_SUMMARY, `- ${record}\n`);
  }
}

test("Conde pinned snapshot integrity and temporal veto (offline, mandatory)", () => {
  // Python independently verifies source metadata and coordinate SHA256,
  // point-in-polygon, original CRS, invalid inputs and 1963 refusal.
  execFileSync("python3", [
    "-m", "unittest", "discover", "-s", "tests", "-p", "test_conde_gis.py", "-v",
  ], { cwd: root, stdio: "pipe", timeout: 30000 });

  const raw = execFileSync("python3", [
    cli, "--lon", "-37.61", "--lat", "-11.81", "--point-crs", "EPSG:4674",
    "--date", "1963-11-08", "--boundary-margin-m", "100",
  ], { cwd: root, timeout: 30000 });
  const point = JSON.parse(raw.toString("utf8"));
  assert.equal(point.modern_comparison, "CONSISTENT_MODERN_INSIDE");
  assert.equal(point.historical_1963_membership, "UNRESOLVED_NO_1963_BOUNDARY");
  assert.equal(point.can_constrain_historical_orbital_reentry, false);
});

const liveEnabled = process.env.CONDE_IBGE_LIVE_REPLAY === "1";
test("Official IBGE 2022/2025 ZIP full replay (live, non-gating)",
  { skip: liveEnabled ? false : "NOT_RUN_REMOTE_SOURCE: enable in dedicated IBGE source check",
    timeout: 210000 }, (t) => {
    const temp = mkdtempSync(join(tmpdir(), "conde-gis-live-"));
    try {
      for (const year of [2022, 2025]) {
        const input = join(temp, `BA_Municipios_${year}.zip`);
        const output = join(temp, `conde_ibge_${year}_sirgas2000.json`);
        const official = join(root, "research", "geo", `conde_ibge_${year}_sirgas2000.json`);
        const download = spawnSync("curl", [
          "--fail", "--location", "--silent", "--show-error",
          "--retry", "0", "--connect-timeout", "15", "--max-time", "75",
          "--write-out", "%{http_code}", "--output", input, sourced(year),
        ], { cwd: root, encoding: "utf8", timeout: 85000 });
        const status = download.status;
        const http = Number((download.stdout || "").trim());
        const unavailable = [6, 7, 28, 35, 52, 56].includes(status)
          || download.error?.code === "ETIMEDOUT"
          || (status === 22 && (http === 429 || http >= 500));
        if (unavailable) {
          const reason = `NOT_RUN_REMOTE_SOURCE: IBGE ${year} network unavailable; curl=${status}, http=${http || "none"}`;
          report(year, "NOT_RUN_REMOTE_SOURCE", `curl=${status} http=${http || "none"}`);
          t.skip(reason);
          return;
        }
        assert.equal(download.error, undefined, `curl process error for ${year}`);
        assert.equal(status, 0,
          `IBGE ${year} download failed; curl=${status}, http=${http}, stderr=${(download.stderr || "").slice(0, 400)}`);
        assert.equal(http, 200, `Unexpected IBGE ${year} HTTP status: ${http}`);
        // This rejects wrong/changed bytes: pinned whole ZIP SHA, record SHA,
        // CRS/municipality/DBF and exact generated coordinate output.
        execFileSync("python3", [
          cli, "--extract", input, "--year", String(year), "--output", output,
        ], { cwd: root, timeout: 30000 });
        assert.deepEqual(readFileSync(output), readFileSync(official),
          `IBGE ${year} source replay differs from the committed geometry`);
        report(year, "VERIFIED_REMOTE", "ZIP and SHP SHA256 matched; exact geometry reproduced");
      }
    } finally {
      rmSync(temp, { recursive: true, force: true });
    }
  });
