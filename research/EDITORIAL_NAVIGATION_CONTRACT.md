# Contrato de navegação conjunta: Evidências e Caderno

Esta fatia é a **ponte de integração** entre a base científica [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1) e o Caderno editorial [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3), empilhada depois do reparo C197 [PR #61](https://github.com/franklinbaldo/conde-incident/pull/61). **Não é** a publicação nem a integração completa do gerador editorial.

## Contrato implementado, testável

- O React/Vite **continua iniciando em Evidências & Pesquisa**, com `ResearchLedger` e avisos visíveis de que os outros módulos são exploratórios.
- O menu científico mantém a aba Evidências e acrescenta link `<a>` nativo (sem leitor duplicado) para o **Caderno de histórias**: `/stories/` localmente e `/conde-incident/stories/` quando o laboratório é montado em `/conde-incident/lab/`.
- `src/lib/sitePaths.mjs` valida a base do laboratório: não aceita domínio externo, `//`, traversal, URL codificada ou query. A navegação não depende de `window.location` nem de data histórica.
- `vite.config.ts` aceita `SCIENCE_BASE` e o modo `GITHUB_PAGES=true` para assets do laboratório na subpasta correta; CI executa cinco testes adversariais no SHA da branch.

## Dependências ainda bloqueantes

1. Integrar a correção C197 e a matriz completa da #1 **somente após** revisão Gavião da base e CI exato; este patch não fornece aprovação global da #1.
2. A [decisão #22](https://github.com/franklinbaldo/conde-incident/pull/22) requer **SSG Rust**; a #3 ainda apresenta Zola. A Coruja é responsável por converter o Markdown canônico `stories/YYYY-MM-DD-slug.md` para SSG Rust e fornecer links reversos Caderno → Evidências. Não substituir a aba científica nem introduzir leitores React duplicados.
3. Gavião deve revisar a composição final, incluindo caminhos reais, Caderno com **novidade verificável** desde o último capítulo e proveniência. Nenhuma notícia nova nesta fatia.
4. Publicação somente após merge em `main`, fonte Pages **GitHub Actions**, sucesso CI no SHA final e deployment público `github-pages` + inspeção HTTPS. `has_pages=false` na API consultada em 12/11/2026: **NOT_VERIFIED**, não afirmar publicação.

## Limite científico

A ocorrência **C197** ([NASA NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), 15/11/1963, p. impressa 8 / PDF índice 9) documenta o decaimento catalogado de `1963 3B` no dia 08/11, sem hora ou posição terminal. C198 aponta ao mesmo documento, não conta como medição independente. Sem TLE primária autenticada, redução comprovada do conjunto admissível, solver reproduzível e holdouts, esta navegação não altera a conclusão científica. Prioridade: custódia 527–529/RAAN #13 → Lean condicional #15/#28 → domínio não vazio/reduzido + holdout 529 #19 → simulador físico #4.

**Critério de reversão:** se a futura publicação SSG montar Caderno fora de `stories/`, alterar um único contrato de caminhos, manter os testes de links e revalidar a composição no SHA final antes de integrar. Não modificar `franklinbaldo.github.io`.
