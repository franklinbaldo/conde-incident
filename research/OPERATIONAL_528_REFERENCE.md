# Operational NORAD 528 source correction

This is a focused integration of Tartaruga [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14).
`src/lib/constants.ts`, `src/lib/pythonScriptExport.ts` and
`norad528_reconstruction.py` are copied from HEAD
`48ae4fd70fabe9bfc910a12c6a29916c2a088015` without modification.
They replace the project's old **unsourced** NORAD 528 vector by values
derived from the single tracked secondary literal now already in main
at `research/tle_custody/mirror_528_1963-10-27.tle` (PR #83).

Nominal 528 reference at 1963-10-27T14:40:16.132512Z:
RAAN 198.5261°, i 81.8615°, e 0.0017147,
argument of perigee 104.7477°, mean anomaly 255.4423°,
mean motion 15.74901460 rev/day. Pair SHA-256
`18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`
from the [public secondary mirror](https://www.itau.magnetic-declination.com/satellite/?s=528).
These are catalogued mean elements, not a certified physical state or
primary original 1963 TLE. The unsupported 284.1520° site value is
recoverable through Git and is no longer an active input.

527/529 illustrative vectors are explicitly downgraded to hypotheses,
not instrument measurements. A NASA catalogue **day** of decay is not
a measured 23:59 UTC reentry time, or a record of a ground impact.

The user explicitly requested source-first choices. The change does not
calibrate the model or infer reentry position; Monte Carlo samples are
sensitivity analyses, not historical posteriors. It does not touch blog
publishing. Run Python provenance regressions and existing Node/
TypeScript integration checks on the exact head.
