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


def validate(d, original=None):
    assert d['schema'] == 'conde.contemporary_satellite_tracking_bibliography/v1'
    assert d['id'] == 'C241-LONTRA-R38' and d['audit_date'] == '2026-11-13'
    assert d['status'] == 'CONTEMPORARY_OBSERVATIONS_OF_ANOTHER_OBJECT_NOT_527_528_529'
    s = d['source']
    assert s['url'] == URL and s['publication_year'] == 1965 and s['number'] == 59
    assert s['http_status'] == 200 and s['tls_validated'] is True
    assert s['bytes'] == 57146 and s['sha256'] == SHA
    assert s['original_print_facsimile_retrieved'] is False
    assert s['original_station_logs_retrieved'] is False
    assert 'transcribed HTML' in s['web_format']
    study = d['study']
    assert study['object_designation'] == '1960 epsilon 3 (Sputnik 4 cabin)'
    assert study['object_is_1963_003_abc'] is False
    assert study['reported_observation_windows'] == [
        '1963-08-21/1963-08-30', '1964-02-17', '1964-04-10/1964-04-13',
        '1964-06-08/1964-06-13', '1964-07-07/1964-07-12', '1964-09-18/1964-09-27']
    assert study['campaign_includes_1963_nov_07_to_09'] is False
    assert (study['stations_in_table_2'], study['fixes_total_in_table_2'],
            study['simultaneous_positions_used_in_study'], study['passes_considered']) == (22, 793, 393, 39)
    assert study['fixes_by_station_from_table_2'] == [
        {'station_code': '1023', 'place': 'Kiev', 'fixes': 29},
        {'station_code': '1113', 'place': 'Baja', 'fixes': 124},
        {'station_code': '1111', 'place': 'Budapest', 'fixes': 84}]
    assert study['station_counts_cover_all_study_windows_not_only_august_1963'] is True
    assert study['inputs_are_from_multinational_network_not_independent_527_to_529'] is True
    vol = d['original_campaign_volumes_cited_by_paper']
    assert vol['title'] == 'Ergebnisse der im Rahmen des Interobs-Programms abgehaltenen Kooperationswochen'
    assert vol['volumes'] == [1, 2] and vol['publication_years'] == [1964, 1965]
    assert vol['citation_number_in_paper'] == 7 and vol['place_of_publication_reported'] == 'Baja, Hungary'
    assert vol['full_text_of_volumes_retrieved'] is False
    assert vol['whether_november_1963_is_covered'] is None
    assert vol['whether_norad_527_528_529_appear'] is None
    lim = d['limits']
    for name in ['target_observations_identified', 'november_1963_campaign_confirmed',
                 'source_html_is_original_print_facsimile', 'raw_station_observations_accessed',
                 'outreach_sent']:
        assert lim[name] is False
    assert lim['orbital_constraints_activated'] == lim['new_target_orbital_measurements'] == 0
    assert '1963-11-07' in d['follow_up'] and '1963-11-09' in d['follow_up']
    if original is not None:
        b = Path(original).read_bytes()
        assert len(b) == 57146 and hashlib.sha256(b).hexdigest() == SHA
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
            assert re.search(pat, t, re.S), pat
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--html-original', type=Path)
    args = p.parse_args()
    validate(json.loads(MANIFEST.read_text(encoding='utf-8')), args.html_original)
    print('C241-LONTRA-R38: provenance and target separation PASS')


if __name__ == '__main__':
    main()
