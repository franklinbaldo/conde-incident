#!/usr/bin/env python3
"""Derived reverse source/occurrence locator; no new evidentiary authority."""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITATIONS = Path('public/data/conde-source-citations.json')
LINEAGE = Path('public/data/conde-declared-dependence.json')
EVIDENCE = Path('public/data/conde-evidence-index-manifest.json')
MATRIX = Path('research/evidence_matrix_C001-C238_2026-11-11.md')
POINTER = Path('public/data/conde-source-lookup-manifest.json')
DIR = Path('public/data/conde-source-lookup')
NAME = re.compile(r'part-[a-f0-9]{64}\.json\Z')
MAX_BYTES = 20_000


def fail_if(condition, message):
    if condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode('utf-8')


def build(root=ROOT):
    inputs = {path: (root / path).read_bytes()
              for path in (CITATIONS, LINEAGE, EVIDENCE, MATRIX)}
    citations, lineage, evidence = [json.loads(inputs[p])
                                    for p in (CITATIONS, LINEAGE, EVIDENCE)]
    fail_if(evidence['matrix_source']['sha256'] != digest(inputs[MATRIX]),
            'Matrix does not match evidence manifest')
    fail_if(evidence['matrix_git_blob_sha1'] != citations['matrix_git_blob_sha1']
            or citations['matrix_git_blob_sha1'] != lineage['matrix_git_blob_sha1'],
            'Matrix identity differs between sources')
    expected_source = {str(CITATIONS): digest(inputs[CITATIONS]),
                       str(LINEAGE): digest(inputs[LINEAGE])}
    fail_if({s['path']: s['sha256'] for s in evidence['source_files']}
            != expected_source, 'Source digest differs from evidence manifest')
    fail_if(citations['curated_occurrences'] + citations['unmapped_occurrences']
            != citations['total_matrix_occurrences'],
            'Source coverage contradicts matrix total')

    references = citations['records']
    lineage_rows = lineage['citation_lineages']
    key = lambda row: (row['snapshot_ref'], row['source_id'])
    source_keys = [key(r) for r in references]
    lineage_keys = [key(r) for r in lineage_rows]
    fail_if(len(set(source_keys)) != len(source_keys)
            or len(set(lineage_keys)) != len(lineage_keys)
            or set(source_keys) != set(lineage_keys),
            'Non-bijective source-to-lineage citation mapping')
    by_key = {key(r): r for r in lineage_rows}
    matrix_lines = inputs[MATRIX].decode('utf-8').splitlines()
    grouped = defaultdict(list)
    for row in references:
        family, source = row['source_family'], row['source_id']
        dep = by_key[key(row)]
        fail_if(dep['family_id'] != family or dep['row_sha256'] != row['row_sha256']
                or dep['matrix_line'] != row['matrix_line'],
                'Lineage citation identity or row digest differs')
        i = row['matrix_line']
        fail_if(not isinstance(i, int) or i < 1 or i > len(matrix_lines)
                or digest(matrix_lines[i - 1].encode('utf-8')) != row['row_sha256'],
                'Source citation no longer matches frozen matrix bytes')
        fail_if(not row['not_a_verified_conde_physical_event']
                or dep['independent_physical_observation_count'] is not None,
                'Attempted promotion of documentary citation to physical observation')
        edges = []
        for path in dep['declared_upstream_paths']:
            for edge in path['edges']:
                fail_if(edge['from'] != source or not edge['kind'] or not edge['to'],
                        'Invalid directed upstream source edge')
                edges.append([edge['from'], edge['kind'], edge['to']])
        grouped[source].append({
            'occurrence': row['occurrence'],
            'snapshot_ref': row['snapshot_ref'],
            'matrix_line': i,
            'row_sha256': row['row_sha256'],
            'work_id': row['work_id'],
            'archive_path': '/conde-incident/evidencias/arquivo/'
                            + row['occurrence'].lower().replace('#', '-') + '/',
            'upstream_edges': sorted({tuple(e) for e in edges}),
        })

    families = defaultdict(list)
    sources = []
    for source, rows in sorted(grouped.items()):
        originals = [row for row in references if row['source_id'] == source]
        family_ids = {row['source_family'] for row in originals}
        fail_if(len(family_ids) != 1, 'Source assigned multiple families')
        family = next(iter(family_ids))
        families[family].append(source)
        sources.append({
            'source_id': source,
            'source_family': family,
            'references': sorted(rows, key=lambda x: (x['matrix_line'], x['work_id'])),
        })
    fail_if(sum(len(s['references']) for s in sources) != len(references),
            'Missing source references in reverse lookup')
    fail_if(len({r['occurrence'] for r in references}) != citations['curated_occurrences'],
            'Incorrect curated coverage in source lookup')
    # Post-matrix documents have no frozen matrix row and must never get a Cnn#N alias.
    post_by_id = {r['id']: r for r in lineage['post_matrix_lineages']}
    fail_if(len(post_by_id) != len(lineage['post_matrix_lineages'])
            or set(post_by_id) != {r['id'] for r in citations['post_matrix_occurrences']},
            'Post-matrix lineage/citation mismatch')
    post = []
    for item in sorted(citations['post_matrix_occurrences'], key=lambda x: x['id']):
        dep = post_by_id[item['id']]
        fail_if(dep['source_id'] != item['source_id'] or
                dep['independent_physical_observation_count'] is not None or
                item['physical_constraint'] is not None,
                'Post-matrix source cannot be promoted to physical constraint')
        edges = sorted({(e['from'], e['kind'], e['to'])
                        for p in dep['declared_upstream_paths'] for e in p['edges']})
        fail_if(any(e[0] != item['source_id'] for e in edges),
                'Invalid post-matrix upstream source edge')
        post.append({'id': item['id'], 'source_id': item['source_id'],
                     'source_family': dep['source_family'], 'source_status': item['status'],
                     'upstream_edges': edges, 'matrix_line': None,
                     'independent_physical_observation_count': None})

    result = {
        'schema': 'conde.source-reverse-lookup/v1',
        'description': 'Índice derivado de citações documentais, não observações físicas',
        'matrix_git_blob_sha1': citations['matrix_git_blob_sha1'],
        'source_files_sha256': expected_source,
        'independent_physical_observation_count': None,
        'absence_of_declared_edge_proves_independence': False,
        'curated_reference_count': len(references),
        'curated_occurrence_count': citations['curated_occurrences'],
        'unmapped_occurrence_count': citations['unmapped_occurrences'],
        'sources': sources,
        'families': [{'family_id': family, 'source_ids': ids}
                     for family, ids in sorted(families.items())],
        'post_matrix_only': post,
    }
    raw = encode(result)
    fail_if(len(raw) > MAX_BYTES, 'Reverse lookup exceeds 20 KB; shard before publishing')
    name = DIR / ('part-' + digest(raw) + '.json')
    pointer = {
        'schema': 'conde.source-reverse-lookup-manifest/v1',
        'source_index': {'path': str(name), 'bytes': len(raw), 'sha256': digest(raw)},
        'inputs_sha256': {str(path): digest(content) for path, content in inputs.items()},
    }
    return {name: raw, POINTER: encode(pointer)}


def sync(artifacts, root=ROOT, check=False):
    expected = set(artifacts)
    existing = set(DIR.glob('*.json')) if root == ROOT else set((root / DIR).glob('*.json'))
    allowed = {root / item for item in expected if item.parent == DIR}
    for historical in existing - allowed:
        fail_if(not NAME.fullmatch(historical.name),
                'Unaddressed or foreign JSON in provenance shard directory')
        fail_if(digest(historical.read_bytes()) != historical.stem[5:],
                'Historical provenance shard mutated: ' + str(historical))
    for path, raw in artifacts.items():
        target = root / path
        if check:
            fail_if(not target.is_file() or target.read_bytes() != raw,
                    'Stale/missing provenance output: ' + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                fail_if(path != POINTER and target.read_bytes() != raw,
                        'Refusing to overwrite content-addressed provenance shard')
            if not target.exists() or target.read_bytes() != raw:
                tmp = target.with_suffix('.staged')
                tmp.write_bytes(raw)
                tmp.replace(target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    artifacts = build()
    sync(artifacts, check=args.check)
    print('PASS: %s, %s' % (next(p for p in artifacts if p != POINTER),
                             'replay byte-for-byte' if args.check else 'exported'))


if __name__ == '__main__':
    main()
