/**
 * A catalogue decay date constrains a calendar day, not a terminal UTC second.
 * Historical data and model-derived display events must not share a marker.
 *
 * OBS-07 was an unsupported claim of a Conde encounter at 19:48 UTC.
 * OBS-08/OBS-11 use an arbitrary end-of-day timestamp as if observed.
 * Keep the source catalogue untouched; filter only the public interactive map.
 */
const unverifiedTerminalIds = new Set(['OBS-07', 'OBS-08', 'OBS-11']);

export function publicMilestones<T extends { id: string }>(events: readonly T[]): T[] {
  return events.filter((event) => !unverifiedTerminalIds.has(event.id));
}
