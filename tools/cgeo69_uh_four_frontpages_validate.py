"""CGEO-69: verify scoped, fully viewed UH front pages and reject overclaims."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/editorial/cgeo69_uh_four_frontpages_20261115.json"
INVENTORY = ROOT / "research/editorial/cgeo65_uh_bn_inventory_20261115.json"
COVERS = ROOT / "research/editorial/cgeo66_uh_cover_dates_20261115.json"
PREREG = ROOT / "research/editorial/cgeo64_null_narrative_prereg_20261114.json"
FROZEN = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"

# These rows were transcribed only after visual checking all quadrants of PDF page 1.
EXPECTED = {
    "00442": ("1963-10-09", "CONTROL_OCT07", "7b7c6189f86a9da5457332927f847262a72a4d0989a18f9b0042283c83e90a6a", "Mobilização do povo contra custo de vida", []),
    "00447": ("1963-10-14", "CONTROL_OCT14", "e249c946712b7685e0a34d3de9a7250929957deb7a4c5894fbdb94aa0d02242b", "Autoridades dominam situação: paz de novo nos sindicatos do campo", [
        ("F07_HEAVY_CLOTHES", "pesados encargos", "Economic or organizational burdens, not heavy clothing; adjectival coincidence only.")]),
    "00455": ("1963-10-22", "CONTROL_OCT21", "d4e08e37c815b538d29eb56c2354ddb3d60b8e2f3dbf27573d643693a7110830", "Arraes recusa diálogo proposto por Lacerda", [
        ("F07_HEAVY_CLOTHES", "à queima-roupa", "Idiom referring to shooting at close range in a police story, not heavy clothing.")]),
    "00467": ("1963-11-04", "TARGET_NOV04", "82c0345dccc9c7d48db3512b134b84b0d1d39579410b5f91530109674bd995f9", "Povo com JG pela lei de remessa de lucros", [
        ("F04_WINDOWS", "abertura do Congresso de Geologia", "Opening ceremony/event, not an opening or window in a metal sphere.")]),
}
EXPECTED_WEEKS = ("CONTROL_OCT07", "CONTROL_OCT14", "CONTROL_OCT21", "TARGET_NOV04")
EXPECTED_LIMITS = {"independent_event_witness_found": False, "narrative_fabrication_proven": False,
                   "chronology_of_8_nov_known": False, "historical_center_1963": None,
                   "orbital_constraint_activated": False}


EXPECTED_METHOD = 'Four pre-registered date slots, one front page from each target/baseline week. For each, verify PDF SHA-256 on Ifro, render PDF p.1 at 3200 px and inspect every quadrant visually, check full-page embedded text for pre-frozen anchors. OCR and text-layer absence alone do not establish absence; distinguish unrelated lexical coincidences. Source images retained on Ifro, not published. Headline/transcription is context, not a separate witness.'
EXPECTED_CAVEAT = 'Page 1 was selected as a repeatable page number; chosen issue dates are a deliberately small convenience checkpoint within the frozen slots, NOT a random or exhaustive sample of each week. No other pages of the selected issues counted; do not extrapolate page-level negatives to entire issues, weeks, or newspapers.'
EXPECTED_LIMITATIONS = ['Zero confirmed matches applies only to these four individual front pages, not to editions or unexamined pages.', 'Many front-page stories continue inside their issue; absence from the cover does not establish absence from their whole article.', 'The same newspaper edition is one publication lineage; the four dates are not four independent Conde witnesses.', 'Historical OCR/text layers can omit or corrupt words; the visual review limits only what is legible on the selected page.', "An ordinary 'abertura', 'pesados encargos' or 'queima-roupa' is not the composite FBIS spacecraft motif.", 'No independent local event hour, 1963 geographical point, orbital restriction, copying chronology or deliberate fabrication can be inferred.']
TOP_KEYS = {'prereg_blob_sha', 'method', 'date_utc', 'interpretation', 'issue', 'prereg_path', 'source_cover_crosswalk', 'selection_caveat', 'coverage', 'type', 'pages', 'limitations', 'source_inventory_path', 'id'}
PAGE_KEYS = {'review', 'date', 'confirmed_article_counts', 'independent_conde_witness', 'source_url', 'headline_as_seen', 'ambiguous_lexical_leads', 'pdf_page', 'publication', 'week', 'countable_page', 'issue_id', 'whole_edition_read', 'source_sha256'}
COVERAGE_KEYS = {'predeclared_slots_changed', 'baseline_full_corpus', 'first_pre_event_occurrence', 'front_pages_inspected', 'other_pages_read_in_this_fatia', 'general_verdict', 'whole_issues_read', 'pages_per_week', 'observed_page_rates', 'jb_pages_read'}
LEAD_KEYS = {'text', 'fragment', 'context', 'fragment_match'}

def require_keys(data: dict, expected: set[str], label: str) -> None:
    require(type(data) is dict and set(data) == expected, label + " keys changed")

def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def validate(doc: dict, inv: dict, covers: dict, prereg: dict) -> int:
    require_keys(doc, TOP_KEYS, "document")
    require(doc["date_utc"] == "2026-11-15", "audit date")
    require(doc["method"] == EXPECTED_METHOD and doc["selection_caveat"] == EXPECTED_CAVEAT
            and doc["limitations"] == EXPECTED_LIMITATIONS, "unreviewed narrative claim")
    prereg_raw = PREREG.read_bytes()
    require(blob_sha(prereg_raw) == FROZEN, "prereg source blob differs from frozen SHA")
    require(prereg == json.loads(prereg_raw), "prereg in-memory data differs from frozen file")
    require((doc.get("type"), doc.get("id")) ==
            ("HistoricalPressFrozenWeekFrontPageAudit", "CGEO-69"), "identity")
    require(doc.get("issue") == "https://github.com/franklinbaldo/conde-incident/issues/887", "issue")
    require(doc.get("prereg_blob_sha") == FROZEN and
            doc.get("prereg_path") == "research/editorial/cgeo64_null_narrative_prereg_20261114.json", "frozen prereg")
    require(prereg.get("id") == "CGEO-64" and len(prereg["frozen_fbis_fragments"]) == 8, "prereg identity")
    require(doc.get("source_inventory_path") == "research/editorial/cgeo65_uh_bn_inventory_20261115.json" and
            doc.get("source_cover_crosswalk") == "research/editorial/cgeo66_uh_cover_dates_20261115.json", "source paths")
    require(inv.get("id") == "CGEO-65" and covers.get("id") == "CGEO-66", "source identities")
    sources = {row["id"]: row for row in inv["issues"] if row["status"] == "PDF_BYTES_ACQUIRED"}
    dated = {row["issue_id"]: row["date"] for row in covers["cover_dates"]}
    slots = {(row["publication"], row["issue_id"]): (row["date"], row["week"])
             for row in covers["slots"] if row["issue_id"] is not None}
    fragments = {x["id"] for x in prereg["frozen_fbis_fragments"]}
    pages = doc.get("pages", [])
    require(len(pages) == 4 and {p.get("issue_id") for p in pages} == set(EXPECTED), "exactly 4 distinct pages")
    for row in pages:
        require_keys(row, PAGE_KEYS, "page")
        key = row["issue_id"]
        date, week, sha, headline, leads = EXPECTED[key]
        require((row.get("publication"), row.get("date"), row.get("week"),
                 row.get("pdf_page"), row.get("headline_as_seen")) ==
                ("UH_RE", date, week, 1, headline), "date/week/page/headline")
        require(sources[key]["sha256"] == sha == row.get("source_sha256"), "source SHA")
        require(sources[key]["url"] == row.get("source_url"), "source URL")
        require(sources[key]["pages"] >= 1 and dated[key] == date and
                slots[("UH_RE", key)] == (date, week), "source date/slot")
        require(row.get("review") == "FULL_FRONT_PAGE_VISUAL_4_QUADRANTS_AND_TEXT_LAYER"
                and row.get("countable_page") is True, "visual full page")
        require(row.get("whole_edition_read") is False and
                row.get("independent_conde_witness") is False, "independence/coverage")
        counts = row.get("confirmed_article_counts")
        require(isinstance(counts, dict) and set(counts) == fragments and
                all(type(counts[k]) is int and counts[k] == 0 for k in fragments), "8 scoped negatives")
        actual_leads = row.get("ambiguous_lexical_leads", [])
        require(len(actual_leads) == len(leads), "leads cardinality")
        for lead in actual_leads:
            require_keys(lead, LEAD_KEYS, "lexical lead")
        require([(lead.get("fragment"), lead.get("text"), lead.get("context"),
                  lead.get("fragment_match")) for lead in actual_leads] ==
                [(frag, txt, ctx, False) for frag, txt, ctx in leads], "adjudicated false leads")
    coverage = doc.get("coverage", {})
    require_keys(coverage, COVERAGE_KEYS, "coverage")
    require(coverage.get("front_pages_inspected") == 4 and
            coverage.get("pages_per_week") == {w: 1 for w in EXPECTED_WEEKS}, "coverage pages")
    byweek = coverage.get("observed_page_rates", {})
    require(set(byweek) == set(EXPECTED_WEEKS), "week strata")
    for week in EXPECTED_WEEKS:
        require(set(byweek[week]) == fragments, "fragment strata")
        for frag in fragments:
            require(byweek[week][frag] == {"confirmed_articles": 0, "pages_read": 1},
                    "only observed-page rate")
    require({k: coverage.get(k) for k in ("whole_issues_read", "other_pages_read_in_this_fatia",
                                          "jb_pages_read", "predeclared_slots_changed")} ==
            dict.fromkeys(("whole_issues_read", "other_pages_read_in_this_fatia",
                           "jb_pages_read", "predeclared_slots_changed"), 0), "no false edition count")
    require(coverage.get("baseline_full_corpus") is None and
            coverage.get("first_pre_event_occurrence") is None and
            coverage.get("general_verdict") == "UNDETERMINED", "no ungrounded inference")
    require(doc.get("interpretation") == EXPECTED_LIMITS, "causal/physical limits")
    return len(pages)


if __name__ == "__main__":
    result = validate(*[json.loads(path.read_text(encoding="utf-8"))
                        for path in (DATA, INVENTORY, COVERS, PREREG)])
    print(f"CGEO-69: {result} front pages, 1 per week; only scoped negatives; general verdict UNDETERMINED")
