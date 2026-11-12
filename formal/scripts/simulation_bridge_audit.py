#!/usr/bin/env python3
"""Audit checked-in simulation source and export a conservative Lean handoff.

This is static inspection of pinned SOURCE CODE, not a numerical re-run,
historical TLE authentication or proof about future trajectories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SNAPSHOT_COMMIT = "38ee0f01134f6a1ee07c9346945d058d2ad3ce0b"
REPO = "https://github.com/franklinbaldo/conde-incident"
LEGACY = {
    "src/lib/astrodynamics.ts": "2e9cf26b2814d8c481b01e40dd9201f3df81f673",
    "src/lib/monteCarlo.ts": "e52ca3b55a48371dadcfa6fe82092c665669e14f",
    "src/lib/inverseSolver.ts": "6f953efe001ed6d58afe6760d743b87250b2033b",
    "src/lib/constants.ts": "0284f1217557b0ea891b5e51b6ac56bd13529d3f",
    "norad528_reconstruction.py": "00f6ad767a00ed9b0a166817913d02b4272e47b0",
}
CASTOR_REVIEW = {
    "pull_request": "https://github.com/franklinbaldo/conde-incident/pull/5",
    "head_read": "3074ae0f014ce33a2c81dacb2a7400f92f4a4359",
    "status": "SOURCE_TEXT_READ_ONLY_NOT_EXECUTED_BY_THIS_AUDIT",
    "modules": {
        "src/lib/orbitPhysics.ts": "ccd4f3e2d17aab047182c540e7ac15a280fc41b6",
        "src/lib/orbitAdmissibility.ts": "9c65e6979ee8c5c325bc3d2a3139802827f74814",
        "src/lib/orbitHoldoutAudit.ts": "1aeddbf6eed4e46638fd69de9555daaebf3f2cbb",
        "src/lib/orbitEnergyAudit.ts": "e383221d8dd96bd7f20b3b47fcc9a9469528f0b8",
    },
    "premises_to_verify_before_historical_inference": [
        "independent original epoch-and-frame observations",
        "lineage and actual source custody",
        "calibrated 1963 atmosphere and CdA/m",
        "rigorous numerical error bound and event convergence",
        "blind 527/529 observational holdouts",
        "material survival and ground-impact model",
    ],
    "historical_holdout": "NOT_RUN",
    "lean_proof_of_typescript": "NOT_RUN",
    "terminal_location": None,
    "ground_impact": None,
}
CHECKS = {
    "src/lib/astrodynamics.ts": (
        ("catalogue_midnight_cutoff", "new Date('1963-11-08T23:59:59Z')",
         "catalogued day used as propagation stop; not a measured reentry epoch",
         ("C131#1", "C197#1")),
        ("uncalibrated_envelope", "sigmaKm: Math.sqrt(crossTrackKm * crossTrackKm + alongTrackKm * alongTrackKm)",
         "computed ellipse width has no empirical sigma calibration",
         ("C127#1", "C128#1")),
        ("synthetic_triangulation", "bracketingVerdict: `A trajetória do 528 está delimitada",
         "bracketing prose is not a physical bound from independent observations",
         ("C139#1", "C142#1")),
        ("fabricated_fallback", "distanceToCondeKm: 0,",
         "no positional datum must be substituted by a zero-distance fallback",
         ("C139#1",)),
    ),
    "src/lib/monteCarlo.ts": (
        ("independent_terminal_phase", "const entryArgLatitudeRad = Math.random() * 2 * Math.PI",
         "synthetic phase is independent of calibrated terminal dynamics",
         ("C127#1", "C130#1")),
        ("legacy_orbit_angle", "const raanAtDecayDeg = (284.152 + totalNodalShiftDeg + 360) % 360",
         "RAAN conflicts with the 528 numerical mirrored element",
         ("C179#1",)),
        ("false_probability_name", "empiricalProbability100Km:",
         "finite synthetic frequency cannot be a historical impact posterior",
         ("C130#1",)),
    ),
    "src/lib/constants.ts": (
        ("conflicting_raan", "raanDeg: 284.1520, // Reconstructed nodal angle at epoch",
         "same source conflicts with C179 RAAN 198.5261 degrees",
         ("C179#1",)),
    ),
    "src/lib/inverseSolver.ts": (
        ("unvalidated_baseline", "Unvalidated historical-TLE extrapolation (SGP4 baseline)",
         "candidate pass is not a verified terminal reentry",
         ("C126#1", "C127#1")),
    ),
    "norad528_reconstruction.py": (
        ("python_legacy_raan", "RAAN_528_DEG = 284.1520",
         "legacy orbital parameter disputed by C179",
         ("C179#1",)),
    ),
}


class BridgeAuditError(ValueError):
    pass


def git_blob_sha1(content: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(content)).encode("ascii") + b"\0" + content
    ).hexdigest()


def audit_files(files: dict[str, bytes], *, verify_sha: bool = True) -> dict:
    findings = []
    for path, sha in LEGACY.items():
        if path not in files:
            raise BridgeAuditError(f"missing simulation source {path}")
        data = files[path]
        found = git_blob_sha1(data)
        if verify_sha and found != sha:
            raise BridgeAuditError(
                f"source {path} SHA drift {found} != {sha}; reinspect model first"
            )
        source = data.decode("utf-8")
        for code, pattern, limit, evidence in CHECKS.get(path, ()):
            if pattern not in source:
                raise BridgeAuditError(
                    f"{path} changed: expected pattern {code!r} absent; review required"
                )
            findings.append({
                "id": code,
                "source": path,
                "url": f"{REPO}/blob/{SNAPSHOT_COMMIT}/{path}",
                "blob_sha1": found,
                "evidence_occurrences": list(evidence),
                "classification": "INSPECTED_SOURCE_PATTERN_NOT_VALIDATED_PHYSICS",
                "blocking_limitation": limit,
            })
    return {
        "schema_version": 1,
        "status": "STATIC_SOURCE_INSPECTION_ONLY",
        "source_commit": SNAPSHOT_COMMIT,
        "checked_file_count": len(files),
        "finding_count": len(findings),
        "findings": findings,
        "castor": CASTOR_REVIEW,
        "lean": {
            "module": "Conde1963.SimulatorBridge",
            "contract": "HistoricallyAdmissible/GroundImpactAdmissible",
            "certifies_typescript_execution": False,
            "symbolic_drag_sign_only": True,
            "sample_radius_counts_not_probabilities": True,
            "original_154_propositions_151_labels": "NOT_RUN",
            "testable_physical_historical_conclusion": None,
        },
        "actual_1963_ground_impact": None,
        "calibrated_uncertainty_probability": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    try:
        out = audit_files({
            path: (args.root / path).read_bytes() for path in LEGACY
        })
        if args.json is not None:
            args.json.write_text(json.dumps(out, ensure_ascii=False, indent=2)
                                 + "\n", encoding="utf-8")
    except (BridgeAuditError, UnicodeDecodeError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 1
    print(json.dumps({
        "status": out["status"],
        "checked_file_count": out["checked_file_count"],
        "finding_count": out["finding_count"],
        "castor_physics_validation": "NOT_RUN",
        "historical_location": None,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
