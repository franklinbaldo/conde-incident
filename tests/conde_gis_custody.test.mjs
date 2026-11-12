/** Official IBGE source replay, running under existing exact-head integration CI.
 * No fixture synthesizes historical limits. Downloads are source acquisitions.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const root = process.cwd();
const cli = join(root, "tools", "conde_gis.py");
const sourced = (y) =>
  `https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_${y}/UFs/BA/BA_Municipios_${y}.zip`;

test("Conde official IBGE 2022/2025 source replay and 1963 temporal veto", () => {
  execFileSync("python3", [
    "-m", "unittest", "discover", "-s", "tests", "-p", "test_conde_gis.py", "-v",
  ], { cwd: root, stdio: "pipe", timeout: 30000 });

  const temp = mkdtempSync(join(tmpdir(), "conde-gis-"));
  try {
    for (const edition of [2022, 2025]) {
      const input = join(temp, `BA_Municipios_${edition}.zip`);
      const output = join(temp, `conde_ibge_${edition}_sirgas2000.json`);
      const official = join(root, "research", "geo", `conde_ibge_${edition}_sirgas2000.json`);
      execFileSync("curl", [
        "--fail", "--location", "--silent", "--show-error",
        "--retry", "2", "--max-time", "90", "--output", input, sourced(edition),
      ], { cwd: root, timeout: 105000 });
      execFileSync("python3", [
        cli, "--extract", input, "--year", String(edition), "--output", output,
      ], { cwd: root, timeout: 30000 });
      assert.deepEqual(readFileSync(output), readFileSync(official),
        `official IBGE ${edition} ZIP replay must reproduce committed geometry exactly`);
    }
    const raw = execFileSync("python3", [
      cli, "--lon", "-37.61", "--lat", "-11.81", "--point-crs", "EPSG:4674",
      "--date", "1963-11-08", "--boundary-margin-m", "100",
    ], { cwd: root, timeout: 30000 });
    const point = JSON.parse(raw.toString("utf8"));
    assert.equal(point.modern_comparison, "CONSISTENT_MODERN_INSIDE");
    assert.equal(point.historical_1963_membership, "UNRESOLVED_NO_1963_BOUNDARY");
    assert.equal(point.can_constrain_historical_orbital_reentry, false);
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
}, { timeout: 260000 });
