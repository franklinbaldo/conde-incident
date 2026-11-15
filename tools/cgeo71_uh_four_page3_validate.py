"""CGEO-71: article boundaries and strict page-limited negative evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"research/editorial"
names=["cgeo71_uh_four_page3_20261115.json","cgeo65_uh_bn_inventory_20261115.json",
       "cgeo66_uh_cover_dates_20261115.json","cgeo64_null_narrative_prereg_20261114.json",
       "cgeo69_uh_four_frontpages_20261115.json","cgeo70_uh_four_internal_pages_20261115.json"]
EXPECTED={
 "00442":("1963-10-09","CONTROL_OCT07","F01_METAL_SPHERE","RECIFE_INDUSTRY",
          "Industry item refers to metalworkers, not to a metallic sphere."),
 "00447":("1963-10-14","CONTROL_OCT14","F04_WINDOWS","VATICAN_NEWS",
          "Pope Paul VI addresses pilgrims near the windows of his Vatican apartment; ordinary architectural windows."),
 "00455":("1963-10-22","CONTROL_OCT21","F06_HUMAN_BODY","EDUCATION_NEWS",
          "Corpo docente means school teaching staff, not a human body found in a sphere."),
 "00467":("1963-11-04","TARGET_NOV04","F06_HUMAN_BODY","VIETNAM_FUNERAL",
          "The burial of Ngo Dinh Diem and his brother in a Saigon wire report is unrelated to a body reportedly found in Conde.")
}
METHOD='Original BN PDFs reverified on Ifro by full SHA-256; PDF page 3 rendered at 1700 pixels, whole-page visual inspection including all four quadrants with embedded text checked as auxiliary search leads. Confirm only same-article composite FBIS motifs and distinguish article genre from lexical coincidences. Page renderings are derivative views of the four pinned PDFs, never additional independent sources.'
BIAS='The page number 3 is fixed equally across four dates already chosen in CGEO-69, reducing post-hoc lexical targeting. The dates themselves are a convenience subset of preregistered slots: NOT a random or representative sample; page-level negatives MUST NOT be extrapolated to editions, weeks or newspapers. No other pages counted this round.'
PAGE_FIELDS={'whole_issue_read', 'source_sha256', 'genre', 'review', 'selection', 'publication', 'pdf_page', 'confirmed_article_counts', 'week', 'independent_conde_witness', 'lexical_adjudication', 'date', 'issue_id', 'source_url'}
def require(cond,msg):
    if not cond: raise ValueError(msg)
def load():
    return [json.loads((ROOT/n).read_text(encoding="utf8")) for n in names]
def validate(d, inv, covers, pre, old69, old70):
    require((d.get("id"),d.get("type"))==("CGEO-71","HistoricalPressFrozenWeekFixedPageAudit"),"id/type")
    require(d.get("prereg_blob_sha")=="0d13d9359080699e5f8402ca9b7014d7f1f6d59a","immutable prereg")
    require([pre["id"],inv["id"],covers["id"],old69["id"],old70["id"]]==["CGEO-64","CGEO-65","CGEO-66","CGEO-69","CGEO-70"],"lineage")
    require(d["prior_audit_paths"]==[
      "research/editorial/cgeo69_uh_four_frontpages_20261115.json",
      "research/editorial/cgeo70_uh_four_internal_pages_20261115.json"],"prior paths")
    require(d["method"]==METHOD,"exact inspected method; no free-text claims")
    require(d["selection_bias"]==BIAS,"exact selection caveat; no free-text claims")
    require("full SHA-256" in d["method"] and "all four quadrants" in d["method"],"inspection")
    require("NOT a random or representative sample" in d["selection_bias"] and
            "MUST NOT be extrapolated" in d["selection_bias"],"sampling limitation")
    pins={x["id"]:x for x in inv["issues"] if x["status"]=="PDF_BYTES_ACQUIRED"}
    dates={x["issue_id"]:x["date"] for x in covers["cover_dates"]}
    slots={(x["publication"],x["issue_id"]):(x["date"],x["week"]) for x in covers["slots"] if x.get("issue_id")}
    frag={x["id"] for x in pre["frozen_fbis_fragments"]}
    require(len(frag)==8,"frozen fragments")
    pages=d["pages"]
    require(len(pages)==4 and {x["issue_id"] for x in pages}==set(EXPECTED),"exactly four observations")
    earlier={(x["issue_id"],x["pdf_page"]) for obj in (old69,old70) for x in obj["pages"]}
    for x in pages:
        require(set(x)==PAGE_FIELDS,"no new page-level claims")
        id=x["issue_id"]
        date,week,fid,genre,context=EXPECTED[id]
        require((id,3) not in earlier,"duplicate denominator")
        require((x["publication"],x["date"],x["week"],x["pdf_page"])==("UH_RE",date,week,3),"date/page")
        require(dates[id]==date and slots[("UH_RE",id)]==(date,week),"predeclared slot")
        require(x["source_url"]==pins[id]["url"] and
                x["source_sha256"]==pins[id]["sha256"] and pins[id]["pages"]>=3,"source pin")
        require((x["review"],x["selection"],x["genre"])==(
             "FULL_PAGE_VISUAL_FOUR_QUADRANTS_TEXT_LAYER_AUXILIARY",
             "FIXED_PDF_PAGE_3_IN_EACH_WEEK",genre),"page method")
        require(x["lexical_adjudication"]=={
                "fragment_or_context":fid,"context":context,"fbis_composite_match":False},
                "false cognate boundary")
        counts=x["confirmed_article_counts"]
        require(set(counts)==frag and all(type(v) is int and v==0 for v in counts.values()),"scoped counts")
        require(x["whole_issue_read"] is False and x["independent_conde_witness"] is False,"witness/issue")
    require(d["coverage"]=={
        "new_fixed_page3_fully_reviewed":4,"prior_cgeo69_pages":4,"prior_cgeo70_pages":4,
        "total_distinct_pages_scoped":12,
        "pages_by_week_scoped":{k:3 for k in (
           "CONTROL_OCT07","CONTROL_OCT14","CONTROL_OCT21","TARGET_NOV04")},
        "whole_issues_read":0,"jb_pages_read":0,"predeclared_slots_changed":0,
        "full_corpus_baseline_rate":None,"first_pre_event_occurrence":None,
        "general_verdict":"UNDETERMINED"},"coverage denominator")
    require(d["lineage_and_limits"]=={
       "distinct_publication_lineages":1,"same_article_republications_authenticated":0,
       "independent_conde_witness_found":False,"source_hour_of_event_found":False,
       "not_all_pages_of_any_issue_inspected":True,"historical_center_1963":None,
       "orbital_constraint_activated":False,"deliberate_fraud_proven":False},"independence limits")
    require(d["interpretation"]==
        "No confirmed composite FBIS narrative motif in these four inspected pages; isolated words such as windows, body and metalworkers refer to different stories. These narrowly scoped negatives do not prove borrowing, assembly, or fraud. Narrative verdict UNDETERMINED; no independent testimony or event hour.",
        "no unreviewed interpretation")
    require(set(d)=={"type","id","date_utc","issue","prereg_path","prereg_blob_sha",
        "source_inventory_path","source_cover_crosswalk","prior_audit_paths","method",
        "selection_bias","pages","coverage","lineage_and_limits","interpretation"},"unexpected claims")
    return len(pages)
if __name__=="__main__":
    print(f"CGEO-71: {validate(*load())} new pages; 12 cumulative; UNDETERMINED")
