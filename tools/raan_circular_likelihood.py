#!/usr/bin/env python3
"""Conditional *mathematical* circular likelihood; NOT a calibrated 1963 model.

The offset is one latent b_g per documentary lineage group, with uniform
Haar prior on S^1, analytically integrated out. Conditional errors are
independent von Mises ONLY UNDER AN EXPLICIT, UNVERIFIED ASSUMPTION.
No prior for orbit parameters, no fit, no sampler, no historical posterior.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

TAU = 2.0 * math.pi
LOG_TAU = math.log(TAU)


@dataclass(frozen=True)
class Datum:
    norad: int
    epoch_utc: str
    lineage: str
    observed_raan_deg: float
    predicted_raan_deg: float
    kappa: float
    prediction_ref: str
    calibration_ref: str


def log_i0(x: float) -> float:
    """Stable log modified Bessel I_0(x), x >= 0.

    Positive power series below 50 and fixed-order asymptotic above 50.
    Numerical accuracy is checked against an independent circle integral.
    This is NOT a concentration estimator.
    """
    if isinstance(x, bool) or not isinstance(x, (float, int)):
        raise ValueError("kappa/concentration must be numeric")
    x = float(x)
    if not math.isfinite(x) or x < 0.0:
        raise ValueError("nonfinite or negative concentration")
    if x < 50.0:
        term = 1.0
        total = 1.0
        for k in range(1, 400):
            term *= (x * x / 4.0) / (k * k)
            total += term
            if term <= total * 1e-16:
                return math.log(total)
        raise ArithmeticError("Bessel positive series did not converge")
    # DLMF 10.40.1: I0(x) ~ e^x / sqrt(2 pi x) *
    # sum_k prod_{j=1}^k ((2j-1)^2/(8*j*x)).
    term, total = 1.0, 1.0
    for k in range(1, 31):
        term *= ((2 * k - 1) ** 2) / (8.0 * k * x)
        total += term
        if term <= total * 1e-16:
            break
    return x - 0.5 * math.log(TAU * x) + math.log(total)


def _checked_grouped(rows: Iterable[Datum]) -> dict[str, list[tuple[float, float]]]:
    grouped: dict[str, list[tuple[float, float]]] = {}
    seen: set[tuple[int, str]] = set()
    for r in rows:
        if not isinstance(r, Datum):
            raise ValueError("expected explicit Datum, no implicit historical model")
        if (type(r.norad) is not int or r.norad <= 0 or
                not isinstance(r.epoch_utc, str) or not r.epoch_utc.strip()):
            raise ValueError("missing NORAD or epoch")
        if not isinstance(r.lineage, str) or not r.lineage.strip():
            raise ValueError("missing documentary lineage")
        for ref in (r.prediction_ref, r.calibration_ref):
            if not isinstance(ref, str) or not ref.strip():
                raise ValueError("prediction/calibration provenance required")
        key = (r.norad, r.epoch_utc)
        if key in seen:
            raise ValueError("duplicate NORAD/epoch: replicas cannot become independent data")
        seen.add(key)
        for angle in (r.observed_raan_deg, r.predicted_raan_deg):
            if isinstance(angle, bool) or not isinstance(angle, (float, int)):
                raise ValueError("angles must be numeric")
            if not math.isfinite(angle):
                raise ValueError("nonfinite angle")
        k = r.kappa
        if isinstance(k, bool) or not isinstance(k, (float, int)):
            raise ValueError("kappa requires an explicit numeric calibrated input")
        k = float(k)
        if k < 0 or not math.isfinite(k):
            raise ValueError("nonfinite or negative kappa")
        # Residual is a circle angle; not Euclidean RAAN minus phase.
        d = math.radians(math.remainder(r.observed_raan_deg - r.predicted_raan_deg, 360.0))
        grouped.setdefault(r.lineage, []).append((d, k))
    if not seen:
        raise ValueError("empty observation set")
    return grouped


def marginal_log_density(rows: Iterable[Datum]) -> float:
    """Log density in radians, after integrating one uniform offset per lineage.

    Given residual r_i and concentration k_i:
    log p(y|mu,k,groups) =
        sum_groups [log I0(|sum_i k_i exp(i*r_i)|)
                    -sum_i log I0(k_i) - n_group log(2*pi)].
    This is only a mathematical conditional density for SPECIFIED mu, k, groups.
    In particular it does not assign probabilities to impact sites.
    """
    grouped = _checked_grouped(rows)
    parts: list[float] = []
    for group in grouped.values():
        x = math.fsum(k * math.cos(r) for r, k in group)
        y = math.fsum(k * math.sin(r) for r, k in group)
        radius = math.hypot(x, y)
        parts.append(log_i0(radius) - math.fsum(log_i0(k) for _, k in group)
                     - len(group) * LOG_TAU)
    return math.fsum(parts)


def predictive_log_density(fit: Iterable[Datum], future: Iterable[Datum]) -> float:
    """p(future | fit, FIXED predictions/kappas), with one shared offset per group.

    The lineage offset is updated by the fit observations, not re-estimated
    from the evaluation data. This identity is a conditional marginal ratio.
    This function DOES NOT refit dynamics, concentrations or orbit parameters.
    Caller must enforce frozen fit/validation/evaluation partitions.
    """
    training = tuple(fit)
    validation = tuple(future)
    if not training or not validation:
        raise ValueError("training and future observations must both be nonempty")
    return marginal_log_density(training + validation) - marginal_log_density(training)
