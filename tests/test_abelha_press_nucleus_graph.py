"""Offline integrity and adversarial tests for the bounded press nucleus graph."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public/data/conde-press-nucleus-provenance-r37.json"
EXPECTED_SOURCE_SHA = {
    "SRC:R79": "75dc400708e80022dc9d1a139739068417e65ff47a3c4130bf0b46b9db4929f3",
    "SRC:R86": "d3b6301c192f8513c8a9a53a06d18eb47fc82b76fda45b6438bc1f416e8854e0",
    "SRC:CGEO77": "0a5170a69e037166ef1fdf502797cef8fc74211b45183af0da775eedc7072fb0",
}
EXPECTED_OCCURRENCES = {
    "OCC:CM21658:DENIAL", "OCC:CM21661:CURVELLO",
    "OCC:UH00477:STANISLAW", "OCC:CORE871:NO_EVENT_HOUR",
}

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result

def validate(d, root=ROOT):
    def need(condition, message):
        if not condition:
            raise ValueError(message)
    need(d["schema"] == "conde.press-nucleus-documentary-bridge/v1", "schema")
    need(d["id"] == "ABELHA-R37-P1-PRESS-20261117", "bridge identity")
    sources = d["sources"]
    need({s["id"] for s in sources} == {*EXPECTED_SOURCE_SHA, "SRC:871-CORE"} and len(sources) == 4, "source IDs")
    for s in sources:
        if s["id"] in EXPECTED_SOURCE_SHA:
            need(s["source_pdf_sha256"] == EXPECTED_SOURCE_SHA[s["id"]], "source SHA")
            path = root / s["path"]
            need(path.is_file(), "missing original manifest")
            manifest = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
            if s["id"] == "SRC:R79":
                actual = manifest["pdf_sha256"]
            elif s["id"] == "SRC:R86":
                actual = manifest["sources"][1]["sha256"]
            else:
                actual = manifest["sources"][1]["sha256"]
            need(actual == s["source_pdf_sha256"], "original manifest changed")
        else:
            need(s["path"] is None and s["source_pdf_sha256"] is None and
                 s["source_url"].endswith("#issuecomment-6906090911"), "unverified closure source")
    need(sources[0]["editorial_family"] == sources[1]["editorial_family"] == "CORREIO_DA_MANHA",
         "same newspaper must share editorial family")
    claims = d["occurrences"]
    need(len(claims) == 4 and {c["id"] for c in claims} == EXPECTED_OCCURRENCES, "occurrence cardinality")
    need(len({c["doc_id"] for c in claims}) == 4 and len({c["source_id"] for c in claims}) == 4, "doc/source cardinality")
    for c in claims:
        need(c["state"] == "CANDIDATE_NOT_ACTIVATED" and c["active"] is False, "activation")
        need(c["event_time_utc"] is None and c["named_event_eyewitness"] is None
             and c["identified_norad_object"] is None, "invented physical observation")
        need(c["source_independence"] != "INDEPENDENT_PRIMARY_EVENT_WITNESS", "false independence")
        need(c["source_id"] in {s["id"] for s in sources}, "dangling provenance")
    need([c["publication_date"] for c in claims] == [
        "1963-11-10", "1963-11-14", "1963-11-14", None
    ], "historical publication versus research date")
    need(claims[3]["research_date"] == "2026-11-16", "research date")
    coverage = d["coverage"]
    editions = coverage["editions"]
    need(len(editions) == 16 and len({(e["family"], e["edition"]) for e in editions}) == 16, "edition cardinality")
    total = 0
    illegible = 0
    for e in editions:
        pages = e["examined_pdf_pages"]
        partial = e["partially_illegible_pdf_pages"]
        need(len(pages) == len(set(pages)) and set(partial) <= set(pages), "page cardinality")
        total += len(pages)
        illegible += len(partial)
    need((total, illegible) == (144, 4) and
         (coverage["examined_pdf_pages_total"], coverage["partially_illegible_pages_total"]) == (144, 4), "denominator")
    need(coverage["no_hour_found_in_examined_scope"] is True and
         coverage["negative_for_complete_editions"] is False and
         coverage["physical_absence_proven"] is False, "false global negative")
    nodes = d["nodes"]
    ids = [n["id"] for n in nodes]
    need(len(ids) == len(set(ids)) == 17, "node cardinality")
    node_by_id = {n["id"]: n for n in nodes}
    for node_id in ("LATENT:CONDE:EVENT_HOUR", "LATENT:CONDE:PRIMARY_NEWS_INDEPENDENCE",
                    "PARAM:reentry_528_time_window", "PARAM:reentry_637_time_window"):
        node = node_by_id[node_id]
        need(node["activation"] is False and node["value"] is None,
             "latent or simulator parameter promoted without evidence")
    lean = node_by_id["LEAN:candidatePressClockCompatibility"]
    need(lean["activation"] is False and lean["status"] == "NOT_COMPILED_NOT_PROMOTED",
         "Lean candidate promoted without proof")
    edges = d["edges"]
    pairs = [(e["source"], e["target"]) for e in edges]
    need(len(pairs) == len(set(pairs)) == 20, "edge cardinality")
    need(all(a in ids and b in ids for a, b in pairs), "orphan graph edge")
    for e in edges:
        if e["source"].startswith("LATENT:"):
            need(e["relation"] == "PREMISE_NOT_ESTABLISHED", "unjustified latent premise")
        elif e["source"].startswith("LEAN:"):
            need(e["relation"] == "NOT_ACTIVATED", "unjustified simulation activation")
    for c in claims:
        need((c["source_id"], c["doc_id"]) in pairs and (c["doc_id"], c["id"]) in pairs, "broken occurrence path")
        need((c["id"], "LATENT:CONDE:EVENT_HOUR") in pairs, "lost clock dependency")
        need((c["id"], "LATENT:CONDE:PRIMARY_NEWS_INDEPENDENCE") in pairs, "lost provenance dependency")
    state = d["epistemic"]
    need((state["event_time_utc"], state["physical_constraints_active"],
          state["delta_links"], state["delta_physical_domain"], state["theta"],
          state["historical_mcmc"], state["norad_528_excluded"], state["norad_637_excluded"])
         == (None, 0, 20, 0, "UNCHANGED", "NOT_RUN", False, False), "unjustified physical inference")
    need(d["independence"]["independent_instrumental_observations_added"] == 0 and
         d["independence"]["primary_event_witnesses_identified"] == 0 and
         d["independence"]["underlying_news_independence_proven"] is False, "independence")
    return True

class PressNucleusGraphTest(unittest.TestCase):
    def setUp(self):
        self.graph = json.loads(DATA.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)

    def test_integrated_source_references_and_graph(self):
        self.assertTrue(validate(self.graph))

    def mutate(self, action):
        changed = copy.deepcopy(self.graph)
        action(changed)
        with self.assertRaises(ValueError):
            validate(changed)

    def test_reject_unjustified_event_hour(self):
        self.mutate(lambda d: d["occurrences"][1].__setitem__("event_time_utc", "1963-11-08T23:30:00Z"))

    def test_reject_fabricated_independent_witness(self):
        self.mutate(lambda d: d["occurrences"][0].__setitem__("source_independence", "INDEPENDENT_PRIMARY_EVENT_WITNESS"))

    def test_reject_orphan_edge(self):
        self.mutate(lambda d: d["edges"][0].__setitem__("source", "SRC:MISSING"))

    def test_reject_missing_occurrence(self):
        self.mutate(lambda d: d["occurrences"].pop())

    def test_reject_wrong_denominator(self):
        self.mutate(lambda d: d["coverage"]["editions"][0]["examined_pdf_pages"].pop())

    def test_reject_global_negative(self):
        self.mutate(lambda d: d["coverage"].__setitem__("negative_for_complete_editions", True))

    def test_reject_physical_activation(self):
        self.mutate(lambda d: d["epistemic"].__setitem__("physical_constraints_active", 1))

    def test_reject_promoted_latent_value(self):
        self.mutate(lambda d: d["nodes"][12].__setitem__("value", "1963-11-08T23:30:00Z"))

    def test_reject_promoted_simulator_parameter(self):
        self.mutate(lambda d: d["nodes"][-1].__setitem__("activation", True))

    def test_reject_unproven_lean_promotion(self):
        self.mutate(lambda d: d["nodes"][-3].__setitem__("status", "COMPILED"))

    def test_reject_activated_relation_without_evidence(self):
        self.mutate(lambda d: d["edges"][-1].__setitem__("relation", "ACTIVATED"))

    def test_reject_false_editorial_independence(self):
        self.mutate(lambda d: d["sources"][1].__setitem__("editorial_family", "PRIMARY_INDEPENDENT"))

    def test_reject_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=unique_pairs)

if __name__ == "__main__":
    unittest.main()
