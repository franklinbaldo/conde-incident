// Links de contexto editorial, não novas provas ou relações científicas.
const editorialReturns = new Map([
  ['C01#1', {anchor:'contexto-fbis', label:'a transmissão FBIS'}],
  ['C197#1', {anchor:'contexto-nasa', label:'a data no catálogo NASA'}],
]);
export const returnToStory = occurrence => {
  const context=editorialReturns.get(occurrence);
  return context ? `[Voltar à reportagem: ${context.label}](/conde-incident/stories/2026-11-12-a-resposta-que-veio-de-salvador/#${context.anchor})\n\n${returnToDossier(occurrence)}` : null;
};

// Return path for the two occurrences that are actually discussed in the opening dossier.
// A navigational relationship is not a new historical-evidence dependency.
const dossierOccurrences = new Set(['C01#1','C197#1']);
export const returnToDossier = occurrence =>
  dossierOccurrences.has(occurrence)
    ? '[Retornar ao dossiê de abertura: comparar as duas fontes](/conde-incident/dossie/#fontes)'
    : null;
