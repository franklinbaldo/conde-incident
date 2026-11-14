#!/usr/bin/env python3
"""Conditional orbital-plane geometry for NORAD 528/637, not an impact predictor.

Historical catalogue rows are a SHA-pinned *secondary* TLE mirror; no original
sensor measurements, physical phase, observed terminal instant, or site of fall.
UT1 is approximated by source UTC and SIRGAS2000 by WGS84 solely for this
sensitivity scenario; no precision claim follows.
"""
from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import random
import sys

from c241_637_regime_holdout import (
    EARTH_J2, EARTH_RADIUS_KM, MU_KM3_S2,
    SOURCE_SHA256, SOURCE_URL, extract_pinned,
)

UTC = timezone.utc
DAY = 86400
START = datetime(1963, 11, 6, tzinfo=UTC)
END = datetime(1963, 11, 10, tzinfo=UTC)
SIGMA_RMSE_DEG = {528: 0.039199, 637: 0.054968}  # same-lineage holdouts, NOT sensor sigma
NASA_DAY = {528: 8, 637: 7}
DISTANCES_KM = (50, 100, 200)
SCALES = (1, 3, 10)
DRAW_COUNT = 256
CAMERA_FILE = 'research/geo/cgeo15_vila_matriz_2022_camera_points.json'
GEO_FILE = 'research/geo/conde_ibge_2022_sirgas2000.json'
CENTRO_VILA_FILE = 'research/geo/cgeo20_centro_vila_2020.json'


def signed_normal_projection(latitude: float, theta: float, raan: float, inc: float) -> float:
    """Unit Earth-fixed point dotted with the inertial orbit-plane normal."""
    if not all(math.isfinite(x) for x in (latitude, theta, raan, inc)):
        raise ValueError('nonfinite geometry')
    if abs(latitude) > math.pi / 2 or not 0 <= inc <= math.pi:
        raise ValueError('invalid latitude/inclination')
    return (math.sin(inc) * math.cos(latitude) * math.sin(raan - theta)
            + math.cos(inc) * math.sin(latitude))


def gmst_radians(epoch: datetime) -> float:
    if epoch.tzinfo is None or epoch.utcoffset() != timedelta(0):
        raise ValueError('epoch must be UTC')
    jd = 2440587.5 + epoch.timestamp() / DAY
    t = (jd - 2451545.0) / 36525.0
    degrees = (280.46061837 + 360.98564736629 * (jd - 2451545.0)
               + 0.000387933 * t*t - t*t*t/38710000.0)
    return math.radians(degrees % 360)


def surface_radius(latitude: float) -> float:
    a = EARTH_RADIUS_KM
    b = 6356.752314245
    x, y = math.cos(latitude), math.sin(latitude)
    return math.hypot(a*a*x, b*b*y) / math.hypot(a*x, b*y)


def dadt_last_secant(rows: list[dict]) -> float:
    a, b = rows[-2:]
    days = (b['epoch'] - a['epoch']).total_seconds()/DAY
    if days <= 0 or b['mean_motion'] <= 0 or a['mean_motion'] <= 0:
        raise ValueError('bad secant')
    n = b['mean_motion'] * math.tau / DAY
    axis = (MU_KM3_S2 / (n*n))**(1/3)
    dn = (b['mean_motion'] - a['mean_motion']) / days
    slope = -2*axis*dn/(3*b['mean_motion'])
    if not math.isfinite(slope) or slope >= 0:
        raise ValueError('last two rows do not support a decaying-a branch')
    return slope


def raan_at(origin: dict, when: datetime, dadt: float) -> float:
    """Integrate secular J2 nodal precession with fixed e/i and linear a(t)."""
    delta = (when - origin['epoch']).total_seconds()/DAY
    n0 = origin['mean_motion'] * math.tau / DAY
    a0 = (MU_KM3_S2/(n0*n0))**(1/3)
    ecc, inc = origin['eccentricity'], math.radians(origin['inclination'])
    def rate(day: float) -> float:
        a = a0 + dadt*day
        if a <= EARTH_RADIUS_KM or not math.isfinite(a):
            raise ValueError('invalid a(t), cannot extend this scenario')
        n = math.sqrt(MU_KM3_S2/a**3)
        return (-1.5*EARTH_J2*n*(EARTH_RADIUS_KM/(a*(1-ecc*ecc)))**2
                * math.cos(inc)*DAY)
    # Simpson integration with two panels per day, at least 2.
    count = max(2, 2 * math.ceil(abs(delta)))
    h = delta/count
    accum = rate(0) + rate(delta)
    for j in range(1,count):
        accum += (4 if j % 2 else 2) * rate(j*h)
    return (math.radians(origin['raan']) + h*accum/3) % math.tau


def cross_km(when: datetime, origin: dict, dadt: float,
             lat_deg: float, lon_deg: float, raan_offset_deg: float = 0) -> float:
    phi = math.radians(lat_deg)
    theta = gmst_radians(when) + math.radians(lon_deg)
    o = raan_at(origin, when, dadt) + math.radians(raan_offset_deg)
    i = math.radians(origin['inclination'])
    return surface_radius(phi) * signed_normal_projection(phi,theta,o,i)


def bisect(fn, left: datetime, right: datetime, target_sign: bool | None = None) -> datetime:
    fa = fn(left)
    fb = fn(right)
    if not (math.isfinite(fa) and math.isfinite(fb)) or fa * fb > 0:
        raise ValueError('root not bracketed')
    while (right-left).total_seconds() > 0.1:
        mid = left + (right-left)/2
        fm = fn(mid)
        if fa*fm <= 0:
            right, fb = mid, fm
        else:
            left, fa = mid, fm
    return left + (right-left)/2


def roots_for_day(fn, start: datetime) -> list[datetime]:
    end = start + timedelta(days=1)
    step = timedelta(minutes=5)
    out = []
    left = start
    while left < end:
        right = min(left+step,end)
        fa, fb = fn(left), fn(right)
        if fa == 0:
            root = left
        elif fa*fb < 0 or fb == 0:
            root = bisect(fn,left,right)
        else:
            root = None
        if root is not None and (not out or abs((root-out[-1]).total_seconds()) > 1):
            out.append(root)
        left = right
    return out


def interval_for_root(fn, root: datetime, distance: int) -> tuple[datetime, datetime]:
    def margin(t):
        return abs(fn(t))-distance
    limits = []
    for direction in (-1,1):
        near = root
        for _ in range(180):  # a 3-hour search bound
            far = near + timedelta(minutes=direction)
            if margin(far) >= 0:
                left, right = (far,near) if direction < 0 else (near,far)
                limits.append(bisect(margin,left,right))
                break
            near = far
        else:
            raise ValueError('threshold width exceeded 3h')
    return limits[0], limits[1]


def iso(t: datetime) -> str:
    return t.isoformat(timespec='seconds').replace('+00:00','Z')


def local(t: datetime) -> str:
    return (t - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')


def cutoff_for(norad: int, interpretation: str) -> datetime:
    """NASA day label is NOT a verified time zone."""
    utc_midnight = datetime(1963, 11, NASA_DAY[norad]+1, tzinfo=UTC)
    return utc_midnight + (timedelta(hours=3) if interpretation=='BAHIA_CIVIL_DAY' else timedelta())


def append_window(fn, root, norad):
    item={'crossing_utc':iso(root),'crossing_bahia_utc_minus_3':local(root),
          'thresholds':{}}
    for distance in DISTANCES_KM:
        begin,end = interval_for_root(fn,root,distance)
        clips = {}
        for reading in ('UTC_CIVIL_DAY','BAHIA_CIVIL_DAY'):
            cutoff = cutoff_for(norad,reading)
            clips[reading] = ([iso(begin), iso(min(end,cutoff))]
                              if begin < cutoff else None)
        item['thresholds'][str(distance)] = {
            'start_utc':iso(begin),'end_utc':iso(end),
            'width_minutes':round((end-begin).total_seconds()/60,3),
            'ends_after_NASA_day_reading':clips,
        }
    return item


def source_point(repo: Path):
    data=json.loads((repo/CAMERA_FILE).read_text(encoding='utf-8'))
    geo=json.loads((repo/GEO_FILE).read_text(encoding='utf-8'))
    localities=json.loads((repo/CENTRO_VILA_FILE).read_text(encoding='utf-8'))
    if geo['jurisdiction']['municipality_code_ibge']!='2908606':
        raise ValueError('wrong municipality')
    if {x['id'] for x in localities['named_localities']}!={'CENTRO20','VILA20'}:
        raise ValueError('expected independent locality branches')
    if any(x['point'] is not None for x in localities['named_localities']):
        raise ValueError('this scenario assumes centro/vila historical points absent')
    photo=data['captured_images'][0]
    gps=photo['camera_point_from_commons']
    if gps['srs_usable_for_1963'] is not False or gps['coordinate_role']!='point_of_view':
        raise ValueError('camera provenance has changed')
    return gps['latitude'],gps['longitude'],photo['id'],photo['sha256']


def report_one(rows, norad, branch, latitude, longitude):
    origin=rows[-1]
    drift=dadt_last_secant(rows) if branch=='DECAYING_A_LAST_SECANT' else 0.0
    if not origin['epoch'] < START:
        raise ValueError('must forecast from pre-window epoch')
    fn=lambda t: cross_km(t, origin,drift,latitude,longitude)
    windows=[]
    day=START
    while day < END:
        windows.extend(append_window(fn,r,norad) for r in roots_for_day(fn,day))
        day+=timedelta(days=1)
    return {'norad':norad,'branch':branch,'origin_source_row':origin['source_row'],
            'origin_utc':iso(origin['epoch']),'inclination_deg':origin['inclination'],
            'raan_deg':origin['raan'],'mean_motion_rev_day':origin['mean_motion'],
            'e':origin['eccentricity'],'da_dt_km_day':round(drift,6),
            'cutoffs_utc':{k:iso(cutoff_for(norad,k)) for k in ('UTC_CIVIL_DAY','BAHIA_CIVIL_DAY')},
            'crossings':windows}


def sensitivity_one_day(fn, start: datetime, norad: int, deviations: list[float]):
    """Count perturbed-RAAN successes, not calibrated probabilities."""
    matrix=[]
    utc_cutoff = cutoff_for(norad,'UTC_CIVIL_DAY')
    local_cutoff = cutoff_for(norad,'BAHIA_CIVIL_DAY')
    for minute in range(0,1440,3):
        now=start+timedelta(minutes=minute)
        if now >= local_cutoff:
            break  # never propagate after either possible last civil-day ending
        # Precalculate all rotations once per grid point, not in each draw.
        theta=gmst_radians(now)
        lon,lat=fn['lon'],fn['lat']
        phi=math.radians(lat)
        o=raan_at(fn['origin'],now,fn['dadt'])
        inc=math.radians(fn['origin']['inclination'])
        radial=surface_radius(phi)
        # Count order: distance=50/100/200, within each scale=1/3/10.
        counts=[]
        for d in DISTANCES_KM:
            for scale in SCALES:
                hits=0
                for z in deviations:
                    v=radial*signed_normal_projection(
                        phi, theta+math.radians(lon),
                        o+math.radians(SIGMA_RMSE_DEG[norad]*scale*z),inc)
                    hits+=abs(v)<=d
                counts.append(hits)
        matrix.append([minute,*counts])
    valid_utc_rows=sum(start+timedelta(minutes=row[0]) < utc_cutoff for row in matrix)
    return {'grid_date_utc':start.date().isoformat(), 'minutes_step':3,
            'UTC_CIVIL_DAY_valid_rows':valid_utc_rows,
            'BAHIA_CIVIL_DAY_valid_rows':len(matrix),
            'thresholds_km':list(DISTANCES_KM), 'raan_rmse_scale_factors':list(SCALES),
            'draws':DRAW_COUNT,'values':'INTEGER_HITS_DIVIDE_BY_DRAWS_NOT_POSTERIOR',
            'matrix_minute_of_day_then_dist50_scales123_dist100_scales123_dist200_scales123':matrix,
            'clipping':'only first UTC_CIVIL_DAY_valid_rows are usable under UTC-day reading; rest valid only for local-day reading'}


def all_results(parquet: Path, repo: Path):
    latitude,longitude,photo_id,photo_sha=source_point(repo)
    rows=extract_pinned(parquet)
    for norad in (528,637):
        if rows[norad][-1]['epoch'] >= START:
            raise ValueError('unexpected late origin')
    rand=random.Random(528637)
    draws=[rand.gauss(0,1) for _ in range(DRAW_COUNT)]
    meta={'schema':'conde.c241-conditional-plane-windows/v1',
          'source':{'secondary_parquet_url':SOURCE_URL,'secondary_parquet_sha256':SOURCE_SHA256,
                    'source_json_sha256':{key:hashlib.sha256((repo/key).read_bytes()).hexdigest()
                                          for key in (GEO_FILE,CENTRO_VILA_FILE,CAMERA_FILE)},
                    'geo_ibge_2022_file':GEO_FILE,'localities_cgeo20_file':CENTRO_VILA_FILE,
                    'modern_camera_file':CAMERA_FILE,'camera_image_sha256':photo_sha,
                    'camera_id':photo_id,'coordinate_lat_lon_deg':[latitude,longitude]},
          'reference_point_class':'MODERN_2022_CAMERA_POINT_NOT_1963_CENTER_OR_FALL',
          'centro20':{'status':'NOT_EVALUATED_NO_CUSTODIED_POINT'},
          'vila20':{'status':'MODERN_CAMERA_PROXY_ONLY_NO_HISTORICAL_GEOCODING'},
          'phase_constraint':'NOT_EVALUATED','posterior':False,'active_constraint':False,
          'reentry_time_identified':False,'impact_probability':None,
          'sensitivity_scale':'RAAN holdout RMSE, SAME SECONDARY LINEAGE, NOT INSTRUMENTAL SIGMA',
          'ut1_1963':'UTC_PROXY_UNCALIBRATED','earth_shape':'WGS84_PROXY_FOR_SIRGAS2000',
          'gmst':'IAU_APPROX_1982_UTC_AS_UT1','date_range_utc':['1963-11-06','1963-11-09'],
          'document_branch_2330_Fbis':{
              'if_2330_is_GMT_broadcast_bahia_20_30':'CONDITIONAL_ONLY',
              'broadcast_time_is_observed_event_time':False,
              'alternative_time_interpretations_retained':True},
          'geometry':'absolute geocentric normal dot surface position; phase and drag survival not modeled',
          'curve_semantics':'simulated fraction under synthetic RAAN variation; do not interpret as P(impact | t)'}
    out={}
    for norad in (528,637):
        for branch in ('CONSTANT_A','DECAYING_A_LAST_SECANT'):
            key=f'{norad}_{branch.lower()}'
            out[key]=report_one(rows[norad],norad,branch,latitude,longitude)
            dadt=out[key]['da_dt_km_day']
            cfg={'lat':latitude,'lon':longitude,'origin':rows[norad][-1],'dadt':dadt}
            curves={}
            for day in range(6,10):
                dt=datetime(1963,11,day,tzinfo=UTC)
                curves[str(day)]=sensitivity_one_day(cfg,dt,norad,draws)
            out[key]['curves']=curves
    return meta,out


def payloads(parquet: Path, repo: Path) -> dict[str, bytes]:
    meta,results=all_results(parquet,repo)
    outputs={'c241_plane_index.json':meta}
    for key,report in results.items():
        curves=report.pop('curves')
        outputs[f'c241_plane_{key}.json']=report
        for date,curve in curves.items():
            outputs[f'c241_plane_curve_{key}_nov{date}.json']=curve
    return {k:(json.dumps(v,ensure_ascii=False,separators=(',',':'),sort_keys=True)+'\n').encode()
            for k,v in outputs.items()}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parquet',required=True,type=Path)
    p.add_argument('--repo',default=Path(__file__).resolve().parents[1],type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    files=payloads(a.parquet,a.repo)
    if any(len(data)>20000 for data in files.values()):
        raise SystemExit('generated file exceeds 20KB')
    if a.check:
        for name,data in files.items():
            if not (a.output_dir/name).is_file() or (a.output_dir/name).read_bytes()!=data:
                raise SystemExit('replay drift: '+name)
    else:
        a.output_dir.mkdir(parents=True,exist_ok=True)
        for name,data in files.items():
            (a.output_dir/name).write_bytes(data)
    print('C241 orbital-plane conditional geometry: {} files; no historic location inference'.format(len(files)))


if __name__=='__main__':
    main()
