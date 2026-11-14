"""Audit a verified Polish technical bibliography without inventing 1963 observations."""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/tle_custody/polish_nafa_soviet_refs_C241_LONTRA_R60.json"
SHA256 = "f83992fecb15d01fbba0a9e8e3b94bdc81d6620f89ed4790dc4c5ee940bed0c4"
URL = "https://www.urania.edu.pl/sites/default/files/archiwum/postepy_astronomii_1969_01.pdf"
SIZE = 7630958

def validate(data):
    if data.get("id") != "C241-LONTRA-R60" or data.get("evidence_class") != "VERIFIED_1969_TECHNICAL_BIBLIOGRAPHY_AND_1963_PRIMARY_LOCATOR":
        raise ValueError("Wrong identity or epistemic class")
    src = data.get("source", {})
    expected = {"author":"S. Oszczak","volume":17,"issue":1,"year":1969,
                "printed_pages":"61-71","pdf_page_indices_zero_based_verified_visually":[62,72],
                "url":URL,"bytes":SIZE,"sha256":SHA256,"pdf_magic":"%PDF-1.6","pdf_eof_seen":True}
    if any(src.get(key) != value for key,value in expected.items()):
        raise ValueError("Bibliographic source or PDF custody mutated")
    if "not original 1963" not in src.get("custody_scope", ""):
        raise ValueError("Secondary article promoted to original observation")
    refs = data.get("source_references", [])
    if len(refs) != 5 or sorted(r.get("reference") for r in refs) != [1,2,7,10,13]:
        raise ValueError("Missing or additional primary bibliographic references")
    for ref in refs:
        if ref.get("status") != "CITED_NOT_RETRIEVED":
            raise ValueError("Bibliographic locator promoted to retrieved source")
    r13 = next(r for r in refs if r["reference"] == 13)
    if r13.get("year") != 1963 or r13.get("bulletin_issue") != 32 or r13.get("authors") != ["L. I. Medvedeva","B. A. Firago"]:
        raise ValueError("1963 Bulletin 32 locator mutated")
    bound = data.get("boundaries",{})
    if any(bound.get(key) is not False for key in
           ("original_1963_bulletin_32_retrieved","original_1963_azh_article_retrieved",
            "chronograph_21p_same_instrument_proven","institutional_contact_sent")):
        raise ValueError("Unverified primary source, crosswalk or contact promoted")
    if bound.get("observations_norad_527_528_529") != [] or bound.get("independent_instrumental_observations") != 0 or bound.get("new_orbital_constraints") != 0:
        raise ValueError("No new NORAD or orbital constraints from bibliography")
    return True

def replay_pdf():
    request = urllib.request.Request(URL,headers={"User-Agent":"conde-incident-archive-custody/1.0"})
    checksum=hashlib.sha256()
    count=0
    prefix=b""
    trailer=b""
    with urllib.request.urlopen(request,timeout=40) as stream:
        while chunk:=stream.read(131072):
            if not prefix:
                prefix=chunk[:8]
            trailer=(trailer+chunk)[-256:]
            checksum.update(chunk)
            count+=len(chunk)
    if count != SIZE or checksum.hexdigest() != SHA256 or prefix != b"%PDF-1.6" or b"%%EOF" not in trailer:
        raise ValueError("Live PDF not equal to the archived 2026-11-14 evidence")
    return count

if __name__=="__main__":
    data=json.loads(PATH.read_text(encoding="utf-8"))
    validate(data)
    if "--live" in sys.argv:
        print("R60 LIVE PDF VERIFIED:",replay_pdf(),"bytes")
    else:
        print("R60 manifest PASS; live replay NOT_RUN")
