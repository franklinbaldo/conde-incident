"""CGEO-83: assigned folios must not become unsupported incident clocks."""
import copy
import json
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "research/editorial/cgeo83_uh_ne_page4_core_20261115.json"
HASHES = {
    "00474": "3d7b9268c1cf45c7700ddf65bfa985c9d17724369d9b0412f9442f4fea87faad",
    "00476": "89af71800faf3d447cf7fd3a2ee473ba010516beb8dc45dd200d220ad65c8047",
    "00477": "0a5170a69e037166ef1fdf502797cef8fc74211b45183af0da775eedc7072fb0",
}
SCOPE = [("00474", 4, 3, False), ("00476", 4, 4, False), ("00477", 4, 4, True)]

def validate(d):
    faults = []
    if d.get("id") != "CGEO-83" or not d.get("method",{}).get("source_hash_rechecked"):
        faults.append("identity-or-custody")
    sources = d.get("sources", [])
    if len(sources) != 3 or {x.get("edition"):x.get("sha256") for x in sources} != HASHES:
        faults.append("pdf-source-provenance")
    rows = d.get("pages",[])
    if [(x.get("edition"),x.get("pdf_page"),x.get("printed_folio"),x.get("within_news_core")) for x in rows] != SCOPE:
        faults.append("pdf-page-vs-printed-folio-or-news-core")
    if any(x.get("reading_status")!="EXAMINADA" or x.get("event_hour") is not None
           or x.get("eyewitnesses") != [] or x.get("incident_article") is not False
           for x in rows):
        faults.append("promoted-event-observable")
    if len(rows)==3 and (rows[0].get("section")!="SOCIEDADE_CINEMA"
                         or rows[1].get("section")!="SOCIEDADE_CINEMA"
                         or rows[2].get("section")!="OPINIAO_POLITICA_NACIONAL"):
        faults.append("wrong-section")
    gen=d.get("genealogy",{})
    if gen.get("independent_phenomenon_hour") is not None or gen.get("new_independent_testimony") is not False or gen.get("orbital_candidate") is not None or gen.get("orbital_exclusion_licensed") is not False:
        faults.append("invented-physics")
    cov=d.get("coverage_note",{})
    if (cov.get("new_pdf_pages_scoped"),cov.get("additional_core_pages_examined"),cov.get("outside_core_pages_examined"))!=(3,1,2):
        faults.append("inflated-coverage")
    return faults

class TestCGEO83(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertEqual(validate(self.source),[])

    def test_adversarial(self):
        mutations = {
            "invent-hour":lambda x:x["pages"][2].__setitem__("event_hour","20h15"),
            "invent-witness":lambda x:x["pages"][0].__setitem__("eyewitnesses",["unknown"]),
            "invent-incident":lambda x:x["pages"][1].__setitem__("incident_article",True),
            "misread-folio":lambda x:x["pages"][0].__setitem__("printed_folio",4),
            "promote-society":lambda x:x["pages"][0].__setitem__("within_news_core",True),
            "wrong-hash":lambda x:x["sources"][1].__setitem__("sha256","0"*64),
            "invent-orbit":lambda x:x["genealogy"].__setitem__("orbital_candidate",528),
            "inflate-core":lambda x:x["coverage_note"].__setitem__("additional_core_pages_examined",3),
            "lost-custody":lambda x:x["method"].__setitem__("source_hash_rechecked",False),
        }
        for name,modify in mutations.items():
            with self.subTest(name=name):
                altered=copy.deepcopy(self.source)
                modify(altered)
                self.assertNotEqual(validate(altered),[],name)

if __name__ == "__main__":
    unittest.main()
