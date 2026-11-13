"""Fail-closed documentary checks for station 1023 museum route C241-LONTRA-R37."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/tle_custody/kyiv_station1023_archive_C241-LONTRA-R37.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(d, html_paths=()):
    require(d['schema'] == 'conde.historical_station_archive_route/v1', 'C241-LONTRA-R37 custodial invariant 1 violated')
    require(d['id'] == 'C241-LONTRA-R37', 'C241-LONTRA-R37 custodial invariant 2 violated')
    require(d['audit_date'] == '2026-11-13', 'C241-LONTRA-R37 custodial invariant 3 violated')
    require(d['status'] == 'ARCHIVE_COLLECTION_LOCATED_IN_RETROSPECTIVE_PUBLICATION_ONLY', 'C241-LONTRA-R37 custodial invariant 4 violated')
    require(len(d['sources']) == 4, 'C241-LONTRA-R37 custodial invariant 5 violated')
    for i, (url, n, sha) in enumerate([
        ('https://observ.knu.ua/museum/publikatsiyi/', 72900, 'de14cfaedd29663591e050f8544499a50f0a621ad0d1bc1cadc5d0e85d847286'),
        ('https://observ.knu.ua/museum/fondi-muzeyu/', 41555, 'e4f569c4e9c7bc3992fbafedb3b3b3693fee3680f49fddc6c5bcc58a60eb5071'),
    ]):
        s = d['sources'][i]
        require(s['url'] == url and s['http_status'] == 200 and s['tls_validated'] is True, 'C241-LONTRA-R37 custodial invariant 6 violated')
        require(s['bytes'] == n and s['sha256'] == sha, 'C241-LONTRA-R37 custodial invariant 7 violated')
        if html_paths:
            b = Path(html_paths[i]).read_bytes()
            require(len(b) == n and hashlib.sha256(b).hexdigest() == sha, 'C241-LONTRA-R37 custodial invariant 8 violated')
            if i == 0:
                require('ФЕНОМЕН СТАНЦІЇ № 1023'.encode('utf-8') in b, 'C241-LONTRA-R37 custodial invariant 9 violated')
                require('2007' in b.decode('utf-8'), 'C241-LONTRA-R37 custodial invariant 10 violated')
            else:
                require('Фонди музею'.encode('utf-8') in b, 'C241-LONTRA-R37 custodial invariant 11 violated')
    require(d['sources'][2]['url'] == 'https://viv.nuou.org.ua/article/download/281444/275680/648790', 'C241-LONTRA-R37 custodial invariant 12 violated')
    require(d['sources'][2]['doi'] == '10.33099/2707-1383-2022-45-3-104-127', 'C241-LONTRA-R37 custodial invariant 13 violated')
    require(d['sources'][2]['printed_pages_checked_visually'] == [116, 118], 'C241-LONTRA-R37 custodial invariant 14 violated')
    require(d['sources'][3]['url'] == 'https://www.mao.kiev.ua/biblio/jscans/svitogliad/svit-2007-07-5/svit-2007-07-5-28-kazanceva.pdf', 'C241-LONTRA-R37 custodial invariant 15 violated')
    for s in d['sources'][2:]:
        require(s['web_pdf_rendered'] is True, 'C241-LONTRA-R37 custodial invariant 16 violated')
        require(s['direct_download_http_status_in_executor'] == 403, 'C241-LONTRA-R37 custodial invariant 17 violated')
        require(s['bytes'] is None and s['sha256'] is None, 'C241-LONTRA-R37 custodial invariant 18 violated')
    st = d['station']
    require(st['identifier'] == '1023' and st['place'] == 'Kyiv, Ukrainian SSR', 'C241-LONTRA-R37 custodial invariant 19 violated')
    require(st['program'] == 'Kosmos', 'C241-LONTRA-R37 custodial invariant 20 violated')
    require(st['regular_operational_years_reported'] == [1957, 1983], 'C241-LONTRA-R37 custodial invariant 21 violated')
    require(st['reported_ephemerides_received_all_years'] == 93165, 'C241-LONTRA-R37 custodial invariant 22 violated')
    require(st['reported_positions_measured_all_years'] == 77134, 'C241-LONTRA-R37 custodial invariant 23 violated')
    require(st['counts_are_not_1963_counts'] is True, 'C241-LONTRA-R37 custodial invariant 24 violated')
    require(st['museum_report_collection_fig3_page'] == 116, 'C241-LONTRA-R37 custodial invariant 25 violated')
    require(st['museum_archive_cited_for_1976_report'] == 'fond SSHSZ, file 06-03-02, Station 1023 report 1976, 32 sheets', 'C241-LONTRA-R37 custodial invariant 26 violated')
    require(st['archive_1976_is_not_archive_1963'] is True, 'C241-LONTRA-R37 custodial invariant 27 violated')
    require(st['unknown_object_observations_reported'] is True, 'C241-LONTRA-R37 custodial invariant 28 violated')
    require(st['unknown_objects_are_not_identified_as_norad_targets'] is True, 'C241-LONTRA-R37 custodial invariant 29 violated')
    require(st['kft_phototheodolite_not_1963_evidence'] is True, 'C241-LONTRA-R37 custodial invariant 30 violated')
    limits = d['limits']
    for key in ['original_1963_reports_retrieved', 'current_custody_in_2026_confirmed',
                'observation_for_norad_527_528_529_confirmed',
                'all_year_counts_usable_as_1963_measurements', 'outreach_sent']:
        require(limits[key] is False, 'C241-LONTRA-R37 custodial invariant 31 violated')
    require(limits['new_independent_orbital_measurements'] == 0, 'C241-LONTRA-R37 custodial invariant 32 violated')
    require(limits['orbital_constraints_activated'] == 0, 'C241-LONTRA-R37 custodial invariant 33 violated')
    require('1963-11-07' in d['follow_up'] and '1963-11-09' in d['follow_up'], 'C241-LONTRA-R37 custodial invariant 34 violated')
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--html-publications', type=Path)
    p.add_argument('--html-holdings', type=Path)
    a = p.parse_args()
    require(bool(a.html_publications) == bool(a.html_holdings), 'Both HTML source paths required together')
    validate(json.loads(MANIFEST.read_text(encoding='utf-8')),
             (a.html_publications, a.html_holdings) if a.html_publications else ())
    print('C241-LONTRA-R37: provenance boundaries PASS')


if __name__ == '__main__':
    main()
