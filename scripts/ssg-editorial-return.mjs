// Links de contexto editorial, não novas provas ou relações científicas.
const editorialReturns = new Map([
  ['C01#1', {anchor:'contexto-fbis', label:'a transmissão FBIS'}],
  ['C197#1', {anchor:'contexto-nasa', label:'a data no catálogo NASA'}],
]);
export const returnToStory = occurrence => {
  const context=editorialReturns.get(occurrence);
  return context ? `[Voltar à reportagem: ${context.label}](/conde-incident/stories/2026-11-12-a-resposta-que-veio-de-salvador/#${context.anchor})` : null;
};
