# Integrating the immutable C01–C238 evidence snapshot

This PR adds only the cumulative research ledger and an integrity regression.
Source is exact file from scientific [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), HEAD `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`,
Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7`.

241 **occurrences** cover 238 labels; C44, C45 and C46 each have two
different occurrences and must not be silently merged. The document is a
historical research trail with explicit errors and errata, not a list of 238
verified physical facts or a numerical likelihood.

**Source chain:** C131 and C197 cite the same original NASA/Goddard
Satellite Situation Report 15 Nov 1963, printed p.8
(https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
for a date of decay only. C179 cites a retrospective secondary 528 orbital
mirror, not an independently authenticated 1963 TLE. C144–C146 cite Navy
synoptic charts; C149–C151 are Recife IGRA meteorological sounding evidence,
not measured weather at Conde.

**Open documentation correction:** independent Gavião review in #1 pointed
out a PDF-index/pagination locator error for C197 (printed page 8 is PDF viewer
page 10, zero-based page 9). Preserve this original file's hash for upstream
Polvo registry tests and correct the citation in a separately reviewed,
repinned follow-up (see #61), without rewriting research history.

Run `node --test scripts/matrix-ledger.test.mjs`; the merged exact-head CI
also executes this test. The matrix changes no active model, impact
probability, website or blog.
