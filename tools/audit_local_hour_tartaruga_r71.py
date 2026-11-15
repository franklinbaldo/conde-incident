"""Guard: administrative-message clocks and newsroom affiliation are not event clocks."""
import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research/archive/conde_local_hour_bluebook_C241_TARTARUGA_R71.json"
EXPECTED = {
    "0809": (1756950, "4e8e460cfe8dfa0f0d6ea6b02017e6ff63915935dc5be5bde8e96f52faf6f326"),
    "0810": (1865459, "136be026e23acdd5e7ff0a5307e04bef799249b48346072a43cae1506be37ce9"),
    "0811": (1852266, "f9c55ab0b14d6e121a4419bef72519a68db29a9ceea6c5bca5ea31fb826cdce7"),
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def validate(d):
    require(d["schema"] == "conde.local_clock_custody/v1" and d["issue"] == 871, "schema/issue")
    n = d["nara"]
    require(n["naid"] == 302531012 and n["case_relation"] == "THREE_PAGES_ONE_ADMINISTRATIVE_CHAIN", "custody")
    require(n["local_event_clock"] is None and n["eyewitness_name"] is None, "invented NARA datum")
    items = n["objects"]
    require(len(items) == 3 and {x["object_id"] for x in items} == set(EXPECTED), "original pages")
    for x in items:
        size, sha = EXPECTED[x["object_id"]]
        require(x["source_bytes"] == size and x["source_sha256"] == sha, "mutated image hash/size")
        require(x["source_url"].endswith("/" + x["object_id"] + ".jp2"), "wrong image")
        require(x["reading"] == "COMPLETE_SINGLE_IMAGE" and x["status"] == "LIDO_SEM_HORA", "false reading scope")
        require(x["event_clock"] is None and x["eyewitness_name"] is None, "invented event observation")
        require(x["independent_witness"] is False, "false independent witness")
        if x["telegram_clock"] is not None:
            require(x["telegram_clock_role"] == "MESSAGE_NOT_EVENT", "message clock promoted to event")
    papers = d["newspapers"]
    require(len(papers) == 3 and [x["date"] for x in papers] == ["1963-11-08", "1963-11-09", "1963-11-08"], "target dates")
    for x in papers:
        require(x["status"] == "INACESSIVEL" and x["scope"] == "ORIGINAL_EDITION_NOT_READ", "false newspaper reading")
        require(x["original_page"] is None and x["original_sha256"] is None and x["reported_event_clock"] is None, "invented original evidence")
        require(x["article_independence"] == "UNDETERMINED", "invented reporter independence")
        if x["title"] == "Diário de Notícias":
            require(x["editorial_network"] == "DIARIOS_ASSOCIADOS", "network dependence erased")
    for flag in ("hour_found", "independent_observation", "orbital_constraint"):
        require(d["limits"][flag] is False, "false historical finding " + flag)
    require(d["limits"]["no_external_contact"] is True, "external contact")
    return True

if __name__ == "__main__":
    print("PASS" if validate(json.loads(MANIFEST.read_text(encoding="utf-8"))) else "FAIL")
