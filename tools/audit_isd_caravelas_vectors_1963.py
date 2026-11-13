#!/usr/bin/env python3
"""Source-station surface wind vectors derived from pinned NOAA ISD rows; no transfer to Conde."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from audit_isd_caravelas_1963 import load_snapshot, parse, WINDOW_SHA256, SOURCE_SHA256

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/meteorology/isd_caravelas_vectors_1963.json'
GRAPH = ROOT / 'research/constraints/isd_caravelas_vector_edges_1963.json'


def to_uv(speed: float, direction_from_deg: int) -> tuple[float, float]:
    """ISD wind direction is meteorological FROM, u eastward and v northward."""
    return (-speed * math.sin(math.radians(direction_from_deg)),
            -speed * math.cos(math.radians(direction_from_deg)))


def calc(raw: bytes) -> dict:
    baseline = parse(raw)  # validates station, all timestamps, QC, and units
    grouped: dict[str, list[tuple[float, float, float]]] = {}
    calms: dict[str, int] = {}
    for row in raw.splitlines():
        date = row[15:23].decode('ascii')
        speed = int(row[65:69]) / 10
        direction = int(row[60:63])
        if direction > 360 or direction < 0:
            raise ValueError('wind bearing outside archive convention')
        u, v = to_uv(speed, direction)
        grouped.setdefault(date, []).append((speed, u, v))
        if speed == 0:
            calms[date] = calms.get(date, 0) + 1
    days = {}
    for date, rows in sorted(grouped.items()):
        scalar = statistics.mean(s for s, _, _ in rows)
        u = statistics.mean(x for _, x, _ in rows)
        v = statistics.mean(y for _, _, y in rows)
        mag = math.hypot(u, v)
        bearing = (math.degrees(math.atan2(-u, -v)) % 360) if mag > 1e-12 else None
        key = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
        if round(scalar, 3) != baseline['daily'][key]['surface']['wind_speed_m_s']['mean']:
            raise ValueError('scalar wind mean differs from original pinned diagnostics')
        days[key] = {
            'rows': len(rows), 'calm_rows': calms.get(date, 0),
            'scalar_speed_mean_m_s': round(scalar, 3),
            'mean_eastward_u_m_s': round(u, 3),
            'mean_northward_v_m_s': round(v, 3),
            'mean_vector_magnitude_m_s': round(mag, 3),
            'mean_vector_from_deg': round(bearing, 1) if bearing is not None else None,
            'vector_resultant_fraction_of_scalar_speed': round(mag/scalar, 3) if scalar > 0 else None,
        }
    return {
        'schema': 'conde.isd-caravelas-surface-wind-vectors/v1',
        'input': {'station': '834970-99999', 'archive_gz_sha256': SOURCE_SHA256,
                  'window_sha256': WINDOW_SHA256, 'nominal_dates_utc': list(days),
                  'same_instrument_family_for_all_hours': True},
        'convention': {'wind_direction': 'meteorological FROM',
                       'u_eastward': '-speed*sin(direction)',
                       'v_northward': '-speed*cos(direction)',
                       'zero_wind_bearing_not_physical': True,
                       'speed_weighted_resultant_is_not_instrument_uncertainty': True},
        'days': days,
        'interpretation': {'classification': 'DERIVED_VECTORS_SAME_ARCHIVED_SURFACE_STATION',
                           'status': 'CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION',
                           'uncertainty_of_hourly_u_v': None,
                           'transfer_to_conde_calibrated': False,
                           'numeric_constraint_on_conde_or_trajectory': None,
                           'notice': 'mean vector is a diagnostic at Caravelas, not a drift path or Conde observation'},
    }


def check() -> dict:
    raw = load_snapshot()
    if hashlib.sha256(raw).hexdigest() != WINDOW_SHA256:
        raise ValueError('original NOAA window hash mismatch')
    report = calc(raw)
    if json.loads(REPORT.read_text()) != report:
        raise ValueError('published Caravelas vector report mismatch')
    graph = json.loads(GRAPH.read_text())
    if (graph['status'] != report['interpretation']['status'] or
        graph['active_conde_constraint'] is not None or
        graph['instrument_sigma_m_s'] is not None or
        graph['geographic_transfer_function'] is not None):
        raise ValueError('derived wind vectors improperly promoted to calibrated Conde evidence')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    print(json.dumps(check() if a.check else calc(load_snapshot()), indent=2, ensure_ascii=False))
