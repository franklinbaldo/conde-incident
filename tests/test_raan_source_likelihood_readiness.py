"""Negative controls for source-level 528 likelihood readiness, not a fit."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from raan_source_likelihood_readiness import (  # noqa: E402
    INPUTS, OUTPUT, REQUIRED_OBSERVABLE_FIELDS, build, structural_gate, is_utc,
)


def raw_inputs():
    return tuple((ROOT / path).read_bytes() for path in INPUTS)


def mutate(raw, callback):
    payload = json.loads(raw)
    callback(payload)
    return json.dumps(payload).encode()


class SourceReadinessTests(unittest.TestCase):
    def test_exact_replay_and_hashes(self):
        raw = raw_inputs()
        output = build(*raw)
        self.assertEqual(output, json.loads((ROOT / OUTPUT).read_text()))
        self.assertEqual([h['sha256'] for h in output['input_sha256']],
                         [hashlib.sha256(b).hexdigest() for b in raw])

    def test_real_corpus_not_physical_posterior(self):
        report = build(*raw_inputs())
        self.assertEqual(report['classification'],
                         'DOCUMENTARY_FACTOR_ELIGIBILITY_AUDIT_NO_HISTORICAL_POSTERIOR')
        groups = report['candidate_groups']
        self.assertEqual(groups[0]['n_528_entries'], 45)
        self.assertEqual(groups[1]['catalog_status_day'], '1963-11-08')
        self.assertEqual(groups[2]['objects_named_in_documents'], [687, 688, 943])
        self.assertEqual(groups[2]['n_documents_about_528'], 0)
        self.assertEqual(groups[3]['n_curated_film_indices'], 15)
        self.assertEqual(groups[3]['n_with_authenticated_target_528'], 0)
        self.assertIsNone(report['independence']['number_of_independent_528_sensor_sources_in_history'])
        self.assertEqual(report['model_contract']['MCMC_historical'], 'NOT_RUN')
        self.assertFalse(report['model_contract']['active_constraint'])

    def test_frozen_holdout_membership_not_retrained(self):
        report = build(*raw_inputs())
        self.assertEqual(report['frozen_holdout']['memberships_by_partition'],
                         {'fit': 61, 'validation': 23, 'evaluation': 35})
        self.assertEqual(report['frozen_holdout']['prediction_score'], 'NOT_RUN')
        self.assertTrue(report['frozen_holdout']['same_secondary_source_family_across_all_partitions'])

    def test_raan_numeric_changes_do_not_create_sensor(self):
        raw = list(raw_inputs())
        original = build(*raw)
        raw[2] = mutate(raw[2], lambda p: p['records'][0].__setitem__('raan_deg', 300.0))
        result = build(*raw)
        self.assertEqual([g.get('factor_eligibility') for g in result['candidate_groups']],
                         [g.get('factor_eligibility') for g in original['candidate_groups']])
        self.assertNotEqual(result['input_sha256'][2]['sha256'],
                            original['input_sha256'][2]['sha256'])

    def test_688_is_not_528_and_false_attribution_fails(self):
        raw = list(raw_inputs())
        raw[0] = mutate(raw[0], lambda p:
                        p['records'][1]['object_ids_reported_in_this_document'].append(528))
        with self.assertRaisesRegex(ValueError, 'object/chronology drift'):
            build(*raw)

    def test_1964_is_not_1963_despite_catalog_claim(self):
        raw = list(raw_inputs())
        raw[0] = mutate(raw[0], lambda p: p['records'][4].__setitem__(
            'source_date', '1963-11-30'))
        with self.assertRaisesRegex(ValueError, 'object/chronology drift'):
            build(*raw)

    def test_duplicates_cannot_be_independent_primary_documents(self):
        raw = list(raw_inputs())
        raw[0] = mutate(raw[0], lambda p: p['records'][4].__setitem__(
            'source_id', p['records'][3]['source_id']))
        with self.assertRaises(ValueError):
            build(*raw)

    def test_new_film_target_requires_manual_reassessment(self):
        raw = list(raw_inputs())
        raw[1] = mutate(raw[1], lambda p: p['film_index_entries'][0].__setitem__(
            'object_catalog_id', 528))
        with self.assertRaisesRegex(ValueError, 'new evidence'):
            build(*raw)

    def test_archive_index_is_not_negative_detection(self):
        report = build(*raw_inputs())
        self.assertIn('not evidence that the object was never observed',
                      report['scope_limit'])
        self.assertIn('TARGET_ID', report['candidate_groups'][3]['blockers'])

    def test_frozen_epoch_leakage_is_rejected(self):
        raw = list(raw_inputs())
        raw[3] = mutate(raw[3], lambda p: p['memberships']['527']['evaluation'].extend(
            p['memberships']['527']['fit'][:1]))
        with self.assertRaisesRegex(ValueError, 'holdout leakage'):
            build(*raw)

    def test_holdout_cross_partition_swap_is_rejected(self):
        # Synthetic adversary: membership, deduplication, and counts stay intact.
        # The swapped Oct epoch must not be allowed into August validation.
        raw = list(raw_inputs())
        split = json.loads(raw[3])
        member = split['memberships']['528']
        member['validation'][0], member['evaluation'][0] = (
            member['evaluation'][0], member['validation'][0])
        raw[3] = json.dumps(split).encode()
        with self.assertRaisesRegex(ValueError, 'holdout leakage: temporal boundary'):
            build(*raw)

    def test_declared_holdout_boundary_drift_is_rejected(self):
        raw = list(raw_inputs())
        raw[3] = mutate(raw[3], lambda split: split['boundaries'].__setitem__(
            'evaluation_from_utc', '1963-11-01T00:00:00Z'))
        with self.assertRaisesRegex(ValueError, 'holdout temporal boundary'):
            build(*raw)

    def test_secondary_epoch_drift_is_rejected(self):
        raw = list(raw_inputs())
        raw[2] = mutate(raw[2], lambda p: p['records'][0].__setitem__(
            'epoch_utc', '1964-01-01T00:00:00Z'))
        with self.assertRaisesRegex(ValueError, 'secondary epoch'):
            build(*raw)

    def test_annual_group_is_not_528_survival_or_perigee(self):
        report = build(*raw_inputs())
        groups = {g['name']: g for g in report['candidate_groups']}
        annual = groups['NASA_SP4004_1963_LAUNCH_GROUP']
        self.assertEqual(annual['printed_group_status'], 'Still in orbit.')
        self.assertEqual(annual['printed_perigee_statute_miles'], 286)
        self.assertEqual(annual['printed_page'], 502)
        self.assertEqual(annual['group_period_minutes_printed'], '94.6')
        self.assertNotIn('VISUAL_TRANSCRIPTION', annual['blockers'])
        self.assertIsNone(annual['child_528_status_from_this_row'])
        self.assertIsNone(annual['child_528_perigee_from_this_row'])
        self.assertFalse(report['model_contract']['active_constraint'])

    def test_annual_group_cannot_be_promoted_to_528(self):
        raw = list(raw_inputs())
        raw[6] = mutate(raw[6], lambda p: p['annual_row_extracted_text'].__setitem__(
            'child_piece_identifier', '1963 3B'))
        with self.assertRaisesRegex(ValueError, 'group/child'):
            build(*raw)

    def test_annual_report_does_not_claim_visual_confirmation(self):
        raw = list(raw_inputs())
        raw[6] = mutate(raw[6], lambda p: p['publication'].__setitem__(
            'page_image_verified', False))
        with self.assertRaisesRegex(ValueError, 'documentary source'):
            build(*raw)

    def test_annual_ocr_false_neighbor_name_fails_closed(self):
        raw = list(raw_inputs())
        raw[6] = mutate(raw[6], lambda p: p["annual_row_extracted_text"].__setitem__(
            "name_printed", "DOD Probe"))
        with self.assertRaisesRegex(ValueError, "group/child"):
            build(*raw)

    def test_annual_status_changed_requires_reassessment(self):
        raw = list(raw_inputs())
        raw[6] = mutate(raw[6], lambda p: p['annual_row_extracted_text'].__setitem__(
            'status_printed', 'Decayed.'))
        with self.assertRaisesRegex(ValueError, 'group/child'):
            build(*raw)

    def test_gcat_labels_cannot_create_sensor_independence(self):
        report = build(*raw_inputs())
        gcat = {g['name']: g for g in report['candidate_groups']}[
            'GCAT_MODERN_COMPILED_PIECE_LABELS']
        self.assertIsNone(gcat['physical_piece'])
        self.assertEqual(gcat['cospar'], '1963-003B')
        self.assertIn('PRIMARY_INSTRUMENT_RECORD', gcat['blockers'])
        self.assertEqual(report['independence'][
            'number_of_independent_528_sensor_sources_identified_in_inputs'], 0)

    def test_gcat_false_independence_must_be_reassessed(self):
        raw = list(raw_inputs())
        raw[5] = mutate(raw[5], lambda p: p['edges'][0].__setitem__(
            'independent_observation', True))
        with self.assertRaisesRegex(ValueError, 'GCAT'):
            build(*raw)

    def test_gcat_physical_identity_claim_must_be_reassessed(self):
        raw = list(raw_inputs())
        raw[5] = mutate(raw[5], lambda p: p['catalogue_labels']['00528'].__setitem__(
            'physical_piece', 'UNVERIFIED_TEST_LABEL'))
        with self.assertRaisesRegex(ValueError, 'GCAT'):
            build(*raw)

    def test_structural_future_contract_not_authentication(self):
        candidate = dict.fromkeys(REQUIRED_OBSERVABLE_FIELDS, 'EXAMPLE_NOT_HISTORICAL')
        candidate.update(norad=528, observation_epoch_utc='1963-11-08T10:00:00Z')
        result = structural_gate(candidate)
        self.assertTrue(result['structurally_complete'])
        self.assertEqual(result['historical_authenticity'], 'NOT_ASSESSED')
        self.assertEqual(result['independent_likelihood_factor'], 'NOT_AUTHORIZED')
        incomplete = copy.deepcopy(candidate)
        incomplete['measurement_error_model_ref'] = None
        incomplete['observation_epoch_utc'] = '1963-11-08T10:00:00'
        result = structural_gate(incomplete)
        self.assertFalse(result['structurally_complete'])
        self.assertIn('measurement_error_model_ref', result['blockers'])
        self.assertIn('observation_epoch_utc', result['blockers'])
        self.assertEqual(structural_gate({**candidate, 'norad': 688})['blockers'],
                         ['OBJECT_NOT_528'])
        self.assertFalse(is_utc('1963-11-08T10:00:00+02:00'))


if __name__ == '__main__':
    unittest.main()
