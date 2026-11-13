"""Audit NOAA station-history excerpts without backdating later instrumentation.

Reproduce with --check; supply --metadata-original and --sonde-original
for an optional full-archive SHA and excerpt identity check (no network).
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research' / 'meteorology'
CARD = BASE / 'igra_recife_1963_station_history_gap.json'
META_EXCERPT = BASE / 'igra_recife_1963_station_history_excerpt.txt'
SONDE_EXCERPT = BASE / 'igra_recife_1963_sonde_code_excerpt.txt'
METADATA_SHA = 'fe1a0b23614306d453728ba499e48ac4efa180956b8f222c55eb1adcfedf68f7'
SONDE_SHA = 'e72e594b8f1c2ce3543e997e5bec0ca0a13d72d41b91197fa16325a1436af0fe'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def parse_metadata(row):
    assert row[:11] == 'BRM00082900'
    assert len(row) >= 235
    data = {
        'wmo_id': int(row[12:17]),
        'station_name': row[18:48].strip(),
        'latitude_deg': float(row[51:60]),
        'longitude_deg': float(row[63:72]),
        'station_elevation_m': float(row[75:81]),
        'event_year': int(row[84:88]),
        'event_month': int(row[89:91]),
        'event_day': int(row[92:94]),
        'event_hour_utc': int(row[95:97]),
        'uncertain_date_flag': int(row[98]),
        'event_type': row[100:119].strip(),
        'information_prior_or_static': row[123:163].strip(),
        'information_after': row[168:208].strip() or None,
        'reference': row[210:235].strip(),
        'row_sha256': sha(row.encode('ascii')),
    }
    assert data['event_type'] in ('USING SONDE MODEL', 'USING RADIAT. CORR.')
    assert data['event_year'] >= 1982
    return data

def derive():
    meta_rows=META_EXCERPT.read_bytes().splitlines()
    sonde_rows=SONDE_EXCERPT.read_bytes().splitlines()
    assert len(meta_rows)==12 and len(sonde_rows)==12
    metadata=[parse_metadata(r.decode('ascii')) for r in meta_rows]
    sonde=[]
    for r in sonde_rows:
        parts=r.decode('ascii').split()
        assert parts[0]=='BRM00082900' and len(parts)==10
        sonde.append({'from_utc': f'{parts[1]}-{parts[2]}-{parts[3]}T{parts[4]}:00Z',
                     'to_utc': f'{parts[5]}-{parts[6]}-{parts[7]}T{parts[8]}:00Z',
                     'instrument_code':int(parts[9]),
                     'row_sha256':sha(r)})
    assert min(int(r['from_utc'][:4]) for r in sonde)==2000
    return {
      'schema':'conde.igra-recife-station-history-gap/v1',
      'id':'LAG-IGRA-RECIFE-HISTORY-GAP-1963-01',
      'source':{
       'metadata_url':'https://www.ncei.noaa.gov/pub/data/igra/history/igra2-metadata.txt',
       'metadata_readme_url':'https://www.ncei.noaa.gov/pub/data/igra/history/igra2-metadata-readme.txt',
       'metadata_full_sha256':METADATA_SHA,
       'metadata_full_bytes':6595873,
       'sonde_url':'https://www.ncei.noaa.gov/pub/data/igra/history/wmo-sonde-history.txt',
       'sonde_format_url':'https://www.ncei.noaa.gov/pub/data/igra/history/wmo-history-format.txt',
       'sonde_full_sha256':SONDE_SHA,
       'sonde_full_bytes':8252302,
       'metadata_excerpt_sha256':sha(META_EXCERPT.read_bytes()),
       'sonde_excerpt_sha256':sha(SONDE_EXCERPT.read_bytes()),
       'readme_last_updated':'2023-01-19',
       'retrieval_date_utc':'2026-11-13',
       'metadata_archive_last_modified_utc':'2026-07-15',
       'institution':'NOAA/NCEI',
       'metadata_lineage':'historical catalog; Gaffen (1996) for IGRA 2; sources listed per row',
       'independent_sounding_measurement':False
      },
      'event_records':metadata,
      'sonde_code_intervals':sonde,
      'conclusions':{
       'historical_target_nominal_dates_utc':['1963-11-07','1963-11-08','1963-11-09'],
       'count_station_events':12,
       'station_event_year_range':[min(r['event_year'] for r in metadata),max(r['event_year'] for r in metadata)],
       'original_wmo_ids_in_later_records':sorted(set(r['wmo_id'] for r in metadata)),
       'sonde_code_earliest_year':2000,
       'documented_1963_instrument':None,
       'documented_1963_height_processing':None,
       'documented_1963_station_coordinates':None,
       'documented_1963_station_elevation_m':None,
       'instrumental_sigma_1963':None,
       'recife_to_conde_error':None,
       'can_backdate_1982_sonde_to_1963':False,
       'can_use_later_coordinates_as_1963_observation':False,
       'can_activate_geographic_constraint':False,
       'interpretation':'No station-history event in these NCEI sources spans or describes 1963; this is a metadata coverage gap, not evidence that no radiosonde launched in 1963.',
       'graph_links':['C149-C151 -> original p/T/GPH from ncdc6301 -> station processing and historical location unknown -> density error PENDING',
                      'C17-C23 and C193 -> independent upper-atmospheric context, not station height calibration',
                      'C144-C146 -> separate surface-chart family, not a calibrated vertical transfer to Conde']
      }
    }

def verify_original(path, excerpt, expected_sha):
    raw=path.read_bytes()
    assert sha(raw)==expected_sha, f'archive SHA mismatch: {path}'
    rows=[x for x in raw.splitlines(keepends=True) if x.startswith(b'BRM00082900')]
    assert b''.join(rows)==excerpt.read_bytes(), f'excerpt differs from {path}'

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--check', action='store_true')
    a.add_argument('--metadata-original',type=Path)
    a.add_argument('--sonde-original',type=Path)
    args=a.parse_args()
    if args.metadata_original: verify_original(args.metadata_original,META_EXCERPT,METADATA_SHA)
    if args.sonde_original: verify_original(args.sonde_original,SONDE_EXCERPT,SONDE_SHA)
    new=derive()
    rendered=json.dumps(new,indent=2,ensure_ascii=False)+'\n'
    if args.check: assert CARD.read_text()==rendered, 'generated card differs'
    else: CARD.write_text(rendered)
    print('PASS station metadata 12 records, sonde code 12 intervals, 1963 gap')
if __name__=='__main__':main()
