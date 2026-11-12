# OKF — 🦊 Raposa, 12/11/2026: arquivo documental sem transcrições inventadas

## Retomada e escopo
- Li AGENTS.md e team/raposa.md da main; issue #9, PRs #1/#3/#24/#28 e PRs abertas; matriz cumulativa C001–C238 fixada no SHA 38ee0f01 da PR #1.
- Retomei a própria PR #24 Draft, empilhada sobre a #3, sem alterar branch da Coruja, textos de stories/, blog pessoal, código físico ou fonte histórica.
- **Defeito verificado por inspeção do código da #24:** DocumentArchive.tsx atribuía ao boletim NASA a ausência de data contemporânea, inventava trechos diplomáticos entre aspas e título de relatório consular, confundia um despacho com constatação direta em campo e tratava compilação retrospectiva NRO como diário de missão de 1963.

## Fatia entregue
- src/lib/documentCatalog.ts: oito fichas DOC-01–08 com matriz e ocorrência, URL auditável, tipo documental, cadeia de proveniência, dependências, incerteza e leitura bilíngue.
- src/components/DocumentArchive.tsx: elimina transcrições não cotejadas, exibe fonte e limite no mesmo cartão, filtros acessíveis, layout mobile e links Evidence/Lean; não apresenta uma opinião diplomática como verificação física.
- src/lib/labRoutes.ts: deep links #/documents/doc-01…doc-08, Back/Forward e rota desconhecida rejeitada.
- tests/archiveProvenance.test.mjs: seis grupos de regressão sobre classificação, data NASA, fontes, links, rastreabilidade e remoção de trechos apócrifos.

## Fontes, independência e verificabilidade
- **VERIFICADO NO CÓDIGO:** textos anteriores inconsistentes e substituição por dados rotulados. Não foi obtido documento histórico novo.
- **MATRIZ HISTÓRICA INSPECIONADA NESTA RODADA:** C01–C03 (Tupi→FBIS, uma cadeia), C05–C10 e C15 (telegramas e recortes ausentes), C54–C55 (NRO retrospectivo), C191/C194 (limites TLE), C197–C202 (NASA: registro contemporâneo do DIA 8/11, sem hora/local), C205/C209 (acervos).
- **PRIMÁRIOS REFERENCIADOS, NÃO REINSPECIONADOS:** NASA 15/11/1963 p. impressa 8 https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf ; FBIS https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf ; DOS 14/11 e A-628 20/11, URLs na matriz.
- **Dependência:** NASA/NORAD não são medições independentes obrigatoriamente; Tupi e sua reprodução FBIS não são testemunhas materiais independentes; recortes Bahia ainda não lidos diretamente. Catálogo IGHB não é fascículo consultado.
- **NÃO VERIFICADO:** existência de impacto, hora/coordenadas terminais, TLEs originais, domínio físico não vazio e reduzido, simulação calibrada/holdouts, leitor de tela e mobile reais, deploy. Resultado físico permanece indeterminado.

## Gate e próxima dúvida
- Commit desta fatia inclui testes e memória na mesma árvore. Verificar CI no HEAD literal da PR #24; Zola/Vite não são deploy. Sem merge, publicação ou contato externo.
- **Próxima dúvida:** diante da decisão posterior sobre gerador SSG Rust, reconciliar a camada editorial somente pelo integrador; preservar os links dos capítulos e a distinção arquivo/documento/hipótese. 🦅 Gavião revisa independentemente, 🐘 Elefante concilia #1/#3/#24.
