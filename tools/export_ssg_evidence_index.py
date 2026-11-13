"""Deterministic, bounded JSON shards of *curated citations*, not physical observations.

The existing SSG documentary archive remains the no-JavaScript interface.
This machine index is an optional input for browser search and cross-references.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CITATIONS = Path('public/data/conde-source-citations.json')
LINEAGE = Path('public/data/conde-declared-dependence.json')
DEST = Path('public/data/conde-evidence-index')
MANIFEST = Path('public/data/conde-evidence-index-manifest.json')
MAX_SHARD_BYTES = 12_000  # Below repository-wide 20,000-byte rule.
SHA256 = re.compile(r'[a-f0-9]{64}\Z')
SHA1 = re.compile(r'[a-f0-9]{40}\Z')
OCCURRENCE = re.compile(r'C[0-9]{1,3}#[1-9][0-9]*\Z')


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(',', ':')) + '\n').encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path, root):
    raw = (root / path).read_bytes()
    return json.loads(raw), digest(raw)


def build(root=ROOT):
    citations, citations_sha = load_json(CITATIONS, root)
    lineage, lineage_sha = load_json(LINEAGE, root)
    require(citations['schema'] == 'conde.source-citations/v1', 'Schema de citações incompatível')
    require(lineage['schema'] == 'conde.declared-documentary-dependence/v1', 'Schema genealógico incompatível')
    matrix = citations['matrix_git_blob_sha1']
    require(bool(SHA1.fullmatch(matrix)), 'SHA-1 de snapshot inválido')
    require(matrix == lineage['matrix_git_blob_sha1'], 'Snapshots de matriz diferentes')
    require(lineage['epistemic_limits']['independent_physical_observation_count'] is None,
            'Independência física não demonstrada')
    original = citations['records']
    family = lineage['citation_lineages']
    require(len(original) == len(family), 'Número de genealogias distinto das referências')
    require(len({x['occurrence'] for x in original}) == citations['curated_occurrences'],
            'Contagem curada de ocorrências divergente')
    require(citations['curated_occurrences'] + citations['unmapped_occurrences'] ==
            citations['total_matrix_occurrences'], 'Cobertura da matriz divergente')
    require(lineage['curated_occurrences'] == citations['curated_occurrences'],
            'Cobertura da genealogia divergente')
    ancestry = {}
    for entry in family:
        key = (entry['snapshot_ref'], entry['source_id'])
        require(key not in ancestry, 'Genealogia duplicada: ' + str(key))
        ancestry[key] = entry
    rows = []
    used = set()
    for record in original:
        occurrence = record['occurrence']
        require(bool(OCCURRENCE.fullmatch(occurrence)), 'ID de ocorrência inválido')
        require(record['snapshot_ref'] == f'matrix:{matrix}:{occurrence}', 'Referência de snapshot falsa')
        require(bool(SHA256.fullmatch(record['row_sha256'])), 'Hash da linha inválido')
        require(record['not_a_verified_conde_physical_event'] is True,
                'A referência não pode ser promovida a testemunho físico')
        require(isinstance(record['matrix_line'], int) and record['matrix_line'] > 0,
                'Número de linha da matriz inválido')
        require(record['citation_url'].startswith('https://'), 'Documento sem URL HTTPS')
        for name in ('source_id', 'source_family', 'work_id', 'source_status', 'locator',
                     'relation', 'scope', 'claim_text'):
            require(isinstance(record[name], str) and bool(record[name].strip()),
                    'Campo documental ausente: ' + name)
        key = (record['snapshot_ref'], record['source_id'])
        require(key not in used, 'Referência documental duplicada: ' + str(key))
        used.add(key)
        require(key in ancestry, 'Referência sem genealogia: ' + str(key))
        entry = ancestry[key]
        require(entry['row_sha256'] == record['row_sha256'], 'Hash divergente na genealogia')
        require(entry['matrix_line'] == record['matrix_line'], 'Linha divergente na genealogia')
        require(entry['family_id'] == record['source_family'], 'Família divergente')
        require(entry['independent_physical_observation_count'] is None,
                'Contagem física não pode ser inferida')
        paths = entry['declared_upstream_paths']
        require(isinstance(paths, list), 'Cadeias de dependência ausentes')
        for path in paths:
            # Entire paths are exported verbatim; unknown keys could publish
            # fabricated observations without altering declared row hashes.
            require(isinstance(path, dict) and set(path) == {'edges', 'upstream_source_id'},
                    'Cadeia contém campo documental não validado')
            cursor = record['source_id']
            visited = {cursor}
            require(isinstance(path['edges'], list) and bool(path['edges']), 'Cadeia vazia')
            for edge in path['edges']:
                require(isinstance(edge, dict) and set(edge) == {'from', 'to', 'kind'},
                        'Aresta contém campo documental não validado')
                require(isinstance(edge['to'], str) and bool(edge['to'].strip())
                        and edge['from'] == cursor and edge['to'] not in visited
                        and isinstance(edge['kind'], str) and bool(edge['kind'].strip()),
                        'Cadeia descontínua, cíclica ou sem relação')
                cursor = edge['to']
                visited.add(cursor)
            require(cursor == path['upstream_source_id'], 'Origem ancestral divergente')
        rows.append({
            'occurrence': occurrence, 'snapshot_ref': record['snapshot_ref'],
            'source_id': record['source_id'], 'source_family': record['source_family'],
            'work_id': record['work_id'], 'source_status': record['source_status'],
            'relation': record['relation'], 'scope': record['scope'],
            'locator': record['locator'], 'claim_text': record['claim_text'],
            'citation_url': record['citation_url'], 'row_sha256': record['row_sha256'],
            'matrix_line': record['matrix_line'],
            'declared_upstream_paths': paths,
            'independent_physical_observation_count': None,
            'not_a_verified_conde_physical_event': True,
            'archive_path': ('/conde-incident/evidencias/arquivo/' +
                             occurrence.lower().replace('#', '-') + '/'),
        })
    require(used == set(ancestry), 'Genealogia órfã não exportada')
    rows.sort(key=lambda r: (int(r['occurrence'].split('#')[0][1:]),
                             int(r['occurrence'].split('#')[1]), r['source_id']))
    # Separate chunks are immutable by content hash and small enough for repository policy.
    chunks = []
    chunk = []
    for row in rows:
        proposed = chunk + [row]
        payload = canonical({'schema': 'conde.evidence-index-shard/v1', 'records': proposed})
        require(len(canonical({'schema': 'conde.evidence-index-shard/v1', 'records': [row]}))
                <= MAX_SHARD_BYTES, 'Uma referência sozinha excede o teto')
        if len(payload) > MAX_SHARD_BYTES and chunk:
            chunks.append(chunk)
            chunk = [row]
        else:
            chunk = proposed
    if chunk:
        chunks.append(chunk)
    artifacts = {}
    shard_refs = []
    for i, records in enumerate(chunks, 1):
        relative = DEST / f'part-{i:03d}.json'
        raw = canonical({'schema': 'conde.evidence-index-shard/v1', 'records': records})
        require(len(raw) <= MAX_SHARD_BYTES, 'Shard excedeu 12 kB')
        artifacts[relative] = raw
        shard_refs.append({'path': str(relative), 'sha256': digest(raw),
                           'bytes': len(raw), 'record_count': len(records)})
    post_ids = [x['id'] for x in citations.get('post_matrix_occurrences', [])]
    require(len(post_ids) == len(set(post_ids)), 'ID pós-matriz repetido')
    manifest = {
        'schema': 'conde.evidence-index/v1',
        'description': 'Referências documentais curadas; não é matriz integral nem evidência física',
        'matrix_git_blob_sha1': matrix,
        'source_files': [
            {'path': str(CITATIONS), 'sha256': citations_sha},
            {'path': str(LINEAGE), 'sha256': lineage_sha},
        ],
        'curated_occurrences': citations['curated_occurrences'],
        'curated_reference_count': len(rows),
        'unmapped_matrix_occurrences': citations['unmapped_occurrences'],
        'total_matrix_occurrences': citations['total_matrix_occurrences'],
        'post_matrix_ids_not_in_curated_index': post_ids,
        'independent_physical_observation_count': None,
        'absence_of_declared_dependency_proves_independence': False,
        'no_js_index': '/conde-incident/evidencias/arquivo/',
        'shards': shard_refs,
    }
    artifacts[MANIFEST] = canonical(manifest)
    return artifacts


def sync(artifacts, root=ROOT, check=False):
    directory = root / DEST
    existing = set(directory.glob('part-*.json')) if directory.exists() else set()
    expected = {root / p for p in artifacts if p.parent == DEST}
    require(not check or existing == expected, 'Lista de shards desatualizada')
    for path, raw in artifacts.items():
        target = root / path
        if check:
            require(target.exists() and target.read_bytes() == raw,
                    'Índice não reproduzível: ' + str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    if not check:
        for stale in existing - expected:
            stale.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Comparar bytes sem escrever')
    args = parser.parse_args()
    artifacts = build()
    sync(artifacts, check=args.check)
    print(f"Índice OKF SSG: {len(artifacts)-1} shard(s), "
          f"{sum(len(v) for v in artifacts.values())} bytes; "
          f"{'verificado' if args.check else 'escrito'}.")
