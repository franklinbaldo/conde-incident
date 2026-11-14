#!/usr/bin/env python3
"""G53: conditional 1963 TEME -> station-topocentric GCRS optical geometry.

A station supplied as WGS84 geodetic coordinates is a SCENARIO, not a
historically surveyed SAO site. Angles are instantaneous, geometric GCRS,
NOT historical FK4/B1950 film measurements or apparent observed angles.
IERS original bytes are required; no original 527/528/529 observation exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from collections.abc import Mapping

import erfa
import numpy as np

from iers_1963_frame import EOP, TIME
from iers_1963_intraday import checked_source
from iers_1963_teme import matrices_at, transform_covariance, _validated_vector

ROOT = Path(__file__).resolve().parents[1]


def station_itrs_km(lon_deg: float, lat_deg: float, height_m: float) -> np.ndarray:
    """WGS84 station scenario, degrees east/north and ellipsoidal metres."""
    try:
        lon, lat, height = (float(lon_deg), float(lat_deg), float(height_m))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Invalid geodetic station coordinates") from exc
    if not all(map(math.isfinite, (lon, lat, height))) or not (
        -180 <= lon < 180 and -90 <= lat <= 90 and -1000 <= height <= 10000
    ):
        raise ValueError("Invalid WGS84 station longitude/latitude/height")
    # SOFA ellipsoid id 1 = WGS84, output metres in terrestrial Cartesian.
    return np.asarray(erfa.gd2gc(1, math.radians(lon),
                                 math.radians(lat), height)) / 1000.


def forward_optical(source: bytes, eop: dict, times: dict, utc: str,
                    teme_position_km: object, station_lon_deg: float,
                    station_lat_deg: float, station_height_m: float,
                    teme_covariance6d: object | None = None) -> dict:
    """Calculate geometric GCRS RA/Dec and optional tangent-plane covariance.

    No station geodetic datum provenance, source film, clock, atmospheric
    refraction, finite-light-time, FK4 conversion or calibrated error is inferred.
    The covariance describes only specified TEME state uncertainty (r,v).
    """
    checked_source(source, eop, times)
    r_teme = _validated_vector(teme_position_km, "TEME position (km)")
    station_itrs = station_itrs_km(station_lon_deg, station_lat_deg,
                                   station_height_m)
    m = matrices_at(utc, eop, times)
    station_gcrs = m["gcrs_to_itrs"].T @ station_itrs
    r_gcrs = m["teme_to_gcrs"] @ r_teme
    los = r_gcrs - station_gcrs
    rho = float(np.linalg.norm(los))
    if not math.isfinite(rho) or rho < 1e-6:
        raise ValueError("Degenerate topocentric line of sight")
    u = los / rho
    if math.hypot(float(u[0]), float(u[1])) <= 1e-12:
        raise ValueError("RA undefined at celestial pole")
    alpha = math.atan2(float(u[1]), float(u[0])) % (2 * math.pi)
    delta = math.atan2(float(u[2]), math.hypot(float(u[0]), float(u[1])))
    # East and north are orthonormal tangent directions on the celestial sphere.
    east = np.array([-math.sin(alpha), math.cos(alpha), 0.])
    north = np.array([-math.sin(delta) * math.cos(alpha),
                      -math.sin(delta) * math.sin(alpha), math.cos(delta)])
    # Differential angles here are physical east/north GREAT-CIRCLE offsets,
    # not raw dRA (which has a cos(dec) singularity).
    h = np.zeros((2, 6), dtype=float)
    h[0, :3] = east @ m["teme_to_gcrs"] / rho
    h[1, :3] = north @ m["teme_to_gcrs"] / rho
    cov2 = None
    if teme_covariance6d is not None:
        # Shared G52 validator, including entrywise symmetry and scaled PSD.
        c = np.asarray(transform_covariance(teme_covariance6d, np.eye(6)),
                       dtype=float)
        cov2 = ((h @ c @ h.T) + (h @ c @ h.T).T) / 2
        if not np.isfinite(cov2).all():
            raise ValueError("Nonfinite angular covariance")
    itrs_los = m["gcrs_to_itrs"] @ los
    lon = math.radians(float(station_lon_deg))
    lat = math.radians(float(station_lat_deg))
    zenith = np.array([math.cos(lat) * math.cos(lon),
                       math.cos(lat) * math.sin(lon), math.sin(lat)])
    elevation = math.degrees(math.asin(float(np.clip(
        np.dot(itrs_los / rho, zenith), -1., 1.))))
    return {
        "epoch_utc": utc, "input_frame": "TEME", "output_frame": "GCRS",
        "station_coordinate_contract": "WGS84_GEODETIC_SCENARIO_NOT_1963_SURVEY",
        "station_wgs84_geodetic": {"longitude_deg": float(station_lon_deg),
                                  "latitude_deg": float(station_lat_deg),
                                  "height_m": float(station_height_m)},
        "earth_orientation": "IERS_RETROSPECTIVE_SOURCE_BYTES_AUTHENTICATED",
        "range_km": rho, "right_ascension_deg": math.degrees(alpha),
        "declination_deg": math.degrees(delta), "elevation_deg": elevation,
        "unit_line_of_sight_gcrs": u.tolist(),
        "angular_jacobian_east_north_rad_per_km_and_km_s": h.tolist(),
        "state_only_angular_covariance_rad2": None if cov2 is None else cov2.tolist(),
        "angle_type": "INSTANTANEOUS_GEOMETRIC_NOT_APPARENT_FK4",
        "model_omissions": ["LIGHT_TIME", "ABERRATION", "REFRACTION",
                            "FK4_B1950", "STATION_SURVEY_1963", "CLOCK_CALIBRATION"],
        "historical_527_528_529_observation": None,
        "historical_holdout": "NOT_RUN", "impact_inference": "NOT_SUPPORTED",
    }



STATE_SCHEMA = "TEME_POSITION_ONLY_V1"
STATE_CLASSES = {"SYNTHETIC_SCENARIO", "SECONDARY_DERIVATIVE_NOT_INSTRUMENT"}


def decode_source_bound_state(raw_bytes: bytes) -> dict:
    """Parse source bytes with duplicate-key rejection; never infer provenance.

    This narrowly defined JSON interchange is a *scenario input*, not a
    historical catalogue or proof that the labelled object was observed.
    """
    if not isinstance(raw_bytes, bytes) or not raw_bytes:
        raise ValueError("Original TEME state source bytes required")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate TEME state source key")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("Nonfinite TEME state source constant")

    try:
        record = json.loads(raw_bytes.decode("utf-8"),
                            object_pairs_hook=unique_pairs,
                            parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("TEME state source must be UTF-8 JSON") from exc
    if not isinstance(record, Mapping) or set(record) != {
        "schema", "object_id", "epoch_utc", "frame", "teme_position_km", "record_class"
    }:
        raise ValueError("Unrecognized TEME state source schema")
    if record["schema"] != STATE_SCHEMA or record["frame"] != "TEME":
        raise ValueError("TEME state source frame/schema mismatch")
    if not isinstance(record["object_id"], str) or not record["object_id"].strip():
        raise ValueError("TEME state source object identity required")
    if not isinstance(record["epoch_utc"], str) or not record["epoch_utc"].endswith("Z"):
        raise ValueError("TEME state source UTC epoch required")
    if not isinstance(record["record_class"], str) or record["record_class"] not in STATE_CLASSES:
        raise ValueError("Unsupported TEME state source evidence class")
    raw_position = record["teme_position_km"]
    if not isinstance(raw_position, list) or len(raw_position) != 3 or any(
        isinstance(x, (bool, str)) or not isinstance(x, (int, float)) for x in raw_position
    ):
        raise ValueError("TEME state source position must be three numeric km values")
    position = _validated_vector(raw_position, "TEME state source position (km)")
    return {**record, "teme_position_km": position.tolist()}


def forward_source_bound_optical(source: bytes, eop: dict, times: dict,
                                 utc: str, state_document_bytes: bytes,
                                 state_document_uri: str, station_lon_deg: float,
                                 station_lat_deg: float, station_height_m: float) -> dict:
    """Bind a G53 scenario prediction to original state JSON bytes and ID."""
    if not isinstance(state_document_uri, str) or not state_document_uri.strip():
        raise ValueError("TEME state source URI required")
    state = decode_source_bound_state(state_document_bytes)
    if state["epoch_utc"] != utc:
        raise ValueError("TEME state source UTC does not match prediction epoch")
    result = forward_optical(source, eop, times, utc,
                             state["teme_position_km"], station_lon_deg,
                             station_lat_deg, station_height_m)
    result["input_teme_position_km"] = state["teme_position_km"]
    result["state_source_binding"] = {
        "schema": STATE_SCHEMA,
        "document_uri": state_document_uri,
        "document_sha256": hashlib.sha256(state_document_bytes).hexdigest(),
        "object_id": state["object_id"],
        "record_class": state["record_class"],
    }
    return result

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True,
                   help="Authenticated complete original IERS 1963 file")
    p.add_argument("--utc", default="1963-11-08T12:00:00Z")
    p.add_argument("--station-lon", type=float, required=True)
    p.add_argument("--station-lat", type=float, required=True)
    p.add_argument("--station-height-m", type=float, required=True)
    p.add_argument("--teme-position-km", type=float, nargs=3, required=True)
    args = p.parse_args()
    eop, times = json.loads((ROOT / EOP).read_text()), json.loads((ROOT / TIME).read_text())
    print(json.dumps(forward_optical(args.source.read_bytes(), eop, times,
                                    args.utc, args.teme_position_km,
                                    args.station_lon, args.station_lat,
                                    args.station_height_m), indent=2))


if __name__ == "__main__":
    main()
