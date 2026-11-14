"""Source-locked custody for a 1965 INTEROBS paper; never promote a different satellite."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/tle_custody/konkoly_interobs_1963_C241-LONTRA-R38.json'
URL = 'https://webarch.konkoly.hu/mitteilungen/Mitt059/059.html'
SHA = '70a0e99bf61528d28b48f583295a4984ae2b9056595d1bb9d7a626a61a47ebe5'


def require(condition, constraint):
    """Custody checks must run under python -O and PYTHONOPTIMIZE."""
    if not condition:
        raise ValueError(f'C241-LONTRA-R38: invalid {constraint}')


def validate(d, original=None):
    require(d['schema'] == 'conde.contemporary_satellite_tracking_bibliography/v1', 'manifest schema')
    require(d['id'] == 'C241-LONTRA-R38' and d['audit_date'] == '2026-11-13', 'catalog identifier and audit date')
    require(d['status'] == 'CONTEMPORARY_OBSERVATIONS_OF_ANOTHER_OBJECT_NOT_527_528_529', 'non-target study classification')
    s = d['source']
    require(s['url'] == URL and s['publication_year'] == 1965 and s['number'] == 59, 'bibliographic source identity')
    require(s['http_status'] == 200 and s['tls_validated'] is True, 'HTTP and TLS provenance')
    require(s['bytes'] == 57146 and s['sha256'] == SHA, 'source bytes and sha256')
    require(s['original_print_facsimile_retrieved'] is False, 'facsimile has not been retrieved')
    require(s['original_station_logs_retrieved'] is False, 'station logs have not been retrieved')
    require('transcribed HTML' in s['web_format'], 'HTML transcription format')
    study = d['study']
    require(study['object_designation'] == '1960 epsilon 3 (Sputnik 4 cabin)', 'Sputnik 4 designation')
    require(study['object_is_1963_003_abc'] is False, 'not the 1963-003 objects')
    require(study['reported_observation_windows'] == [
        '1963-08-21/1963-08-30', '1964-02-17', '1964-04-10/1964-04-13',
        '1964-06-08/1964-06-13', '1964-07-07/1964-07-12', '1964-09-18/1964-09-27'], 'campaign observation windows')
    require(study['campaign_includes_1963_nov_07_to_09'] is False, 'no November 7-9 campaign in this study')
    require((study['stations_in_table_2'], study['fixes_total_in_table_2'],
            study['simultaneous_positions_used_in_study'], study['passes_considered']) == (22, 793, 393, 39), '22 stations, 793 fixes, 393 simultaneous positions, 39 passes')
    require(study['fixes_by_station_from_table_2'] == [
        {'station_code': '1023', 'place': 'Kiev', 'fixes': 29},
        {'station_code': '1113', 'place': 'Baja', 'fixes': 124},
        {'station_code': '1111', 'place': 'Budapest', 'fixes': 84}], 'station fixes by published station')
    require(study['station_counts_cover_all_study_windows_not_only_august_1963'] is True, 'station counts cover every listed campaign')
    require(study['inputs_are_from_multinational_network_not_independent_527_to_529'] is True, 'not independent tracking of NORAD 527-529')
    vol = d['original_campaign_volumes_cited_by_paper']
    require(vol['title'] == 'Ergebnisse der im Rahmen des Interobs-Programms abgehaltenen Kooperationswochen', 'cited volumes title')
    require(vol['volumes'] == [1, 2] and vol['publication_years'] == [1964, 1965], 'cited volumes and publication years')
    require(vol['citation_number_in_paper'] == 7 and vol['place_of_publication_reported'] == 'Baja, Hungary', 'volumes citation and Baja publication place')
    require(vol['full_text_of_volumes_retrieved'] is False, 'volumes full text not retrieved')
    require(vol['whether_november_1963_is_covered'] is None, 'volumes November coverage unknown')
    require(vol['whether_norad_527_528_529_appear'] is None, 'volumes NORAD coverage unknown')
    lim = d['limits']
    for name in ['target_observations_identified', 'november_1963_campaign_confirmed',
                 'source_html_is_original_print_facsimile', 'raw_station_observations_accessed',
                 'outreach_sent']:
        require(lim[name] is False, 'no target claim or outreach')
    require(lim['orbital_constraints_activated'] == lim['new_target_orbital_measurements'] == 0, 'zero activated orbital constraints and measurements')
    require('1963-11-07' in d['follow_up'] and '1963-11-09' in d['follow_up'], 'follow-up dates')
    if original is not None:
        b = Path(original).read_bytes()
        require(len(b) == 57146 and hashlib.sha256(b).hexdigest() == SHA, 'retrieved HTML bytes and SHA')
        t = b.decode('latin1')
        # Replay the actual HTML, not a fabricated JSON tally or an OCR-only snippet.
        for pat in [r'Kiev\s+U\.S\.S\.R\.\s+1023\s+29',
                    r'Baja\s+Hungary\s+1113\s+124',
                    r'Budapest\s+Hungary\s+1111\s+84',
                    r'Total:\s+22 stations\s+793 fixes',
                    r'Total:\s+39 transits\s+393 simultaneous points',
                    r'21-30 Aug\. 1963',
                    r'\[7\] Ergebnisse der im Rahmen des Interobs-Programms abgehaltenen Kooperationswochen',
                    r'1960 epsilon3']:
            require(re.search(pat, t, re.S), pat)
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--html-original', type=Path)
    args = p.parse_args()
    validate(json.loads(MANIFEST.read_text(encoding='utf-8')), args.html_original)
    print('C241-LONTRA-R38: provenance and target separation PASS')


if __name__ == '__main__':
    main()
