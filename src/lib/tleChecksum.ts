/**
 * Only checks TLE line length, number/prefix and modulo-10 check digit.
 * A passing checksum says NOTHING about historical custody, authentic epochs,
 * measurements, orbit quality, physical admissibility or independent sources.
 */
export interface TleSyntaxAudit {
  length: number;
  expectedLine: 1 | 2;
  actualChecksum: number | null;
  computedChecksum: number | null;
  prefixMatches: boolean;
  valid: boolean;
}

export function auditTleSyntax(line: string, expectedLine: 1 | 2, expectedNoradId: number): TleSyntaxAudit {
  const length = line.length;
  const prefixMatches =
    line[0] === String(expectedLine) &&
    line[1] === ' ' &&
    /^\d{5}$/.test(line.slice(2, 7)) &&
    Number(line.slice(2, 7)) === expectedNoradId;
  const actualChecksum = length === 69 && /^\d$/.test(line[68]) ? Number(line[68]) : null;
  const computedChecksum = length === 69
    ? [...line.slice(0, 68)].reduce((sum, character) => {
        if (/^\d$/.test(character)) return sum + Number(character);
        return sum + (character === '-' ? 1 : 0);
      }, 0) % 10
    : null;
  return {
    length,
    expectedLine,
    actualChecksum,
    computedChecksum,
    prefixMatches,
    valid: length === 69 && prefixMatches && actualChecksum !== null && computedChecksum === actualChecksum,
  };
}
