# 🐙 Evidence to physical observables: independent Polvo slice

Extracted from the large draft Polvo [PR #17](https://github.com/franklinbaldo/conde-incident/pull/17),
source HEAD `a51735704fca07f41e29b0ffb24babf4ab44ca8f`.
`physical_observable_bridge.py` and the six tests are ported with the
source registry's minimal read-only hash and C44–C46 identity checks
inlined, so this PR does NOT import the full unfinished Lean registry.

Already integrated: [C01–C238 matrix #79](https://github.com/franklinbaldo/conde-incident/pull/79),
Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7`. A SHA mismatch
fails the extraction. C179#1 contains a single secondary TLE reference
for NORAD 528, with RAAN 198.5261° at 1963-10-27 14:40:16.132512 UTC;
its primary origin and error covariance remain unknown. C151#1
contains NOAA/NCEI IGRA **Recife** winds on 8 Nov 1963, not observations
of winds over Conde. C144–C146 are Navy synoptic charts, not directly
measured upper-air conditions in Conde.

The script computes n rev/day to rad/s, Kepler proxy semimajor axis/perigee,
first-order J2 nodal rate; hPa to Pa; meteorological wind direction
FROM to east/north components; and a **hypothetical** 50 m/s descent
over the five selected Recife levels (~11 km to ~1.56 km). It exports
structured source URLs, matrix occurrences, missing uncertainty flags,
and conditional drift. No geographic inference is made and the script
does not constrain the 528 physical orbit.

**Not performed:** atmospheric transfer from Recife to Conde, measured
surviving fragment mass/area/Cd, density at the reentry path, MCMC
posterior, primary original NORAD 528 tracking, or 527/529 blind physical
holdout. No impact location follows. See source SHA in PR #17 and
[historical original NASA/Goddard SSR 15 Nov 1963 p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
for a catalogued day only.

Validation: `python3 -m unittest discover -s formal/tests -p 'test_physical_observable_bridge.py' -v`,
and dedicated exact-head GitHub workflow exporting a JSON artifact. A later
PR may connect the Castor model to this contract, but cannot treat it as
calibrated meteorological data for Conde.
