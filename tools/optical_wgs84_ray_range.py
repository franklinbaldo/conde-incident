#!/usr/bin/env python3
"""Conditional geometric range exclusion for a WGS84 ray (no 1963 observation).

Given station ITRS coordinates (km) and a *direction* in the same frame,
return the first strictly interior crossing of the reference ellipsoid. An
object farther along this ray is Earth-occulted even if its own endpoint is
outside the Earth. None means the forward half-line never enters the solid
ellipsoid (including a tangent). This is not terrain, atmospheric refraction,
an optical film observation, or a bound on NORAD 528's real trajectory.
"""
from __future__ import annotations

import math

WGS84_RADII_KM = (6378.137, 6378.137, 6356.752314245)


def first_earth_entry_km(station: tuple[float, float, float],
                         direction: tuple[float, float, float],
                         radii: tuple[float, float, float] = WGS84_RADII_KM
                         ) -> float | None:
    """First forward-ray entry, in km of physical line-of-sight distance.

    C + 2Bt + At² is the squared ellipsoid radius minus 1 along the ray.
    For an outside station and inward ray, solve the near quadratic root
    using C/(-B + sqrt(B²-AC)) to avoid cancellation near the horizon.
    A negative discriminant means the half-line cannot penetrate Earth.
    """
    try:
        s, d, axes = tuple(map(float, station)), tuple(map(float, direction)), tuple(map(float, radii))
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError('Invalid WGS84 ray values') from exc
    if len(s) != 3 or len(d) != 3 or len(axes) != 3 or not all(
        math.isfinite(x) for x in (*s, *d, *axes)
    ) or any(x <= 0 for x in axes):
        raise ValueError('Nonfinite, nonpositive or wrongly shaped WGS84 ray')
    length = math.hypot(*d)
    if length == 0:
        raise ValueError('Zero line-of-sight direction')
    u = tuple(x / length for x in d)
    sn = tuple(a / r for a, r in zip(s, axes))
    dn = tuple(a / r for a, r in zip(u, axes))
    c = math.fsum(x * x for x in sn) - 1.0
    if c < -1e-12:
        raise ValueError('Station inside WGS84 reference ellipsoid')
    c = max(0., c)  # Roundoff of a nominal surface location.
    a = math.fsum(x * x for x in dn)
    b = math.fsum(x * y for x, y in zip(sn, dn))
    if b >= 0:
        return None  # Outward/tangential from an outside station.
    disc = b * b - a * c
    if disc <= 0:
        return None  # No strictly interior intersection, tangent allowed.
    return c / (-b + math.sqrt(disc))
