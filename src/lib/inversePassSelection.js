// Selection only uses the visible scenario subset; it does not validate the physics.
/**
 * @template {{ epochMs: number, closestApproachDistanceKm: number }} T
 * @param {readonly T[]} visible
 * @param {number | null} requestedEpoch
 * @param {boolean} preferNearest
 * @returns {T | null}
 */
export function selectVisiblePass(visible, requestedEpoch, preferNearest) {
  const explicit = visible.find((pass) => pass.epochMs === requestedEpoch);
  if (explicit) return explicit;
  if (!preferNearest) return visible[0] ?? null;
  return visible.reduce(
    (closest, pass) => !closest || pass.closestApproachDistanceKm < closest.closestApproachDistanceKm
      ? pass : closest, null
  );
}
