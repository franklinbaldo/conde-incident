/**
 * Pivoted, two-pass modified Gram-Schmidt rank of stacked Cartesian position
 * displacements, measured in km. Columns represent finite-difference velocity
 * probes. This is a local, threshold-dependent NUMERICAL diagnostic: neither
 * a singular-value enclosure nor evidence of orbital observability in 1963.
 *
 * A fixed vx,vy,vz traversal can artificially inflate rank when a weak column
 * is accepted before a much stronger nearly-parallel one. At every pivot we
 * instead select the largest residual over all remaining free axes. Axes
 * excluded by the numerical rank are not proven physically unobservable.
 */
export interface VelocityRankColumn {
  readonly rawNormKm: number;
  /** Residual after projecting against the selected pivot basis. */
  readonly independentNormKm: number;
  readonly entersBasis: boolean;
}
export interface PivotedVelocityRank {
  readonly rankAtThreshold: number;
  /** Indices into the caller's input columns, in selected pivot order. */
  readonly pivotOrder: readonly number[];
  readonly columns: readonly VelocityRankColumn[];
}

function magnitude(values: readonly number[]): number {
  return Math.hypot(...values);
}
function dot(x: readonly number[], y: readonly number[]): number {
  return x.reduce((sum, xi, i) => sum + xi * y[i], 0);
}
function residual(input: readonly number[], basis: readonly (readonly number[])[]): number[] {
  const out = [...input];
  // Reorthogonalization reduces loss for nearly parallel columns.
  for (let pass = 0; pass < 2; pass++) {
    for (const unit of basis) {
      const projection = dot(out, unit);
      for (let i = 0; i < out.length; i++) out[i] -= projection * unit[i];
    }
  }
  return out;
}

/**
 * Returns null if finite inputs create a nonfinite norm or projection.
 * Caller must then mark the audit NOT_RUN, never treat it as rank zero.
 */
export function pivotVelocityResponseRank(
  columns: readonly (readonly number[])[], minimumSignalKm: number,
): PivotedVelocityRank | null {
  if (!Array.isArray(columns) || columns.length > 3 ||
      !(minimumSignalKm > 0) || !Number.isFinite(minimumSignalKm))
    throw new RangeError('Require up to three columns and a positive finite km threshold');
  if (!columns.length) return { rankAtThreshold: 0, pivotOrder: [], columns: [] };
  const length = columns[0]?.length;
  if (!Number.isInteger(length) || length === 0 || length % 3 !== 0 ||
      columns.some(c => !Array.isArray(c) || c.length !== length))
    throw new RangeError('Every response column needs the same nonempty 3D position schedule');
  if (columns.some(c => c.some(x => !Number.isFinite(x)))) return null;

  const rawNorms = columns.map(magnitude);
  if (rawNorms.some(x => !Number.isFinite(x))) return null;
  const basis: number[][] = [];
  const pivotOrder: number[] = [];
  const selected = new Set<number>();

  for (let step = 0; step < columns.length; step++) {
    let bestIndex = -1;
    let bestMagnitude = -Infinity;
    let bestResidual: number[] = [];
    for (let i = 0; i < columns.length; i++) {
      if (selected.has(i)) continue;
      const candidate = residual(columns[i], basis);
      const size = magnitude(candidate);
      if (!Number.isFinite(size)) return null;
      if (size > bestMagnitude) {
        bestMagnitude = size;
        bestIndex = i;
        bestResidual = candidate;
      }
    }
    if (bestIndex === -1 || bestMagnitude < minimumSignalKm) break;
    selected.add(bestIndex);
    pivotOrder.push(bestIndex);
    basis.push(bestResidual.map(x => x / bestMagnitude));
  }

  const assessed = columns.map((column, i) => {
    // Selected pivots are recorded at their selection stage; others are
    // projected against the complete accepted basis.
    const pivotPosition = pivotOrder.indexOf(i);
    const referenceBasis = pivotPosition < 0 ? basis : basis.slice(0, pivotPosition);
    const independentNormKm = magnitude(residual(column, referenceBasis));
    return { rawNormKm: rawNorms[i], independentNormKm,
      entersBasis: pivotPosition >= 0 };
  });
  if (assessed.some(c => !Number.isFinite(c.independentNormKm))) return null;
  return { rankAtThreshold: pivotOrder.length, pivotOrder, columns: assessed };
}
