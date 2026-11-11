import { readFileSync } from 'node:fs';

// Genealogical roots represent document lineage, NEVER independent witnesses
// to a physical event. The code checks conservative editorial consistency.
export function genealogicalRoots(graph, ids) {
  const parents = new Map(graph.nodes.map(n => [n.id, []]));
  for (const edge of graph.relations) {
    if (['documented_transcription', 'documented_quotation'].includes(edge.kind)) {
      if (!parents.has(edge.to) || !parents.has(edge.from)) throw Error('Unknown genealogy endpoint');
      parents.get(edge.to).push(edge.from);
    }
  }
  function roots(id, seen = new Set()) {
    if (seen.has(id)) throw Error('Cycle in documented genealogy');
    if (!parents.has(id)) throw Error('Unknown source: ' + id);
    const upstream = parents.get(id);
    if (!upstream.length) return [id];
    const next = new Set(seen);
    next.add(id);
    return upstream.flatMap(p => roots(p, next));
  }
  return [...new Set(ids.flatMap(id => roots(id)))].sort();
}

export function auditGraph(graph) {
  const errors = [];
  const nodes = new Map();
  const claims = new Map();
  if (graph.schema_version !== 1 || !graph.based_on?.matrix || !graph.based_on?.ledger)
    errors.push('Missing version or pinned prior evidence');
  for (const node of graph.nodes ?? []) {
    if (nodes.has(node.id)) errors.push('Duplicate source: ' + node.id);
    nodes.set(node.id, node);
    if (!/^https:\/\//.test(node.url ?? '')) errors.push('Missing source URL: ' + node.id);
    if (!(node.matrix_ids?.length > 0)) errors.push('Missing matrix IDs: ' + node.id);
    if (!node.inspection || !node.family) errors.push('Unclassified source: ' + node.id);
    if (!Array.isArray(node.supports)) errors.push('Missing support array: ' + node.id);
  }
  const kinds = ['documented_transcription','documented_quotation','shared_institution_only','possible_common_information','possible_common_tracking'];
  for (const edge of graph.relations ?? []) {
    if (!nodes.has(edge.from) || !nodes.has(edge.to) || edge.from === edge.to)
      errors.push('Invalid relation endpoints: ' + edge.from + ' -> ' + edge.to);
    if (!kinds.includes(edge.kind)) errors.push('Unknown relation kind: ' + edge.kind);
    if (edge.kind.startsWith('possible_') && edge.verification !== 'unverified')
      errors.push('Possible link presented as verified: ' + edge.from + ' -> ' + edge.to);
    if (edge.kind === 'shared_institution_only' && !edge.note?.includes('does not prove'))
      errors.push('Institutional relationship must not be treated as copied text');
    if (!edge.note || !edge.verification) errors.push('Unqualified relation: ' + edge.from);
  }
  try { genealogicalRoots(graph, [...nodes.keys()]); }
  catch (e) { errors.push(String(e.message)); }

  const validStatuses = ['documented_text','prior_matrix_only','secondary_technical','not_verified'];
  for (const claim of graph.claims ?? []) {
    if (claims.has(claim.id)) errors.push('Duplicate claim: ' + claim.id);
    claims.set(claim.id, claim);
    if (!validStatuses.includes(claim.status)) errors.push('Unknown status: ' + claim.id);
    if (!Array.isArray(claim.sources) || !Array.isArray(claim.cannot_infer) || !claim.cannot_infer.length)
      errors.push('Missing claim bounds: ' + claim.id);
    for (const sourceId of claim.sources ?? []) {
      const source = nodes.get(sourceId);
      if (!source || !source.supports?.includes(claim.id))
        errors.push('Source does not support documentary claim: ' + claim.id + ' / ' + sourceId);
    }
    if (claim.status === 'not_verified' && claim.sources?.length)
      errors.push('Unsupported conclusion promoted to source-backed: ' + claim.id);
    if (claim.status !== 'not_verified' && !claim.sources?.length)
      errors.push('Documentary claim without carrier: ' + claim.id);
    if (claim.status === 'documented_text' && !claim.sources?.some(id => nodes.get(id)?.inspection === 'direct_visual_facsimile'))
      errors.push('Direct source inspection missing: ' + claim.id);
  }
  for (const id of ['impact_in_conde','reentry_coordinates','broadcast_clock_zone_GMT','hoax_physically_proven']) {
    const c = claims.get(id);
    if (!c || c.status !== 'not_verified' || c.sources?.length)
      errors.push('Unverified empirical claim was promoted: ' + id);
  }
  if (!graph.relations?.some(e => e.from === 'TUPI_RIO' && e.to === 'FBIS03' && e.kind === 'documented_transcription'))
    errors.push('Missing Tupi -> FBIS common-report genealogy');
  if (nodes.get('BLUEBOOK_INDEX')?.inspection !== 'prior_matrix_text_extraction_no_visual_facsimile')
    errors.push('Blue Book index promoted beyond verified inspection');
  if (nodes.get('TUPI_SP_SCRIPT_09')?.inspection !== 'prior_matrix_24_page_visual_check_not_repeated')
    errors.push('TV script promoted to newly verified inspection');
  return errors;
}

export function summarize(graph) {
  const result = {};
  for (const c of graph.claims) {
    result[c.id] = {
      status: c.status,
      documented_carriers: c.sources,
      genealogical_roots: genealogicalRoots(graph, c.sources),
      warning: 'Genealogy is not an independent physical observation count'
    };
  }
  return result;
}

if (process.argv[1]?.endsWith('check-document-genealogy.mjs')) {
  const data = JSON.parse(readFileSync(new URL('../research/gaviao_document_genealogy_2026-11-11.json', import.meta.url),'utf8'));
  const errors = auditGraph(data);
  if (errors.length) {
    console.error(errors.join('\n'));
    process.exitCode = 1;
  } else {
    const out = summarize(data);
    console.log('PASS: documentary lineage checked; FBIS radio-report root(s)=' +
      out.radio_report_in_fbis.genealogical_roots.join(',') +
      '; physical impact=' + out.impact_in_conde.status +
      '; terminal coordinates=' + out.reentry_coordinates.status +
      '; GMT timezone=' + out.broadcast_clock_zone_GMT.status +
      '; no live/physical evidence inferred.');
  }
}
