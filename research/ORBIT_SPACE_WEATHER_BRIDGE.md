# Castor: conditional historical space-weather drivers at physical RK4 stages

Scope: `src/lib/orbitSpaceWeatherAdapter.ts` provides an **offline, source-declared
NRLMSISE-00 input bridge** into `orbitPhysics.ts`, not a density model, not
SGP4, and not any authenticated 1963 NORAD orbital fit.

## Primary records and documentary dependency

- **GFZ Potsdam**: [historical planetary ap/Ap definitive time series](https://kp.gfz.de/en/data);
  3-hour linear `ap` (UTC bins), daily `Ap`; these and `Kp` are **one**
  planetary geomagnetic family, not independent channels. The actual queries,
  source payload SHA-256s and retrieved values are in
  [Lagarto's machine-readable ledger](meteorology/space_weather_msise_inputs_1963_11_07_09.json).
- **Natural Resources Canada**: [historical daily observed F10.7](https://www.spaceweather.gc.ca/solar_flux_data/daily_flux_values/F107_1947_1996.txt)
  (10⁻²² W m⁻² Hz⁻¹). This distinct solar observable is *not* itself an
  atmospheric-density measurement. Its 81-day **centered** average includes
  **future observations**, so it is suitable only for retrospective input
  reconstruction, not an operational forecast known at that historical epoch.
- [NCAR/GLOW NRLMSISE-00 reference](https://github.com/NCAR/GLOW/blob/master/nrlmsise00.f)
  specifies 7 positions: `[Ap_day, ap(t), ap(t−3h), ap(t−6h), ap(t−9h),
  mean(t−12h..t−33h), mean(t−36h..t−57h)]`. The two means include
  eight 3-hour intervals each.
- [NASA/Goddard *Satellite Situation Report* 15 Nov 1963 p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
  matrix **C197#1 / C201#1**, documents the **catalogued day**
  8 Nov 1963 for 1963-003B, but no UTC time, altitude, inertial state,
  density or location. NASA and NORAD catalog entries may share tracking
  provenance. Secondary 528 TLE mirror **C179#1 / C241-L1** is not an
  independent 527/529 Cartesian measurement. C151#1 is Recife upper-air
  wind, not local orbital density.

## Explicit physical interface and statuses

1. `deriveMsiseDriversAtUtc(snapshot, epochUtc)` uses observed F10.7 from the
   prior calendar day, a centered ±40-calendar-day F10.7 observed mean,
   daily planetary Ap, and the 3-hour `ap` bin at the requested **actual**
   UTC and previous 3/6/9 hours plus two historical averages.
   Refuses missing dates, bins, provenance or malformed snapshots. `Kp`
   is **never** substituted for linear `ap`. The 12:00 UTC snapshot rows
   are replay controls, **not** asserted reentry times.
2. `makeConditionalMsiseAtmosphere` inserts a stage-local density callback
   into the existing co-rotating drag term, calling a **caller-supplied**
   inertial-state-to-geodetic-and-local-solar-time transform and a
   **caller-supplied** named density solver on **each RK4 substage**. Both
   source strings and `Cd*A/m` are mandatory; geodetic latitude, longitude,
   altitude, local solar time and density must be finite and physically
   bounded. No inertial longitude is blindly equated with Earth-fixed
   longitude. The adapter neither asserts the supplied transform's accuracy
   nor runs an actual NRLMSISE implementation by itself.
3. A caller can choose any **conditional** state and solar/geomagnetic driver
   time within available historical series. Orbital uncertainties, original
   NORAD 527/529 position/epoch/frame/covariances, model discrepancy,
   instrument bias, proper ECI↔ECEF Earth orientation and density validation
   remain **unknown / NOT_RUN**. These are prerequisites for a
   historically calibrated trajectory, a claim of holdout skill, or a
   narrowing of any Lean-certified parameter domain.

## Reproducibility and deliberate negative tests

```sh
node --experimental-strip-types --test tests/orbitSpaceWeatherAdapter.test.mjs
node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitConvergence.test.mjs
```

Tests use the source-declared GFZ/NRC raw series to rebuild all three
**published scenario vectors** (7/8/9 Nov 12 UTC), then evaluate the
**06:00 UTC geomagnetic-bin boundary** dynamically inside RK4.
The injected density solver and Cartesian trajectories are **synthetic**
test doubles; their outputs cannot validate 1963 orbital observations.
Controls reject missing future days in the centered flux window, an
incomplete ap history, missing geodetic/time conversion, invalid density
and extrapolation outside covered epochs.

This interface adds a traceable connection **C17–C23 / C193 / Lagarto
GFZ+NRCan inputs → conditional drivers(t) → density model(t,r) → drag(r,v,t)**.
It produces no new active empirical restriction, exclusion of Conde,
reentry time, trajectory probability or SGP4 comparison. Its domain
reduction status remains **CONNECTED_PENDING_CALIBRATION**.
