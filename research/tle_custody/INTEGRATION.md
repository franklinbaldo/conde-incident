# Traceable reference orbit, not an authenticated 1963 NORAD observation

This is a minimal custody slice extracted without changes from Tartaruga
[PR #14](https://github.com/franklinbaldo/conde-incident/pull/14)
HEAD `48ae4fd70fabe9bfc910a12c6a29916c2a088015`.
The preserved two-line literal comes from the [secondary 528 mirror](https://www.itau.magnetic-declination.com/satellite/?s=528),
SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`.
Epoch `63300.61129783` = 1963-10-27 14:40:16.132512 UTC;
RAAN 198.5261°, inclination 81.8615°, eccentricity 0.0017147,
mean motion 15.74901460 rev/day. The same family of values appears in the
oxzoid Parquet mirror documented by C25#1/C179#1 in the [integrated matrix](../evidence_matrix_C001-C238_2026-11-11.md).
Two copies can share one tracking origin. A checksum is only a
syntax/integrity check; it does **not** authenticate the primary observing
station, original epoch, frame or physical uncertainty.

The former site's RAAN 284.1520° (and its synthesized TLE) is NOT
considered an additional observation or an active model scenario. Its
Git history remains available, and the original PR #14 still contains
other custody analyses for later small integrations.

No back-propagated site, atmospheric drag estimate, historical Bayesian
posterior, orbit termination epoch or impact location is asserted.
The primary NASA/Goddard *Satellite Situation Report* 15 Nov 1963 p.8
(https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
documents the day 8 Nov 1963, not a full positional orbit.

Verify with `node --test scripts/tle-528-provenance.test.mjs`
under the existing exact-head integration workflow.


## Auditor independente de sintaxe (C241-L1)

O subconjunto `tools/tle_literal_layout.py` e `tests/test_tle_literal_layout.py`
foi separado da PR histórica #14 sobre a `main` (sem importar outros
scripts do Parquet nem alterar o único par literal). Para gerar relatório:

```bash
python -m unittest discover -s tests -p 'test_tle_literal_layout.py' -v
python tools/tle_literal_layout.py \
  --pair research/tle_custody/mirror_528_1963-10-27.tle \
  --output /tmp/tle_528_literal_audit.json
```

O workflow `tle-literal-layout.yml` confere checkout no HEAD real e arquiva JSON.
Isso testa o **formato da cópia moderna**, não checksum de 45 TLEs originais.
