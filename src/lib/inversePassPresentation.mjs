// Presentation-only translations for the legacy inverse solver. No orbital inputs change.
// Exact string matching fails closed if the solver changes a note.
const feasibilityEn = Object.freeze({
  ALTA: 'HIGH',
  MODERADA: 'MODERATE',
  EXTREMA: 'EXTREME',
  INCOMPATIVEL: 'INCOMPATIBLE',
});

const noteBases = [
  ['Geometria nominal quase direta sobre o litoral norte baiano. Requer ajuste de fase mínimo (<0,5°).',
    'Nominal geometry lies close to the northern Bahia coast. The legacy note assumes a minimal phase adjustment (<0.5°).'],
  ['Passagem dentro do horizonte visual de alta altitude (>150 km). Fase sintonizável com pequena variação de arrasto.',
    'Pass within the high-altitude viewing horizon (>150 km). The legacy note assumes phase adjustment by a small drag variation.'],
  ['Passagem regional distante (Atlântico ou interior do Brasil). Exigiria desvio balístico acumulado de 3° a 10°.',
    'Distant regional pass (Atlantic or inland Brazil). The legacy note estimates a cumulative ballistic deviation of 3° to 10°.'],
  ['Fora de qualquer raio de observação ou reentrada terminal local (>1500 km de Conde).',
    'Outside the legacy local observation or terminal-reentry radius (>1500 km from Conde).'],
];

const noteSuffixes = new Map([
  [' Altura orbital ainda em vácuo (>200 km); não é ponto de queda.',
    ' Orbital altitude is still above 200 km; this is not an impact point.'],
  [' CORREDOR DE REENTRADA TÉRMICA (120-70 km).',
    ' THERMAL REENTRY CORRIDOR (120–70 km, legacy designation).'],
]);

export function inverseHeuristicText(code, lang) {
  if (lang === 'pt') return code;
  return Object.hasOwn(feasibilityEn, code)
    ? feasibilityEn[code]
    : `Untranslated legacy code (PT): ${code}`;
}

export function inverseLegacyNote(note, lang) {
  if (lang === 'pt') return note;
  for (const [source, english] of noteBases) {
    if (!note.startsWith(source)) continue;
    const suffix = note.slice(source.length);
    if (!suffix) return english;
    const translatedSuffix = noteSuffixes.get(suffix);
    if (translatedSuffix) return english + translatedSuffix;
  }
  return `Untranslated legacy note (PT): ${note}`;
}

export function inverseBahiaClock(value, lang) {
  if (lang === 'pt') return value;
  const suffix = '(Horário da Bahia / UTC-3)';
  return value.endsWith(suffix)
    ? value.slice(0, -suffix.length) + '(Bahia time / UTC-3)'
    : `Untranslated legacy time label (PT): ${value}`;
}
