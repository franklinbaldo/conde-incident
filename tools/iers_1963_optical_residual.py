#!/usr/bin/env python3
"""G54: source-bound conditional angular residual for G53 geometric GCRS.

Accepts only a fully specified, *geometric instantaneous GCRS* datum whose
timestamp and WGS84 scenario station match the G53 predictor. Historical
FK4/film or apparent positions are deliberately NOT reinterpreted as GCRS.
This numerical contract cannot turn a supplied datum into a verified 1963
NORAD instrument observation or calibrate an unknown error distribution.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping

import numpy as np

from iers_1963_optical import (decode_source_bound_state, forward_source_bound_optical,
                               STATE_SCHEMA)

ARCSEC_RAD = math.pi / (180.0 * 3600.0)
FRAME = "GCRS"
ANGLE_TYPE = "INSTANTANEOUS_GEOMETRIC_NOT_APPARENT_FK4"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXTRACTION_SCHEMA = "GCRS_OPTICAL_EXTRACTION_V1"
EXTRACTION_CLASSES = {"SYNTHETIC_SCENARIO", "SECONDARY_DERIVATIVE_NOT_INSTRUMENT"}


def _verified_extraction(observed: Mapping, raw: bytes) -> tuple[str, str]:
    """Bind typed comparison inputs to extraction bytes, not just to a source PDF hash.

    This is a separately versioned *transcription/derivation* record, not a
    claim that the primary source contained GCRS angles or calibrated errors.
    An attacker can forge both inputs: SHA-256 proves identity, not authorship.
    """
    if not isinstance(raw, bytes) or not raw:
        raise ValueError("Original optical extraction bytes required")

    def unique_pairs(pairs):
        record = {}
        for key, value in pairs:
            if key in record:
                raise ValueError("Duplicate optical extraction key")
            record[key] = value
        return record

    def reject_constant(value):
        raise ValueError("Nonfinite optical extraction constant")

    try:
        extracted = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                               parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Optical extraction must be UTF-8 JSON") from exc
    if not isinstance(extracted, Mapping) or set(extracted) != {
        "schema", "evidence_class", "observation"
    } or extracted["schema"] != EXTRACTION_SCHEMA:
        raise ValueError("Unrecognized optical extraction schema")
    tier = extracted["evidence_class"]
    if not isinstance(tier, str) or tier not in EXTRACTION_CLASSES:
        raise ValueError("Unsupported optical extraction evidence class")
    snapshot = extracted["observation"]
    if not isinstance(snapshot, Mapping):
        raise ValueError("Optical extraction observation must be a record")
    # Byte-for-byte transcription lineage for *all* supplied typed fields.
    # Sorting JSON keys preserves meaning without allowing missing/extra
    # fields; serialized form distinguishes bool from 1 and strings from nums.
    try:
        extracted_values = json.dumps(snapshot, sort_keys=True, allow_nan=False)
        supplied_values = json.dumps(dict(observed), sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("Optical extraction contains non-JSON values") from exc
    if extracted_values != supplied_values:
        raise ValueError("Optical observation differs from original extraction bytes")
    return hashlib.sha256(raw).hexdigest(), tier



def _finite_number(value: object, name: str) -> float:
    if isinstance(value, (bool, str)):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _covariance(value: object, name: str, *, require_pd: bool) -> np.ndarray:
    try:
        arr = np.asarray(value, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a 2x2 covariance") from exc
    if arr.shape != (2, 2) or not np.isfinite(arr).all():
        raise ValueError(f"{name} must be a finite 2x2 covariance")
    # An absolute or global-matrix tolerance could silently admit a negative
    # velocity/angle variance hidden beside a much larger marginal (G52).
    x, y = float(arr[0, 0]), float(arr[1, 1])
    xy, yx = float(arr[0, 1]), float(arr[1, 0])
    if abs(xy - yx) > 1e-12 * max(abs(xy), abs(yx), np.finfo(float).tiny):
        raise ValueError(f"{name} must be symmetric")
    if x < 0 or y < 0:
        raise ValueError(f"{name} must be positive semidefinite")
    if require_pd and (x <= 0 or y <= 0):
        raise ValueError(f"{name} must be positive definite")
    cross = (xy + yx) / 2
    if x == 0 or y == 0:
        if cross != 0:
            raise ValueError(f"{name} must be positive semidefinite")
    else:
        # Dimensionless correlation avoids global scale masking, and avoids
        # overflow from computing x*y when marginal scales are far apart.
        rho = cross / math.sqrt(x) / math.sqrt(y)
        if not math.isfinite(rho) or abs(rho) > (1 - 1e-12 if require_pd else 1 + 1e-12):
            raise ValueError(f"{name} must be {'positive definite' if require_pd else 'positive semidefinite'}")
    return np.array([[x, cross], [cross, y]])


def _unit(ra_deg: float, dec_deg: float) -> np.ndarray:
    ra, dec = math.radians(ra_deg), math.radians(dec_deg)
    return np.array([math.cos(dec) * math.cos(ra),
                     math.cos(dec) * math.sin(ra), math.sin(dec)])


def compare_geometric_gcrs(predicted: Mapping, observed: Mapping,
                           original_document_bytes: bytes, original_state_document_bytes: bytes,
                           original_extraction_bytes: bytes, original_iers_bytes: bytes,
                           eop: Mapping, times: Mapping) -> dict:
    """Evaluate a conditional angular residual, NOT a 527/529 holdout.

    Source PDF bytes and separately versioned typed-extraction JSON bytes
    are required, as well as the TEME state record and original IERS 1963
    bytes. The reported RA/Dec are independently replayed from those inputs.
    Neither digest is
    proof of historical authorship or independence.

    The observation must declare its own instrumental error covariance in
    arcsec^2, document digest, UTC, exact frame/angle type, and station
    geodetic parameters. No uncertainty, catalogue transformation or clock
    correction is silently supplied. Source contract TEME_POSITION_ONLY_V1
    supplies no covariance; accepting an editable predicted covariance could
    artificially suppress an angular residual, so it is rejected.
    """
    if not isinstance(predicted, Mapping) or not isinstance(observed, Mapping):
        raise ValueError("Prediction and observation must be records")
    if predicted.get("output_frame") != FRAME or predicted.get("angle_type") != ANGLE_TYPE:
        raise ValueError("Prediction is not instantaneous geometric GCRS")
    if predicted.get("historical_holdout") != "NOT_RUN":
        raise ValueError("Unexpected historical holdout status")
    if predicted.get("station_coordinate_contract") != "WGS84_GEODETIC_SCENARIO_NOT_1963_SURVEY":
        raise ValueError("Station survey contract is not supported")
    # A geometrically plausible angle is not a match to a NORAD object if
    # its *predicted* Cartesian input has no verified source/content binding.
    binding = predicted.get("state_source_binding")
    if not isinstance(binding, Mapping) or binding.get("schema") != STATE_SCHEMA:
        raise ValueError("Prediction lacks source-bound TEME object identity")
    digest_state = binding.get("document_sha256")
    if not isinstance(digest_state, str) or not SHA256.fullmatch(digest_state):
        raise ValueError("Invalid TEME state source digest")
    if not isinstance(original_state_document_bytes, bytes) or not original_state_document_bytes:
        raise ValueError("Original TEME state source bytes required")
    if hashlib.sha256(original_state_document_bytes).hexdigest() != digest_state:
        raise ValueError("Original TEME state source digest mismatch")
    state_record = decode_source_bound_state(original_state_document_bytes)
    if (state_record["object_id"] != binding.get("object_id") or
            state_record["object_id"] != observed.get("object_id")):
        raise ValueError("Prediction and observation object identities differ")
    if state_record["epoch_utc"] != predicted.get("epoch_utc"):
        raise ValueError("TEME input and predicted UTC epochs differ")
    if state_record["record_class"] != binding.get("record_class"):
        raise ValueError("TEME state source evidence class differs")
    if not isinstance(binding.get("document_uri"), str) or not binding["document_uri"].strip():
        raise ValueError("Missing TEME state source URI")
    try:
        psource = np.asarray(predicted["input_teme_position_km"], dtype=float)
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Missing source-bound TEME coordinates") from exc
    if psource.shape != (3,) or not np.array_equal(psource, state_record["teme_position_km"]):
        raise ValueError("TEME prediction coordinates differ from source bytes")
    if observed.get("frame") != FRAME or observed.get("angle_type") != ANGLE_TYPE:
        raise ValueError("Observation frame/angle type requires explicit conversion")
    if observed.get("instrument_covariance_basis") != "PREDICTED_GCRS_TANGENT_EAST_NORTH":
        raise ValueError("Instrument covariance basis must be predicted GCRS east/north")
    if not isinstance(observed.get("epoch_utc"), str) or observed["epoch_utc"] != predicted.get("epoch_utc"):
        raise ValueError("Unmatched UTC epoch; clock bias is not calibrated")
    for name in ("object_id", "station_id", "document_uri"):
        if not isinstance(observed.get(name), str) or not observed[name].strip():
            raise ValueError(f"Missing observation provenance: {name}")
    digest = observed.get("document_sha256")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        raise ValueError("Expected a lowercase SHA-256 digest")
    if not isinstance(original_document_bytes, bytes) or not original_document_bytes:
        raise ValueError("Original observation source bytes are required")
    if hashlib.sha256(original_document_bytes).hexdigest() != digest:
        raise ValueError("Original observation source digest mismatch")
    ps = predicted.get("station_wgs84_geodetic")
    osite = observed.get("station_wgs84_geodetic")
    if not isinstance(ps, Mapping) or not isinstance(osite, Mapping):
        raise ValueError("Unspecified scenario station")
    for name in ("longitude_deg", "latitude_deg", "height_m"):
        p, o = _finite_number(ps.get(name), name), _finite_number(osite.get(name), name)
        if p != o:
            raise ValueError("Observation station differs from prediction")

    # G58: original state JSON binds the input vector, but did not bind the
    # output RA/Dec to that vector. Recompute with authenticated original IERS
    # bytes and versioned derived EOP/time records, never trust editable angles.
    # The state source is POSITION_ONLY. A caller-provided state covariance is
    # not evidence bound and can arbitrarily reduce Mahalanobis distance.
    if predicted.get("state_only_angular_covariance_rad2") is not None:
        raise ValueError("Unbound state covariance is not admissible with POSITION_ONLY source")
    replayed = forward_source_bound_optical(
        original_iers_bytes, eop, times, predicted["epoch_utc"],
        original_state_document_bytes, binding["document_uri"],
        _finite_number(ps.get("longitude_deg"), "station longitude"),
        _finite_number(ps.get("latitude_deg"), "station latitude"),
        _finite_number(ps.get("height_m"), "station height"))
    for name in ("right_ascension_deg", "declination_deg"):
        candidate = _finite_number(predicted.get(name), "predicted " + name)
        if candidate != replayed[name]:
            raise ValueError("Predicted GCRS angles differ from original IERS/state replay")

    pra = _finite_number(predicted.get("right_ascension_deg"), "predicted RA")
    pdec = _finite_number(predicted.get("declination_deg"), "predicted Dec")
    ora = _finite_number(observed.get("right_ascension_deg"), "observed RA")
    odec = _finite_number(observed.get("declination_deg"), "observed Dec")
    if not (0 <= pra < 360 and 0 <= ora < 360 and -90 < pdec < 90 and -90 < odec < 90):
        raise ValueError("RA/Dec out of normalized domain")
    pred_unit, obs_unit = _unit(pra, pdec), _unit(ora, odec)
    cos_sep = float(pred_unit @ obs_unit)
    if cos_sep <= math.cos(math.radians(5.)):
        raise ValueError("Offset exceeds 5 degrees; tangent-plane linearization invalid")
    a, d = math.radians(pra), math.radians(pdec)
    east = np.array([-math.sin(a), math.cos(a), 0.])
    north = np.array([-math.sin(d)*math.cos(a), -math.sin(d)*math.sin(a), math.cos(d)])
    residual = np.array([east @ obs_unit, north @ obs_unit]) / cos_sep
    # Both angular covariances refer to the predicted tangent frame; the
    # bounded 5-degree domain still requires small-error justification.
    instrument_arcsec2 = _covariance(observed.get("instrument_covariance_arcsec2"),
                                    "Instrument covariance", require_pd=True)
    instrument = instrument_arcsec2 * ARCSEC_RAD**2
    total = instrument
    # Cholesky avoids explicitly inverting a covariance in disparate units.
    # Preserve exact typed-input/extraction binding before emitting a statistic.
    z = np.linalg.solve(np.linalg.cholesky(total), residual)
    chi2 = float(z @ z)
    if not math.isfinite(chi2):
        raise ValueError("Nonfinite angular distance")
    extraction_digest, extraction_tier = _verified_extraction(observed, original_extraction_bytes)
    return {
        "epoch_utc": predicted["epoch_utc"], "object_id": observed["object_id"],
        "station_id": observed["station_id"], "document_uri": observed["document_uri"],
        "document_sha256_verified": digest,
        "extraction_sha256_verified": extraction_digest,
        "extraction_evidence_class": extraction_tier,
        "state_document_sha256_verified": digest_state,
        "state_source_uri": binding["document_uri"],
        "state_source_class": state_record["record_class"], "frame": FRAME,
        "residual_east_north_arcsec": (residual / ARCSEC_RAD).tolist(),
        "combined_covariance_arcsec2": (total / ARCSEC_RAD**2).tolist(),
        "squared_mahalanobis_2d": chi2,
        "uncertainty_contract": "SUPPLIED_INSTRUMENT_ONLY_POSITION_ONLY_STATE_NO_COVARIANCE",
        "prediction_binding": "REPLAYED_FROM_ORIGINAL_TEME_AND_IERS_BYTES",
        "object_binding": "ORIGINAL_TEME_STATE_BYTES_AND_ID_MATCHED_NOT_HISTORICALLY_VERIFIED",
        "comparison_status": "CONDITIONAL_GEOMETRIC_ONLY",
        "extraction_binding": "TYPED_FIELDS_MATCH_SUPPLIED_EXTRACTION_NOT_PRIMARY_AUTHENTICITY",
        "historical_holdout": "NOT_RUN",
        "impact_inference": "NOT_SUPPORTED",
        "missing_historical_requirements": [
            "1963_STATION_SURVEY", "CLOCK_CALIBRATION",
            "FK4_APPARENT_TO_GEOMETRIC_GCRS_IF_APPLICABLE",
            "INDEPENDENT_NORAD_OBJECT_IDENTIFICATION",
            "INSTRUMENT_ERROR_CALIBRATION"
        ],
    }
