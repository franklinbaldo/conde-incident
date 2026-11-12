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


@dataclass(frozen=True)
class OffsetAnchor:
    """Hypothetical von Mises prior for lineage offset, not a measurement.

    Source and independence basis are caller attestations, not verification.
    A zero concentration is Haar-uniform regardless of its nominal mean.
    """
    lineage: str
    mean_deg: float
    concentration: float
    source_ref: str
    independence_basis: str


def _checked_anchors(
    lineages: set[str], anchors: Iterable[OffsetAnchor],
) -> dict[str, OffsetAnchor]:
    found: dict[str, OffsetAnchor] = {}
    for a in anchors:
        if not isinstance(a, OffsetAnchor):
            raise ValueError("explicit OffsetAnchor required")
        if not isinstance(a.lineage, str) or not a.lineage.strip():
            raise ValueError("anchor lineage required")
        if a.lineage in found:
            raise ValueError("multiple anchors for one lineage would double-count a prior")
        for ref in (a.source_ref, a.independence_basis):
            if not isinstance(ref, str) or not ref.strip():
                raise ValueError("anchor provenance and independence basis required")
        for value in (a.mean_deg, a.concentration):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("anchor angle and concentration must be numeric")
            if not math.isfinite(value):
                raise ValueError("nonfinite anchor angle or concentration")
        if a.concentration < 0:
            raise ValueError("negative anchor concentration")
        found[a.lineage] = a
    if set(found) != lineages:
        raise ValueError("exactly one explicitly documented anchor per observed lineage")
    return found


def anchored_marginal_log_density(
    rows: Iterable[Datum], anchors: Iterable[OffsetAnchor],
) -> float:
    """Conditional circular likelihood integrated over an anchored lineage offset.

    p(b_g) = VM(b_g | m_g, lambda_g) and p(r_i|b_g) = VM(r_i|b_g, k_i).
    Integrating b gives per lineage
    log I0(|lambda exp(i*m) + sum_i k_i exp(i*r_i)|)
      -log I0(lambda)-sum_i log I0(k_i)-n_g log(2*pi).

    lambda=0 recovers the Haar model. A hypothetical prior can break gauge
    symmetry in the model, but is NOT historical phase identification.
    """
    groups = _checked_grouped(rows)
    by_lineage = _checked_anchors(set(groups), anchors)
    contributions = []
    for lineage, group in groups.items():
        a = by_lineage[lineage]
        m = math.radians(math.remainder(a.mean_deg, 360.0))
        k0 = float(a.concentration)
        try:
            real = math.fsum([k0 * math.cos(m)] +
                            [k * math.cos(r) for r, k in group])
            imag = math.fsum([k0 * math.sin(m)] +
                            [k * math.sin(r) for r, k in group])
            radius = math.hypot(real, imag)
        except OverflowError as exc:
            raise ValueError("anchor resultant outside representable range") from exc
        if not math.isfinite(radius):
            raise ValueError("anchor resultant outside representable range")
        contributions.append(log_i0(radius) - log_i0(k0)
                             - math.fsum(log_i0(k) for _, k in group)
                             - len(group) * LOG_TAU)
    return math.fsum(contributions)


def anchored_predictive_log_density(
    fit: Iterable[Datum], future: Iterable[Datum],
    anchors: Iterable[OffsetAnchor],
) -> float:
    """Predictive log density with frozen H, concentrations and offset anchors.

    The prior is applied once to each shared offset; no refit or MCMC.
    """
    training, held_out, prior = tuple(fit), tuple(future), tuple(anchors)
    if not training or not held_out:
        raise ValueError("both chronological partitions required")
    full = anchored_marginal_log_density(training + held_out, prior)
    used = {d.lineage for d in training}
    fit_prior = tuple(a for a in prior if a.lineage in used)
    base = anchored_marginal_log_density(training, fit_prior)
    return full - base
