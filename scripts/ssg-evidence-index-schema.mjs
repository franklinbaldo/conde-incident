import assert from 'node:assert/strict';

const tracked=['occurrence','snapshot_ref','source_id','source_family','work_id',
  'source_status','relation','scope','locator','claim_text','citation_url',
  'row_sha256','matrix_line'];

// Reject extra machine-readable fields even when the JSON digest was recomputed.
// Otherwise a consumer might mistake unreviewed properties for physical evidence.
export const exactKeys=(value,keys,context)=>assert.deepEqual(
  Object.keys(value).sort(),[...keys].sort(),'Unexpected '+context+' fields');
export const manifestKeys=[
  'schema','description','matrix_git_blob_sha1','matrix_source','source_files',
  'curated_occurrences','curated_reference_count','unmapped_matrix_occurrences',
  'unmapped_matrix_refs','unmapped_shards','total_matrix_occurrences',
  'post_matrix_ids_not_in_curated_index','independent_physical_observation_count',
  'absence_of_declared_dependency_proves_independence','no_js_index','shards',
];
export const curatedKeys=[...tracked,'archive_path','declared_upstream_paths',
  'independent_physical_observation_count','not_a_verified_conde_physical_event'];
export const shardMetaKeys=['path','sha256','bytes','record_count'];
export const gapKeys=['occurrence','matrix_line','row_sha256','claim_text'];

export {tracked};
