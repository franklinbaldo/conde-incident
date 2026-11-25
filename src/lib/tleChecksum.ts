import { auditTleSyntax as auditSharedTleSyntax } from '../../static/js/tle-checksum.mjs';

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
  return auditSharedTleSyntax(line, expectedLine, expectedNoradId);
}
