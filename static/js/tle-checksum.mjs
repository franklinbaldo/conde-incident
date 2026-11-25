/**
 * Minimal NORAD TLE syntax checks shared by the lab and SSG.
 * A valid modulo-10 digit does not authenticate an epoch, sensor, orbit or source.
 * Deliberately do not trim, pad, normalize, or repair the user's input bytes.
 */
/**
 * @param {string} line
 * @param {1 | 2} expectedLine
 * @param {number | null} expectedNoradId
 */
export function auditTleSyntax(line, expectedLine, expectedNoradId) {
  const length = line.length;
  const prefixMatches = line[0] === String(expectedLine)
    && line[1] === ' '
    && /^\d{5}$/.test(line.slice(2, 7))
    && Number(line.slice(2, 7)) === expectedNoradId;
  const actualChecksum = length === 69 && /^\d$/.test(line[68]) ? Number(line[68]) : null;
  const computedChecksum = length === 69
    ? [...line.slice(0, 68)].reduce(
        (sum, character) => sum + (/^\d$/.test(character) ? Number(character) : character === '-' ? 1 : 0),
        0,
      ) % 10
    : null;
  return {
    length, expectedLine, prefixMatches, actualChecksum, computedChecksum,
    valid: length === 69 && prefixMatches
      && actualChecksum !== null && computedChecksum === actualChecksum,
  };
}
