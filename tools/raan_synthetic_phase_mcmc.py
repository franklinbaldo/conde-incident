#!/usr/bin/env python3
"""REFERENCE synthetic circular Metropolis-Hastings, NOT an orbital posterior.

A single free RAAN phase theta is added to FROZEN H_i predictions, while one
documentary-lineage offset per group is integrated analytically using the
existing von Mises likelihood. No physical orbit is propagated here.

All input provenance markers must be explicitly synthetic. No historical
observations, empirical concentrations, or reentry-site distributions are read.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Sequence

from raan_circular_likelihood import (
    Datum, OffsetAnchor, anchored_marginal_log_density,
)
from raan_chain_diagnostics import diagnose_circular_chains, CircularDiagnostic


def _angle_deg(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(name + " must be numeric")
    if not math.isfinite(value):
        raise ValueError(name + " must be finite")
    return float(value) % 360.0


def _kappa(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(name + " must be numeric")
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(name + " must be finite and nonnegative")
    return float(value)


def _synthetic_ref(ref: str, name: str) -> None:
    if not isinstance(ref, str) or not ref.startswith("synthetic:") or not ref[10:].strip():
        raise ValueError(name + " must be explicitly synthetic, never a historical claim")


@dataclass(frozen=True)
class PhasePrior:
    mean_deg: float
    concentration: float
    source_ref: str
    independence_basis: str


@dataclass(frozen=True)
class SyntheticPhaseModel:
    """Synthetic additive phase model conditional on a frozen forward operator.

    Every source label must be synthetic, not merely an arbitrary historical
    calibration ID. No claim that a recorded TLE is a calibrated observation.
    """

    rows: tuple[Datum, ...]
    anchors: tuple[OffsetAnchor, ...]
    phase_prior: PhasePrior
    purpose: str = "SYNTHETIC_TEST_ONLY"

    def __post_init__(self) -> None:
        if self.purpose != "SYNTHETIC_TEST_ONLY":
            raise ValueError("this reference sampler never creates a historical posterior")
        if not isinstance(self.phase_prior, PhasePrior):
            raise ValueError("explicit PhasePrior required")
        p = self.phase_prior
        _angle_deg(p.mean_deg, "prior mean")
        _kappa(p.concentration, "prior concentration")
        _synthetic_ref(p.source_ref, "phase prior reference")
        _synthetic_ref(p.independence_basis, "phase prior independence statement")
        if not isinstance(self.rows, tuple) or not self.rows:
            raise ValueError("explicit nonempty tuple of toy rows required")
        if not isinstance(self.anchors, tuple):
            raise ValueError("explicit anchor tuple required")
        for row in self.rows:
            if not isinstance(row, Datum):
                raise ValueError("explicit Datum required")
            _synthetic_ref(row.prediction_ref, "forward prediction reference")
            _synthetic_ref(row.calibration_ref, "measurement calibration reference")
        for anchor in self.anchors:
            if not isinstance(anchor, OffsetAnchor):
                raise ValueError("explicit OffsetAnchor required")
            _synthetic_ref(anchor.source_ref, "offset prior reference")
            _synthetic_ref(anchor.independence_basis, "offset independence statement")
        # Validate lineages, epochs, duplicate rows, finite angles, concentrations.
        anchored_marginal_log_density(self.rows, self.anchors)

    def log_target(self, phase_deg: float) -> float:
        """Unnormalized log p(theta | toy y, frozen H, priors), on S^1."""
        phase = _angle_deg(phase_deg, "phase")
        p = self.phase_prior
        shifted = tuple(
            Datum(r.norad, r.epoch_utc, r.lineage, r.observed_raan_deg,
                  (r.predicted_raan_deg + phase) % 360.0, r.kappa,
                  r.prediction_ref, r.calibration_ref)
            for r in self.rows
        )
        delta = math.radians(math.remainder(phase - p.mean_deg, 360.0))
        # Prior normalizer does not depend on theta. Keep only target differences.
        return (anchored_marginal_log_density(shifted, self.anchors)
                + float(p.concentration) * math.cos(delta))


@dataclass(frozen=True)
class SyntheticMCMCResult:
    chains_deg: tuple[tuple[float, ...], ...]
    acceptance_rates: tuple[float, ...]
    diagnostic: CircularDiagnostic
    seed: int
    warmup: int
    proposal_step_deg: float
    global_jump_probability: float
    interpretation: str = "SYNTHETIC_ONLY_NOT_HISTORICAL_POSTERIOR"


def sample_synthetic_phase(
    model: SyntheticPhaseModel, *, seed: int, draws_per_chain: int = 512,
    warmup: int = 256, proposal_step_deg: float = 45.0,
    global_jump_probability: float = 0.30,
) -> SyntheticMCMCResult:
    """Four independent MH chains on a circle using a symmetric mixture q.

    q(theta'|theta) = w Uniform(S1) + (1-w) WrappedNormal(theta, step).
    Both components are symmetric under theta <-> theta', thus log Hastings
    proposal ratio = 0. Warmup is discarded, not counted as posterior draws.
    Fixed tuning parameters; no adaptation to held-out data.
    """
    if not isinstance(model, SyntheticPhaseModel):
        raise ValueError("synthetic phase model required")
    if type(seed) is not int:
        raise ValueError("seed must be integer")
    if type(draws_per_chain) is not int or not 40 <= draws_per_chain <= 4096:
        raise ValueError("draws_per_chain must be 40..4096")
    if type(warmup) is not int or not 0 <= warmup <= 100000:
        raise ValueError("warmup must be an integer between 0 and 100000")
    if not (0.0 < _kappa(proposal_step_deg, "proposal step") <= 180.0):
        raise ValueError("positive proposal step <= 180 degrees required")
    if isinstance(global_jump_probability, bool) or not isinstance(
        global_jump_probability, (float, int)
    ) or not math.isfinite(global_jump_probability) or not (
        0.0 <= global_jump_probability <= 1.0
    ):
        raise ValueError("global jump probability must lie in [0,1]")

    chains: list[tuple[float, ...]] = []
    rates: list[float] = []
    total = warmup + draws_per_chain
    for chain_id in range(4):
        rng = random.Random(seed + 104729 * chain_id)
        theta = (45.0 + 90.0 * chain_id) % 360.0
        log_prob = model.log_target(theta)
        accepted = 0
        draws: list[float] = []
        for iteration in range(total):
            if rng.random() < global_jump_probability:
                proposed = rng.random() * 360.0
            else:
                proposed = (theta + rng.gauss(0.0, proposal_step_deg)) % 360.0
            proposed_log_prob = model.log_target(proposed)
            if math.log(max(rng.random(), 2.0 ** -1074)) < (
                proposed_log_prob - log_prob
            ):
                theta = proposed
                log_prob = proposed_log_prob
                accepted += 1
            if iteration >= warmup:
                draws.append(theta)
        chains.append(tuple(draws))
        rates.append(accepted / total)
    output = tuple(chains)
    return SyntheticMCMCResult(output, tuple(rates),
                               diagnose_circular_chains(output), seed, warmup,
                               float(proposal_step_deg),
                               float(global_jump_probability))


def circular_moment(chains: Sequence[Sequence[float]]) -> complex:
    """First circular moment; a zero resultant has no well-defined mean angle."""
    angles = [math.radians(_angle_deg(d, "sample")) for chain in chains for d in chain]
    if not angles:
        raise ValueError("no draws")
    return complex(math.fsum(math.cos(d) for d in angles) / len(angles),
                   math.fsum(math.sin(d) for d in angles) / len(angles))


def quadrature_circular_moment(
    model: SyntheticPhaseModel, *, nodes: int = 1440,
) -> complex:
    """Deterministic periodic midpoint quadrature as an INDEPENDENT toy oracle."""
    if not isinstance(model, SyntheticPhaseModel):
        raise ValueError("synthetic model required")
    if type(nodes) is not int or not 360 <= nodes <= 32768:
        raise ValueError("nodes must be integer in [360,32768]")
    angles = [(i + 0.5) * 360.0 / nodes for i in range(nodes)]
    log_probs = [model.log_target(phi) for phi in angles]
    peak = max(log_probs)
    weights = [math.exp(lp - peak) for lp in log_probs]
    total = math.fsum(weights)
    if not math.isfinite(total) or total <= 0.0:
        raise ArithmeticError("quadrature normalization invalid")
    return complex(
        math.fsum(w * math.cos(math.radians(phi)) for w, phi in zip(weights, angles)) / total,
        math.fsum(w * math.sin(math.radians(phi)) for w, phi in zip(weights, angles)) / total,
    )
