"""Fail-closed scoped audit of two visually reviewed FBN newspaper pages (R73)."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/archive/ultima_hora_ne_space_page_closeout_R73.json"
EXPECTED = {
    "00473": ("1963-11-10", 5, 18, 8298891, "f37e4afa500fe841546a751e562cc799c33c699decb8967b2ae00b45e721e349", 'NASA: "Explorer 18" Abrirá Caminho Aos Cosmonautas', "WASHINGTON, 10 (FP)"),
    "00475": ("1963-11-12", 5, 10, 5031193, "88859dfbab5e9590614b684121507c7eb54148028a66d1efb9a3269d6444611f", 'URSS no Páreo Para Conquista da Lua: "Polet I" Rasga Caminho Aos "Vostoks"', "MOSCOU, 12 (FP)"),
}
REQUIRED_TOP = {"schema","id","refs_issue","review_date_utc","rationale","method","pages","external_crosscheck","result","limitations"}
REQUIRED_PAGE = {"edition","date_printed","pdf_page","printed_page","pdf_pages","pdf_bytes","pdf_sha256","pdf_url","review_status","full_page_visual_columns_reviewed","space_headline_literal","space_dateline_literal","space_article_classification","other_content","previous_ledger_correction","conde_ba_reference_found","fragment_sphere_or_fall_in_brazil_found","independent_event_time_literal","independent_witness","orbital_observation_of_528_or_637","source_credit_literal"}
REQUIRED_RESULT = {"target_pages_closed":2,"target_pages_total":2,"full_editions_read":False,"other_46_pages_scope":"CAPA_OU_PANORAMA_MAIS_TRIAGEM_LEXICAL","confirmed_independent_local_event_time":None,"independent_witness":None,"all_four_editions_negative":False,"physical_orbital_constraint_added":False,"next_blocker":"conde-incident#884 item 2: A Tarde e Jornal da Bahia, acesso humano"}

def validate(data):
    if not isinstance(data,dict) or set(data)!=REQUIRED_TOP:
        raise ValueError("R73: top-level keys altered")
    if (data["schema"], data["id"], data["refs_issue"], data["review_date_utc"]) != ("conde.newspaper_two_page_closeout/v1","C241-LONTRA-R73",871,"2026-11-15"):
        raise ValueError("R73: identity altered")
    if data["result"]!=REQUIRED_RESULT or data["method"].get("pdftotext_negative_inference") is not False or data["method"].get("new_ocr_performed") is not False:
        raise ValueError("R73: unsupported broad inference")
    if len(data["pages"])!=2 or [p.get("edition") for p in data["pages"]] != list(EXPECTED):
        raise ValueError("R73: wrong page set")
    for p in data["pages"]:
        if not isinstance(p,dict) or set(p)!=REQUIRED_PAGE:
            raise ValueError("R73: page fields altered")
        number=p["edition"]
        date,page,count,size,sha,headline,dateline=EXPECTED[number]
        if (p["date_printed"],p["pdf_page"],p["printed_page"],p["pdf_pages"],p["pdf_bytes"],p["pdf_sha256"],p["pdf_url"],p["space_headline_literal"],p["space_dateline_literal"]) != (date,page,page,count,size,sha,f"https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_{number}.pdf",headline,dateline):
            raise ValueError("R73: source, page or headline altered")
        if (p["review_status"],p["full_page_visual_columns_reviewed"],p["conde_ba_reference_found"],p["fragment_sphere_or_fall_in_brazil_found"],p["independent_event_time_literal"],p["independent_witness"],p["orbital_observation_of_528_or_637"],p["source_credit_literal"]) != ("LIDO_SEM_MENCAO",True,False,False,None,None,False,"(FP)"):
            raise ValueError("R73: event/witness or status promoted")
        if number=="00473" and "Explorer 18" not in p["previous_ledger_correction"]:
            raise ValueError("R73: prior Explorer 1 reading not corrected")
        if "Conde/BA" in p["other_content"] or "19h30" in p["space_article_classification"]:
            raise ValueError("R73: unreviewed article claim")
    nasa=data["external_crosscheck"]
    if set(nasa)!={"source","release_date","url","original_page","finding","nasa_nssdc_url","actual_launch_date","cospar","identity"}:
        raise ValueError("R73: NASA citation keys altered")
    if (nasa["source"],nasa["release_date"],nasa["original_page"],nasa["actual_launch_date"],nasa["cospar"])!=("NASA News Release 63-249","1963-11-10",1,"1963-11-27","1963-046A"):
        raise ValueError("R73: NASA identity altered")
    if len(data["limitations"])!=4 or any(not isinstance(s,str) for s in data["limitations"]):
        raise ValueError("R73: limitations altered")
    return True

def replay(pdf_dir):
    for edition,(date,page,count,size,sha,headline,dateline) in EXPECTED.items():
        source=pdf_dir/(edition+".pdf")
        if not source.is_file() or source.stat().st_size!=size:
            raise ValueError("R73: original missing/wrong length "+edition)
        h=hashlib.sha256()
        with source.open("rb") as f:
            for block in iter(lambda:f.read(1024*1024),b""):
                h.update(block)
        if h.hexdigest()!=sha:
            raise ValueError("R73: source SHA differs "+edition)
        info=subprocess.run(["pdfinfo",str(source)],capture_output=True,check=True,text=True).stdout
        if int(next(line.split(":")[1] for line in info.splitlines() if line.startswith("Pages:")))!=count:
            raise ValueError("R73: page count differs "+edition)
    return True

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--replay-dir",type=Path)
    args=parser.parse_args()
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    if args.replay_dir: replay(args.replay_dir)
    print("R73 PASS: two page-level reviews; no global newspaper negative")
