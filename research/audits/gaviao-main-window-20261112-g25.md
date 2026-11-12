---
type: Guide
title: "G25: 13 integrações e bloqueio de vazamento entre blocos RAAN"
description: "Auditoria retrospectiva a52b4e7..609b352d com SHA completo, teste adversarial e limites epistêmicos do Conde."
---

# 🦅 G25: revisão científica, editorial e de software

**Janela imutável:** [`a52b4e75..609b352d`](https://github.com/franklinbaldo/conde-incident/compare/a52b4e757198d24a3a29a058438abe891d74c54c...609b352d382fc2d7b4ee48c06c9dc8b9cc1a2e05). Partiu-se do checkpoint privado G24, não do SHA da sua PR. Cobertura **13 integrações first-parent**, 12 squash e 1 merge convencional (#240, com 1 commit lateral), total **14 commits no DAG**, sem commit direto. A redação da #253 omite o número da PR no assunto, mas o SHA de integração confere com a PR no GitHub. Incluem-se PRs fechadas sem integração no intervalo: **#148, #249, #251 e #254**; foram substituídas por trabalhos integrados, não contadas como merges. [Manifesto completo](gaviao-main-window-20261112-g25.json) com SHA, pais, arquivos e heads PR.

## Cobertura integral first-parent

| PR | SHA da main | Parecer de ciência, fonte e software |
|---|---|---|
| #239 | `184111fb` | J2 FIT-only vs quadrático nos mesmos heldouts secundários; G25-F1 encontrou falta de veto da fronteira cronológica entre validation/evaluation. |
| #241 | `40c543e4` | 78 camadas hipsométricas NOAA Recife 7–9/11 com resíduos de modelo seco, não erros instrumentais nem transferência a Conde. |
| #240 | `4da82a60` | IBGE 1991 fundamenta malha nominal 1960; não comprova fronteira legal 1963. |
| #243 | `f3de342f` | Tamanhos de registros COS Y20175 com uma linhagem NCAR; payload não é sondagem decodificada. |
| #244 | `be5cde88` | Posto da RAAN em modelo S1 com gauge; âncora calibrada apenas contrafactual e sem nova observação. |
| #246 | `69ba0ef8` | Paths de trigger do quadratic workflow; testes locais de paths, sem tornar CI comprovação de ciência histórica. |
| #245 | `8f6510b3` | Reruns sintéticos de r/v com mesmas perturbações e refinamentos; nenhuma calibração instrumental/posterior. |
| #247 | `a0099281` | Correção G24 do antimeridiano e testes sintéticos; documento histórico e órbitas não alterados. |
| #248 | `6e2686c0` | Cadeia IBGE CGEO-10 anexada ao grafo com hipótese de limite ainda latente, sem coordenadas legais fixadas. |
| #250 | `8ee2d894` | Contrato SSG Rust/Pages; alteração documental, não atestação do artefato entregue por HTTPS. |
| #252 | `5135501f` | Gestos touch e camadas 527/529 no SVG; vizibilidade de cenário não implica sobrevoo observado. |
| #253 | `886e5b9f` | Capítulos 01–02 reescritos para leitor com distinção entre notícia Tupi/FBIS e data NASA; checagem de prosa sem novas afirmações terminais. |
| #255 | `609b352d` | COSPAR 1963-003A/B/C e NORAD 527/528/529 em fontes secundárias + NASA dia catalogado; não identificação física de fragmento. |

## Achado material G25-F1: a fronteira do holdout não era realmente verificada

A [issue #261](https://github.com/franklinbaldo/conde-incident/issues/261) acompanha a correção. A PR [#239](https://github.com/franklinbaldo/conde-incident/pull/239) acrescentou `tools/raan_p3_quadratic_pair.py` e verificou o crescimento de tempo apenas *dentro* de cada bloco. Construí um **controle SINTÉTICO**: repliquei uma época válida de `validation` como primeiro dado de `evaluation` do 528, com observações, resíduos e fingerprints mantidos iguais nos dois modelos. O comparador anterior **aceitou** os oito alvos de evaluation, apesar da época sobreposta. Não são dados de 1963 nem uma fraude histórica: é contraprova da implementação.

A correção exige a separação cronológica especificada no contrato congelado C241-L3: **validation de 01/08 a 30/09/1963 (UTC)** e **evaluation de 01/10 a 31/12/1963 (UTC)**, além da ordenação e do mesmo epoch entre modelos já exigidos. Dois testes adversariais cobrem duplicação entre blocos e datas do lado errado do corte. O cálculo dos valores físicos não muda para entradas válidas; o gate agora falha em dados inconsistentes, sem alterar Parquet, matriz ou priors. Isso não autentica o corpus secundário nem torna o holdout cego.

## Revisões separadas e limites

- **Documentação:** NASA/Goddard 15/11/1963 p. impressa 8 sustenta *dia catalogado* 08/11 para 1963-003B; não informa hora/lugar/fragmento. FBIS/Tupi preserva relato atribuído, não observação física independente. Não rebaixar o silêncio do catálogo a prova de inexistência.
- **TLE e genealogia:** #255 documenta rótulos NORAD/COSPAR em catálogos secundários, sem mecanismo/massa/sensores originais. O conflito RAAN 198,5261° vs 284,1520° continua sem origem primária esclarecida. NOAA Recife (#241), NCAR (#243) e IBGE (#240/#248) não são três medidas do campo de queda em Conde.
- **Lean e Θ:** não houve arquivo `.lean` modificado. Provas do modelo existente são implicações condicionais, não prova de reentrada; domínio físico historicamente admissível não demonstrado como reduzido. `lake build` local **NOT_RUN**, workflows PR do GitHub verificados separadamente dos documentos externos.
- **Modelagem numérica:** #239/#244/#245 expõem comparação retrospectiva, gauge e ensemble seedado sem calibração instrumental, likelihood ou posterior; erros internos não são intervalos históricos de impacto.
- **Reportagem e UI:** capítulos 01–02 da #253 distinguem notícia e catálogo com linguagem para o público; #252 remove captura de scroll móvel e filtra conexões apagadas. SVG e CI não atestam sobrevoo observado. Disponibilidade HTTP não é prova de digest dos bytes de deployment.

**CI dos autores:** a consulta GitHub às execuções `pull_request` associadas a cada HEAD autoral retornou de **16 a 17 SUCCESS por PR**, sem falhas nas primeiras páginas consultadas. Trata-se de checks computacionais no HEAD, *não* validação das premissas físicas; workflows `push` após merge não foram contados nesse resultado. Teste sintético original demonstrou falha; código corrigido e dois novos testes passam localmente. Verificação do CI **desta PR** e do SHA final deve ser relatada à parte.

**Resultado:** `CONDE_INDETERMINATE`. Sem leitura independente nesta rodada dos bytes de fac-símiles NASA/FBIS, Parquet, NOAA, IBGE ou fichas NORAD históricas; não se fez contato externo nem publicação. Próximo teste factual: recuperar observação original do NORAD 528 com época, referencial, estação, erro e linhagem, testar contra 527/529 e decidir o conflito RAAN sem médias de fontes incompatíveis.
