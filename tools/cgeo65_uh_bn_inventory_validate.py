"""CGEO-65 validates true PDF custody without promoting OCR, dates or conclusions."""
import hashlib,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
FILE=ROOT/"research/editorial/cgeo65_uh_bn_inventory_20261115.json"
BLOB="0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
URL="https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_"
# Exact reviewed-page claims are pinned independently of the inventory JSON.
EXPECTED_VISUAL = [{'id': '00452',
  'page': 1,
  'date': '1963-10-19',
  'scope': 'OUT_OF_SAMPLE',
  'note': 'Cosmos 20 headline outside frozen control windows'},
 {'id': '00470',
  'page': 1,
  'date': '1963-11-07',
  'scope': 'TARGET_NOV04',
  'note': 'cover only'},
 {'id': '00471',
  'page': 1,
  'date': '1963-11-08',
  'scope': 'TARGET_NOV04',
  'note': 'cover only'},
 {'id': '00471',
  'page': 8,
  'date': '1963-11-08',
  'scope': 'TARGET_NOV04',
  'note': 'statues in Rio Doce article; four metres OCR lead; same publication date; ordering '
          'versus FBIS unknown'}]

def validate(d,source_dir=None,blob=BLOB):
 if d["type"]!="HistoricalPressSourceInventory" or d["id"]!="CGEO-65" or d["status"]!="INVENTORY_ONLY_NOT_RATE":raise ValueError("contract")
 if blob!=BLOB or d["prereg_git_blob_sha"]!=BLOB:raise ValueError("frozen registration changed")
 ids={f"{i:05d}" for i in [*range(439,460),*range(466,473)]}
 arr=d["issues"]
 if len(arr)!=28 or {v["id"] for v in arr}!=ids:raise ValueError("issue cardinality")
 acquired=miss=pages=0
 for r in arr:
  if r["url"]!=URL+r["id"]+".pdf":raise ValueError("archive URL")
  if r["status"]=="PDF_BYTES_ACQUIRED":
   acquired+=1;pages+=r["pages"]
   if not re.fullmatch("[0-9a-f]{64}",r["sha256"]) or r["pages"]<1 or r["bytes"]<1000:raise ValueError("PDF metadata")
   if source_dir is not None:
    body=(pathlib.Path(source_dir)/("per765147_1963_"+r["id"]+".pdf")).read_bytes()
    if not body.startswith(b"%PDF") or len(body)!=r["bytes"] or hashlib.sha256(body).hexdigest()!=r["sha256"]:raise ValueError("PDF bytes differ")
  elif r["status"]=="NOT_ACQUIRED":
   miss+=1
   if r.get("http_result")!="404" or "sha256" in r or "pages" in r:raise ValueError("404 promoted")
  else:raise ValueError("unknown download status")
 if (acquired,miss,pages)!=(26,2,288):raise ValueError("custody totals changed")
 v=d["visually_reviewed_pdf_pages"]
 if v!=EXPECTED_VISUAL:raise ValueError("visually reviewed page assertion drift")
 c=d["coverage"]
 if (c["predeclared_date_vehicle_slots"],c["archive_issues_attempted"],c["original_pdfs_acquired"],c["http404_files"],c["pages_in_acquired_pdfs"],c["pages_fully_inspected_for_rates"])!=(50,28,26,2,288,0):raise ValueError("denominator inflation")
 if c["articles_confirmed_by_protocol"] is not None or c["control_baseline_rates"] is not None:raise ValueError("OCR counted")
 o=d["conclusion"]
 if o["general"]!="UNDETERMINED" or o["first_pre_event_occurrence"] is not None or o["per_fragment"] is not None or o["center_1963"] is not None or o["orbital_constraint"] or o["fraud"]:raise ValueError("invented verdict")
 return acquired,pages
if __name__=="__main__":
 d=json.loads(FILE.read_text())
 actual=subprocess.check_output(["git","hash-object",str(ROOT/d["prereg_path"])],text=True).strip()
 print("CGEO-65:",validate(d,sys.argv[1] if len(sys.argv)>1 else None,actual),"original PDF hash validation" if len(sys.argv)>1 else "offline schema only")
