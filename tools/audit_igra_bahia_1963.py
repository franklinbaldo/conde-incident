#!/usr/bin/env python3
"""NOAA IGRA station-file coverage near modern Conde/BA. Not a weather model."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/meteorology/igra_bahia_regional_1963.json'
STATION_LIST_SHA = '9515d29b0c61fcfc912028830c37f47e723ba32c14d88fb48cf6d8bf727060ab'
GEOGRAPHY_SHA = '6559f564071dec2d49e3c55061049190054ea71121cb02e2e6d9cbf8e9bc7c48'
ARCHIVES = {
    'BRM00082900': (7834492, 'df4fcd10e1920723b3cf337b745301b505810ee1dc8a6c5006b84e52b2c871df', 346, {'11': 29}),
    'BRM00082599': (19067487, 'e8ffc9be391d97674b95624eda8d57cd94ddac599404cdea775aa6e95202f7be', 0, {}),
    'BRM00082400': (14035890, '3005549a9eb830202b0f5bb117ccaa23431d3a24f259824c6feb7b7d9d839445', 0, {}),
    'BRM00083746': (25370969, '4caf057ca487167ac68241d7e150a994e79fda7601c784df07db60dceeac6ac8', 72, {'01':17, '02':11, '03':7, '04':9, '06':14, '07':14}),
}
RADIUS_KM = 1500
NOV_DATES = ('1963-11-07', '1963-11-08', '1963-11-09')


def digest(b: bytes) -> str:
    return sha256(b).hexdigest()


def current_bbox_center() -> tuple[float, float]:
    p = ROOT / 'research/geo/conde_ibge_2022_sirgas2000.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    if (d['jurisdiction']['municipality_code_ibge'] != '2908606'
            or d['source']['archive_sha256'] != GEOGRAPHY_SHA
            or d['metadata']['valid_in_november_1963'] != 'NOT_ESTABLISHED'):
        raise ValueError('IBGE 2022 municipal geography lineage changed')
    west, south, east, north = d['metadata']['bbox_lonlat']
    if not (-39 < west < east < -36 and -14 < south < north < -10):
        raise ValueError('unexpected Conde municipal bbox')
    return ((south + north) / 2, (west + east) / 2)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Spherical approximation, not minimum distance to municipal polygon.
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*6371.0*asin(min(1, sqrt(max(0, a))))


def catalogue_rows(data: bytes, *, strict_hash: bool = True) -> list[dict]:
    if strict_hash and digest(data) != STATION_LIST_SHA:
        raise ValueError('NOAA station catalogue SHA mismatch; do not silently update')
    center = current_bbox_center()
    rows = []
    for raw_bytes in data.splitlines():
        if not raw_bytes.startswith(b'BR'):
            continue
        raw = raw_bytes.decode('latin-1')
        sid = raw[:11].strip()
        if len(sid) != 11:
            continue
        lat, lon = float(raw[12:20]), float(raw[21:30])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        km = haversine_km(*center, lat, lon)
        if km > RADIUS_KM:
            continue
        first, last = int(raw[72:76]), int(raw[77:81])
        rows.append({'station_id': sid, 'catalogue_name': raw[41:71].strip(),
                     'catalogue_lat':lat, 'catalogue_lon':lon,
                     'approx_bbox_center_km':round(km,1),
                     'inventory_first_year':first, 'inventory_last_year':last,
                     'year_1963_inside_inventory_bounds':first <= 1963 <= last})
    return sorted(rows, key=lambda r:(r['approx_bbox_center_km'], r['station_id']))


def archive_dates(path: Path, station: str) -> dict:
    if station not in ARCHIVES:
        raise ValueError('unexpected station')
    size, expected_sha, expected_1963, _ = ARCHIVES[station]
    if path.stat().st_size != size:
        raise ValueError('NOAA archive size mismatch: '+station)
    if digest(path.read_bytes()) != expected_sha:
        raise ValueError('NOAA archive SHA mismatch: '+station)
    months, days = Counter(), Counter()
    total = n1963 = 0
    with ZipFile(path) as z:
        if z.namelist() != [f'{station}-data.txt']:
            raise ValueError('unexpected ZIP member: '+station)
        with z.open(z.namelist()[0]) as f:
            for ln in f:
                if not ln.startswith(b'#'):
                    continue
                if ln[1:12].decode('ascii') != station:
                    raise ValueError('NOAA header station mismatch')
                stamp = ln[13:23].decode('ascii')
                parts = stamp.split()
                if len(parts) != 3 or not all(p.isdigit() for p in parts):
                    raise ValueError('malformed NOAA sounding date')
                y, m, d = map(int,parts)
                if not 1900 <= y <= 2100 or not 1 <= m <= 12 or not 1 <= d <= 31:
                    raise ValueError('bad NOAA date components')
                total += 1
                if y == 1963:
                    n1963 += 1
                    months[f'{m:02d}'] += 1
                    if m == 11 and 7 <= d <= 9:
                        days[f'1963-11-{d:02d}'] += 1
    if n1963 != expected_1963:
        raise ValueError('1963 count disagrees with original audit')
    return {'station_id': station, 'snapshot_zip_bytes':size, 'snapshot_zip_sha256':expected_sha,
            'sounding_headers_total':total, 'sounding_headers_1963':n1963,
            'months_1963':dict(sorted(months.items())),
            'dates_nov_07_09_1963':dict(sorted(days.items()))}


def audit(station_list: Path, zip_dir: Path) -> dict:
    rows = catalogue_rows(station_list.read_bytes())
    ids = {r['station_id'] for r in rows if r['year_1963_inside_inventory_bounds']}
    if ids != set(ARCHIVES):
        raise ValueError('year-overlap inventory selection changed: '+repr(ids))
    zips = [archive_dates(zip_dir/f'{sid}-data.txt.zip', sid) for sid in sorted(ARCHIVES)]
    # Only the 2022 bbox midpoint is used. No claim of 1963 position or spatial representativeness.
    return {
        'schema':'conde.igra-bahia-regional-1963/v1', 'capture_date_utc':'2026-11-13',
        'sources':{'station_list_url':'https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt',
            'station_list_sha256':STATION_LIST_SHA,
            'zip_url_template':'https://www.ncei.noaa.gov/pub/data/igra/data/data-por/{station_id}-data.txt.zip',
            'conde_ibge_2022_archive_sha256':GEOGRAPHY_SHA},
        'reference':{'type':'midpoint_of_IBGE_2022_municipality_bbox_not_centroid',
            'lat_lon':list(current_bbox_center()), 'radius_km':RADIUS_KM,
            'distance_method':'haversine_spherical_earth_R6371km',
            'coordinates_valid_for_1963':None,'historical_site_distance_error_km':None},
        'catalogue':{'within_1500_km':len(rows), 'year_1963_in_catalogue_bounds':len(ids),
            'rows':rows},
        'audited_archives':zips,
        'result':{'actual_1963_headers_in_four_nominally_eligible_archives':sum(z['sounding_headers_1963'] for z in zips),
            'archive_ids_with_nov_07_09_headers':sorted(z['station_id'] for z in zips if z['dates_nov_07_09_1963']),
            'independent_conde_wind_observation_1963_11_08':None,
            'spatiotemporal_transfer_uncertainty':None,
            'instrumental_covariance':None,
            'geographic_constraint_activated':False,
            'status':'CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION',
            'links':['C149','C150','C151','PR420']},
    }


def validate_report(rep: dict) -> None:
    if rep['schema'] != 'conde.igra-bahia-regional-1963/v1':
        raise ValueError('schema mismatch')
    if rep['sources']['station_list_sha256'] != STATION_LIST_SHA:
        raise ValueError('unrecognized source digest')
    if rep['reference']['lat_lon'] != list(current_bbox_center()):
        raise ValueError('geography midpoint changed')
    rows = rep['catalogue']['rows']
    if len(rows) != 31 or sum(x['year_1963_inside_inventory_bounds'] for x in rows) != 4:
        raise ValueError('spatial catalogue coverage changed')
    ids = {x['station_id'] for x in rows if x['year_1963_inside_inventory_bounds']}
    if ids != set(ARCHIVES):
        raise ValueError('eligible station IDs changed')
    if sorted(x['station_id'] for x in rep['audited_archives']) != sorted(ARCHIVES):
        raise ValueError('ZIP audit coverage changed')
    for x in rep['audited_archives']:
        sid = x['station_id'];size, sha, num, months = ARCHIVES[sid]
        if x['snapshot_zip_bytes'] != size or x['snapshot_zip_sha256'] != sha or x['sounding_headers_1963'] != num:
            raise ValueError('source provenance changed: '+sid)
        if sid in ('BRM00083746','BRM00082900') and x['months_1963'].get('11',0) != months.get('11',0):
            raise ValueError('Galeao 1963 seasonal gap changed')
        if x['dates_nov_07_09_1963'] and sid != 'BRM00082900':
            raise ValueError('unverified regional observation promoted')
    if (rep['result']['archive_ids_with_nov_07_09_headers'] != ['BRM00082900']
            or rep['result']['geographic_constraint_activated'] is not False
            or rep['result']['independent_conde_wind_observation_1963_11_08'] is not None
            or rep['result']['spatiotemporal_transfer_uncertainty'] is not None
            or rep['result']['instrumental_covariance'] is not None):
        raise ValueError('epistemic promotion without evidence')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--station-list',type=Path)
    p.add_argument('--zip-dir',type=Path)
    p.add_argument('--check',action='store_true')
    a = p.parse_args()
    if (a.station_list is None) != (a.zip_dir is None):
        p.error('station-list and zip-dir must be supplied together')
    old = json.loads(REPORT.read_text(encoding='utf-8')) if REPORT.exists() else None
    if a.station_list is not None:
        result = audit(a.station_list,a.zip_dir)
        validate_report(result)
        if a.check:
            if old != result:
                raise SystemExit('FAIL: pinned complete-source audit changed')
        else:
            REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    elif a.check:
        if old is None:
            raise SystemExit('FAIL: no pinned report')
        validate_report(old)
    else:
        p.error('provide source paths for a new audit, or --check to validate the pinned report')
    print('PASS: 31 catalogue stations; 4 nominally eligible; only Recife has Nov 7–9 headers (not Conde observations)')


if __name__ == '__main__':
    main()
