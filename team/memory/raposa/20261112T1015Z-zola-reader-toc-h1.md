# OKF — 🦊 Raposa, 12/11/2026: leitor Markdown com índice verificável e H1 único

## Retomada e delimitação
- Lidos `AGENTS.md` e `team/raposa.md` na main, issue #9, PRs #1/#3/#24/#28, issues/PRs abertas e a matriz cumulativa C001–C238 pinada no SHA `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b` da PR #1.
- A #28 continuava aberta na consulta; aplicado o fluxo científico exigido pelo usuário sem antecipar merge para main.
- Retomada a PR #24 **Draft**, branch `raposa/zola-evidence-lab-deeplinks`, empilhada sobre `feature/coruja-reportage` da Coruja. Nenhuma edição em `stories/*.md`, blog pessoal, dados observacionais, modelo físico ou matriz científica.

## Defeito e fatia verificáveis
- **Defeito encontrado pelo CI:** o gerador removia o primeiro `# H1` somente quando imediatamente após o YAML; o capítulo canônico começa com linha vazia. O render Zola duplicava a manchete (`h1` editorial + `h1` Markdown) e o novo índice apontava ao `H1` repetido. Corrigida a regex em `scripts/prepare-zola.mjs`, sem reescrever a reportagem.
- **Leitura longa:** `templates/story.html` agora utiliza `page.toc` nativo do Zola, `<nav>` semântico e `<details>/<summary>` acessível por teclado para consultar títulos e âncoras verdadeiras do Markdown. Adicionada navegação sequencial `page.lower/page.higher` quando houver capítulos, com retorno para o índice.
- **Metadados e visual:** `article:published_time` na página do capítulo via bloco no template-base; cores, foco visível, estilo responsivo e texto de tamanho flexível em `static/css/site.css`. Sem nova dependência JS.
- **Gate de HTML:** `scripts/check-site.mjs` agora verifica âncoras do índice contra IDs de cabeçalhos renderizados, metadado do artigo, ausência de H1 repetido, landmark e vizinhança cronológica (o último par só exercitável quando 2+ capítulos estiverem integrados). Mantidos testes anteriores de Evidence `#/research/c01`, `#/research/c197`, mapa e fonte pinada.

## Fontes, grau e limites
- **VERIFICADO no código e artefato de CI:** [templates da PR #24](https://github.com/franklinbaldo/conde-incident/pull/24), [estrutura nativa do índice Zola](https://www.getzola.org/documentation/content/table-of-contents/), [ordenação e vizinhos por weight Zola](https://www.getzola.org/documentation/content/section/). Verificada por inspeção a separação de `stories/*.md` (texto Coruja) e `content/stories/` (gerado).
- **Fonte científica contextual:** [matriz pinada C001–C238](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md), sobretudo C01/C02 (mesma cadeia Tupi/FBIS) e C197–C202 (registro NASA do dia, sem hora/posição); este trabalho não gerou nenhuma nova alegação científica ou linha da matriz. Fontes primárias não reinspecionadas. Nenhum pressuposto Lean ou domínio numérico certificado nesta fatia.
- **Falha intermediária auditável:** [run #43198237934](https://github.com/franklinbaldo/conde-incident/actions/runs/43198237934) **FAIL** no teste de integridade dos fragmentos: TOC incluía o H1 duplicado pelo bug preexistente. Correção posterior sem silenciar o teste.
- **Gate do código depois da correção:** [commit `9a5ab4ee`](https://github.com/franklinbaldo/conde-incident/commit/9a5ab4ee3d92949cd400e3df4159fc4ddf67da10), [run #43198474722](https://github.com/franklinbaldo/conde-incident/actions/runs/43198474722) **SUCCESS**; React/Vite, TypeScript, Zola check/build e auditoria HTML passam. Este registro de memória produzirá outro HEAD; o CI desse SHA também deve ser conferido.
- **NÃO VERIFICADO:** interações em navegador móvel/leitor de tela físico, `page.lower/page.higher` com dois capítulos reais (branch #24 contém 1), integração das reportagens posteriores PRs da Coruja, reconciliação #1/#3/#24, deploy Pages, evidência física de queda, hora/local/probabilidade ou domínio admissível validado.

## Próxima dúvida
- Validar de ponta a ponta a navegação anterior/próximo assim que a Coruja integrar pelo menos dois capítulos, sem importar os textos dela para esta PR. Testar VoiceOver/TalkBack e contraste/rolagem em telas reais. 🦅 Gavião revisa; 🐘 Elefante concilia e integra. Nenhum merge ou deploy realizado pela Raposa.
