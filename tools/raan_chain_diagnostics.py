#!/usr/bin/env python3
"""Synthetic-ready diagnostics for circular MCMC parameters; NOT historical MCMC.

Rank-normalized split and folded R-hat plus Geyer IPS/IMS bulk/tail ESS
on sin/cos projections. Explicitly handles a circle as S^1, not a line.
These diagnostics cannot validate a prior, likelihood, physics, or provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import NormalDist, median, variance
from typing import Sequence

MIN_CHAINS = 4
MIN_DRAWS = 40
_MAX_DRAWS = 4096  # reference O(n^2) implementation, not a production sampler
_Z = NormalDist()


@dataclass(frozen=True)
class AxisDiagnostic:
    rank_rhat: float
    folded_rhat: float
    bulk_ess: float
    tail_ess: float

    @property
    def rhat(self) -> float:
        return max(self.rank_rhat, self.folded_rhat)


@dataclass(frozen=True)
class CircularDiagnostic:
    draws_per_chain: int
    chain_count: int
    cos: AxisDiagnostic
    sin: AxisDiagnostic

    @property
    def worst_rhat(self) -> float:
        return max(self.cos.rhat, self.sin.rhat)

    @property
    def minimum_bulk_ess(self) -> float:
        return min(self.cos.bulk_ess, self.sin.bulk_ess)

    @property
    def minimum_tail_ess(self) -> float:
        return min(self.cos.tail_ess, self.sin.tail_ess)

    def passes_numerical_gate(self) -> bool:
        """Conventional numerical thresholds only, NOT a historical validation."""
        return (self.worst_rhat < 1.01 and self.minimum_bulk_ess >= 100.0 * self.chain_count
                and self.minimum_tail_ess >= 100.0 * self.chain_count)


def _split(chains: Sequence[Sequence[float]]) -> list[list[float]]:
    half = len(chains[0]) // 2
    return [list(part) for chain in chains for part in
            (chain[:half], chain[-half:])]


def _rank_normalize(chains: list[list[float]]) -> list[list[float]]:
    flat = [x for chain in chains for x in chain]
    order = sorted(range(len(flat)), key=flat.__getitem__)
    ranks = [0.0] * len(flat)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and flat[order[end]] == flat[order[start]]:
            end += 1
        rank = (start + 1 + end) / 2.0  # mean of 1-based tied ranks
        for k in range(start, end):
            ranks[order[k]] = rank
        start = end
    n = len(flat)
    zs = [_Z.inv_cdf((rank - 0.375) / (n - 0.25)) for rank in ranks]
    width = len(chains[0])
    return [zs[i:i+width] for i in range(0, n, width)]


def _within_between(chains: list[list[float]]) -> tuple[float, float, float, list[float]]:
    n = len(chains[0])
    means = [math.fsum(c) / n for c in chains]
    within = math.fsum(variance(c, xbar=mean) for c, mean in zip(chains, means)) / len(chains)
    between = n * variance(means)
    var_plus = (n - 1) * within / n + between / n
    return within, between, var_plus, means


def _rhat(chains: list[list[float]]) -> float:
    w, b, v, _ = _within_between(chains)
    if w == 0.0:
        if b == 0.0:
            raise ValueError("undefined R-hat: all chains have the same constant projection")
        return math.inf  # chains each stuck at different constants
    return math.sqrt(max(0.0, v / w))


def _ess(chains: list[list[float]]) -> float:
    """Split-chain autocorrelations with Geyer initial-positive, monotone pairs.

    Uses biased within-chain autocovariance (1/n) and var_plus across splits;
    positive pair truncation and monotone correction. Diagnostic, not MCMC.
    """
    m, n = len(chains), len(chains[0])
    w, b, v, means = _within_between(chains)
    if v <= 0.0 or not math.isfinite(v):
        raise ValueError("undefined ESS for constant or invalid projected draws")
    centered = [[x - mean for x in c] for c, mean in zip(chains, means)]

    def rho(lag: int) -> float:
        if lag == 0:
            return 1.0
        cov = math.fsum(
            math.fsum(c[i] * c[i + lag] for i in range(n - lag)) / n
            for c in centered
        ) / m
        return 1.0 - (w - cov) / v

    # Paired autocorrelations 0+1, 2+3, ... (Geyer's IPS/IMS).
    last = math.inf
    pairs = []
    for lag in range(0, n - 1, 2):
        value = rho(lag) + rho(lag + 1)
        if value <= 0.0:
            break
        last = min(last, value)
        pairs.append(last)
    tau = max(1.0, -1.0 + 2.0 * math.fsum(pairs))
    return min(float(m * n), m * n / tau)


def _quantile(values: list[float], p: float) -> float:
    values = sorted(values)
    pos = p * (len(values) - 1)
    lo = int(pos)
    part = pos - lo
    return values[lo] * (1.0 - part) + values[min(lo + 1, len(values) - 1)] * part


def _axis(split: list[list[float]]) -> AxisDiagnostic:
    z = _rank_normalize(split)
    raw = [x for chain in split for x in chain]
    center = median(raw)
    folded = _rank_normalize([[abs(x - center) for x in chain] for chain in split])
    low, high = _quantile(raw, 0.05), _quantile(raw, 0.95)
    low_indicators = [[1.0 if x <= low else 0.0 for x in c] for c in split]
    high_indicators = [[1.0 if x >= high else 0.0 for x in c] for c in split]
    return AxisDiagnostic(
        rank_rhat=_rhat(z), folded_rhat=_rhat(folded),
        bulk_ess=_ess(z), tail_ess=min(_ess(low_indicators), _ess(high_indicators))
    )


def diagnose_circular_chains(chains_deg: Sequence[Sequence[float]]) -> CircularDiagnostic:
    """Validate 4+ chains of equal length, then test cos/sin of circle angles.

    Angles are draws from a *user-specified* posterior, not historical inputs.
    No empirical calibration is inferred. Invariance is to modulo 360 only;
    sin/cos projection diagnostics may vary under arbitrary coordinate rotation.
    """
    if not isinstance(chains_deg, (tuple, list)) or len(chains_deg) < MIN_CHAINS:
        raise ValueError("at least four separately initialized chains required")
    if any(not isinstance(c, (tuple, list)) for c in chains_deg):
        raise ValueError("each chain must be an explicit list of draws")
    size = len(chains_deg[0])
    if size < MIN_DRAWS or size > _MAX_DRAWS or any(len(c) != size for c in chains_deg):
        raise ValueError("equal chain lengths 40..4096 required; no padding or fabricated draws")
    values = []
    for chain in chains_deg:
        row = []
        for x in chain:
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
                raise ValueError("nonfinite/non-numeric angular draw")
            row.append(math.radians(math.remainder(float(x), 360.0)))
        values.append(row)
    cos = _axis(_split([[math.cos(x) for x in chain] for chain in values]))
    sin = _axis(_split([[math.sin(x) for x in chain] for chain in values]))
    return CircularDiagnostic(size, len(chains_deg), cos, sin)
