#!/usr/bin/env python3
"""Validate source custody and protect 1963 interpretation from catalogue chronology."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/tle_custody/zvenigorod_collection_date_audit_C241-LONTRA-R36.json'
SOURCES = (
 ('https://www.astro.bas.bg/conf_proc/book_VIIBSAC.pdf',2012,17605841,'e6b538c34a8c26056cd8d0296ae6570033eb9ff5359f932f9b6250f670e64e42','359-362'),
 ('https://www.astroplate.cz/wp-content/uploads/2014/12/astroplate_2014_proceedings.pdf',2014,8854648,'59b53f4ea48c3c9486b80aead7469b01e15307747fa085e99df04de7f08f1d70','119-122')
)
EXPECTED = {'Zeiss-400 astrograph':(1972,2005,4500),'AFU camera':(1973,1985,2800),'VAU camera':(1971,2005,10000)}

def validate(d, files=None):
    assert d['schema']=='conde.archival_collection_date_range/v1'
    assert d['id']=='C241-LONTRA-R36' and d['audit_date']=='2026-11-13'
    assert d['previous_reference']=='C241-LONTRA-R35'
    assert len(d['sources'])==len(SOURCES)
    for src, (url,year,length,digest,pages) in zip(d['sources'],SOURCES):
        assert (src['url'],src['publication_year'],src['bytes'],src['sha256'],src['printed_pages'])==(url,year,length,digest,pages)
        assert src['http_status']==200 and src['tls_validated'] is True and src['page_text_indexed'] is True
    assert d['sources'][0]['page_checked_visually'] is False
    assert d['sources'][1]['page_checked_visually'] is True
    assert d['sources'][1]['checked_pdf_pages_1based']==[126,127]
    rows=d['inventory_as_reported_in_2012']
    assert len(rows)==3
    assert {x['instrument']:(x['from_year'],x['to_year'],x['reported_units']) for x in rows}==EXPECTED
    assert all(x['from_year']>1963 for x in rows)
    counts=d['inventory_as_reported_in_2014']
    assert (counts['Zeiss_negative_count'], counts['AFU_film_count'],counts['VAU_film_count_approx'])==(3703,2683,10000)
    assert (counts['WFPDB_observatory_code'],counts['WFPDB_AFU_instrument_code'])==('ZVN','021')
    assert counts['AFU_catalogued_in_WFPDB'] is True and counts['AFU_scanning_planned'] is False
    assert d['scope']=='named_zvenigorod_plate_film_collections_only'
    assert d['conclusion']=='NO_1963_IN_DOCUMENTED_COLLECTION_YEAR_RANGES'
    assert all(v is True for v in d['does_not_establish'].values())
    assert d['orbits']=={'target_ids':[527,528,529],'new_independent_measurements':0,'orbital_constraints_activated':0}
    assert d['outreach_sent'] is False
    if files:
        for src,p in zip(d['sources'], files):
            raw=Path(p).read_bytes()
            assert len(raw)==src['bytes'] and hashlib.sha256(raw).hexdigest()==src['sha256']
            assert raw.startswith(b'%PDF-') and b'%%EOF' in raw[-2048:]
    return True

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--pdf-2012',type=Path);pa.add_argument('--pdf-2014',type=Path)
    args=pa.parse_args();pair=(args.pdf_2012,args.pdf_2014) if args.pdf_2012 and args.pdf_2014 else None
    if bool(args.pdf_2012) != bool(args.pdf_2014):pa.error('Both PDF paths required for replay')
    validate(json.loads(MANIFEST.read_text()),pair)
    print('PASS: 2012/2014 collection dates, integrity and no unjustified 1963 interpretation'+(' (PDF bytes replayed)' if pair else ' (manifest-only)'))
