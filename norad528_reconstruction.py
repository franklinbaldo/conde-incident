#!/usr/bin/env python3
"""
NORAD 528 (1963-003B) & O CASO CONDE (1963)
Reconstrucao Orbital Historica, Triangulacao Dinamica e Teste Inverso de Falsificacao
"""

# Modelo exploratorio: retropropagacao de 12 dias nao e previsao de reentrada.
# O dia de decaimento NASA 08/11 nao fornece hora nem local.
import math
import random
from datetime import datetime, timezone, timedelta

EARTH_RADIUS_KM = 6378.137
EARTH_MU = 398600.4418
EARTH_J2 = 0.00108262668
CONDE_LAT = -11.8139
CONDE_LON = -37.6108

EPOCH_528 = datetime(1963, 10, 27, 14, 40, 16, 132512, tzinfo=timezone.utc)
INCLINATION_528_DEG = 81.8615
MEAN_MOTION_528_REV_DAY = 15.74901460
RAAN_528_DEG = 198.5261
ECCENTRICITY_528 = 0.0017147

def haversine_km(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def nodal_precession_rate(n_rev_day, inc_deg, a_km, e):
    n_rad_s = n_rev_day * 2 * math.pi / 86400.0
    p_km = a_km * (1 - e**2)
    factor = -1.5 * n_rad_s * EARTH_J2 * (EARTH_RADIUS_KM / p_km)**2
    rate_rad_s = factor * math.cos(math.radians(inc_deg))
    return math.degrees(rate_rad_s) * 86400.0

def main():
    n_rad_s = MEAN_MOTION_528_REV_DAY * 2 * math.pi / 86400.0
    a_km = (EARTH_MU / (n_rad_s**2))**(1/3)
    period_min = 1440.0 / MEAN_MOTION_528_REV_DAY
    nodal_rate = nodal_precession_rate(MEAN_MOTION_528_REV_DAY, INCLINATION_528_DEG, a_km, ECCENTRICITY_528)

    print("=== NORAD 528 (1963-003B) ORBITAL RECONSTRUCTION ===")
    print(f"Semi-major axis: {a_km:.1f} km (Altitude: {a_km - EARTH_RADIUS_KM:.1f} km)")
    print(f"Period: {period_min:.2f} min | Nodal precession: {nodal_rate:.3f} deg/day")

    inc_rad = math.radians(INCLINATION_528_DEG)
    sin_u = math.sin(math.radians(CONDE_LAT)) / math.sin(inc_rad)
    u_asc = math.asin(sin_u)
    u_desc = math.pi - u_asc
    print(f"Geometric crossing arg latitude: asc={math.degrees(u_asc):.2f} deg, desc={math.degrees(u_desc):.2f} deg")

    start_sim = datetime(1963, 11, 8, 0, 0, 0, tzinfo=timezone.utc)
    print("\nPasses over/near Conde parallel on 08/11/1963:")
    for rev in range(1, 17):
        t_sec = (rev - 1) * (period_min * 60)
        cur_time = start_sim + timedelta(seconds=t_sec)
        dt_days = (cur_time - EPOCH_528).total_seconds() / 86400.0
        alt_km = max(0.0, (a_km - EARTH_RADIUS_KM) - 240 * ((dt_days / 12.0)**3.2))
        earth_rot_deg = (cur_time.hour + cur_time.minute/60.0 + cur_time.second/3600.0) * 15.041
        raan_t = (RAAN_528_DEG + nodal_rate * dt_days) % 360
        lon_asc = ((raan_t + math.degrees(math.atan2(math.cos(inc_rad)*math.sin(u_asc), math.cos(u_asc))) - earth_rot_deg + 540) % 360) - 180
        dist = haversine_km(CONDE_LAT, lon_asc, CONDE_LAT, CONDE_LON)
        print(f"Rev {rev:02d}: {cur_time.strftime('%H:%M')} UTC | Alt: {alt_km:5.1f} km | Distance to Conde: {dist:6.1f} km")

if __name__ == '__main__':
    main()
