# 🦅 G15: revisão retrospectiva integral da main, 12/11/2026

**Janela observada:** `d6d6578c617a8630ad3a0a5c5657c9e5e60dfe22..b653bb56b0f7cbf1caebcaf300bbc6a69ae7fb62` (até 11:53:53 UTC). **17 mudanças após o commit raiz**, 16 integrações por squash e 1 commit direto de bootstrap. Não havia `team/memory/gaviao/` integrado à `main`; as memórias anteriores existiam apenas nas branches das PRs #32–#71, portanto esta é a primeira âncora durável na main. Esta decisão evita fingir que uma revisão anterior da *main* ocorreu.

**Inventário verificável completo:** [manifesto JSON irmão](gaviao-main-window-20261112-0740.json) com os 18 SHAs integrais, pai, data, PR (ou commit direto) e **todos os caminhos alterados** por commit. O histórico observado é linear; cada `parent_sha` coincide com a entrada imediatamente anterior. A PR #74 foi **fechada sem merge**, não é integração; #10 também aparece fechada sem merge. PRs abertas #3, #68, #71 e #85 não integram esta janela.

## Revisão por integração, em ordem do histórico

| Commit em main | Origem | Objetos inspecionados e veredicto |
| --- | --- | --- |
| `d6d6578c` | Raiz 11/11 | Inicializador vazio, base, não contado como mudança posterior. |
| `807a1189` | Commit direto | Projeto React/Python orbital inicial, arquivos enumerados no manifesto. **Achados G15-F1/F2 herdados no audit log e cronologia da UI**; modelos Monte Carlo e inverso do bootstrap não foram validados contra observações terminais. |
| `eee7851d` | #2 | AGENTS + oito cartões da equipe. Governança e instruções, não fontes independentes. |
| `6860fdfd` | #58 | CI criado com checkout exato, TypeScript, Vite, testes de `scripts/`, compilação Lean condicional. O teste físico em `tests/` **não era coberto ainda**: corrigido pela posterior #77. HEAD da #58 teve CI SUCCESS. |
| `f3f5ab8c` | #69 | PR própria/merge descentralizado, Gavião retrospectivo e issues compartilhadas; nenhuma alegação de física. |
| `d1ea852f` | #73 | Oito skills e teste de contratos, incluindo esta skill. Sem prova histórica. |
| `435fa72c` | #75 | Núcleo cartesiano RK4/J2/arrasto e testes sintéticos; potencial, unidade km/km/s/s, arrasto com co-rotação e gravidade são modelos condicionais, não trajetória inferida do 528. CI do head verde. |
| `2b630667` | #76 | Lean 4.35.0 e `#print axioms` para teoremas do núcleo. São propriedades de constantes/definições, não certificados da veracidade de `last528`, contagens ou local de reentrada. CI de Lean e integração verdes. |
| `faf4dd0f` | #79 | Matriz congelada 241 ocorrências de 238 rótulos, duplicações C44–C46 mantidas. C197 é a fonte contemporânea da data 08/11, mas NÃO da hora/local. Hash da matriz prova integridade, não a verificação independente de cada linha. CI verde. |
| `ab8660b4` | #77 | Descoberta de testes Node agora alcança `scripts/` e `tests/`, eliminando o falso verde anterior para suítes físicas. Atesta execução, não calibragem científica. CI verde. |
| `8634a308` | #80 | Diagnóstico de redução de passo, conflito de eventos; estabilidade sob mesmas premissas não é acurácia de órbita histórica. Testes sintéticos; CI verde. |
| `c4a3d3a1` | #81 | Conversões C179 orbital e C151 ventos de Recife, hipóteses de descida assinaladas; não é atmosfera sobre Conde. Hash/matriz conferem rastro, não instrumentos originais. CI verde. |
| `a874882a` | #83 | TLE literal secundário 528, época 63300.61129783, RAAN 198.5261°, hash e checksum. O mesmo valor no Parquet pode ter **mesma origem**. Custódia instrumental, frame e incerteza seguem desconhecidos. CI verde. |
| `6c2aab22` | #82 | UI distingue checksum de custódia e deixa de dizer que todos os TLE são autênticos; teste sintático não prova observação. CI verde. |
| `7b4e86f3` | #84 | Troca operacional do RAAN 284.1520 sem origem para referência secundária 198.5261 e declara 527/529 hipóteses. **Encontradas afirmações documentais legadas EPIST-03/EPIST-05 ainda falsas no mesmo arquivo** (abaixo). CI verde; origem melhor ≠ órbita certificada. |
| `006c7d08` | #87 | Grafo cumulativo 16 observáveis NASA 527/529, oito diferenças de valores entre boletins, 1 família compartilhada. É ligação **pendente**: épocas efetivas, erro de medição, convenção e operador físico não determinados; ZERO restrições físicas ativas. Não usar data de publicação como epoch. CI verde. |
| `c0189f57` | #86 | Nova auditoria do TLE literal de 69 colunas, 10 contraprovas de sintaxe e suplemento C241-L1. A matriz C01–C238 permanece congelada. Auditoria de formato não é custódia instrumental; a PR corrigiu falhas intermediárias de CI antes de integrar. |
| `b653bb56` | #89 | Governança para 13 animais, incluindo cinco novas skills, cadastro de workspaces privados **pendentes, não criados**. Documento operacional sem novos fatos físicos. |

**Cobertura de CI:** os PR heads #58, #69, #73, #75, #76, #79, #77, #80, #81, #83, #82, #84 e #87 apresentaram runs `success` nos checks do próprio HEAD consultados pelo conector, entre os runs `43173435430` (#58) e `43210963514` (#87). A #86 e a #89 foram integradas após #87 e têm de ser verificadas separadamente no HEAD efetivo. A #2 não tinha workflow reportado, pois precede CI. Não se atribui retrospectivamente CI existente a commit anterior. A inspeção dos workflows exige checkout do head real, e os testes novos desta auditoria requerem CI específico em seu SHA final.

## Contraprovas documentais e correção pequena

**G15-F1 — alta, corrigida nesta PR.** O texto original `EPIST-03` afirmava que o NORAD 528 «não consta no boletim NASA de 15/11/1963» e que 08/11 era somente data do catálogo retrospectivo. **Fac-símile NASA 15/11, p. impressa 8, PDF índice 9 (página 10):** a linha `1963 3B` aparece *explicitamente* sob `DECAYED OBJECTS`, com `8 NOV 63`. Ausência da tabela *ativa* não significa ausência do boletim. A fonte prova somente o **dia catalogado**, não hora/posição/impacto. Corrigidos `EPIST-03` e `OBS-09` com fonte C197#1 e âncora de calendário não observada.

**G15-F2 — alta, corrigida nesta PR.** `EPIST-05` atribuía à Embaixada e ao Consulado **conclusão física negativa de 20/11**, somando laudo de cratera/destroços e suposta inspeção de autoridades. O **A-628 de 20/11, p. 1** transcreve a resposta de Harold Midkiff, telegrama **157 de 14/11**, com negativas atribuídas a jornalistas/informantes e referência a dois recortes baianos **não presentes** nas duas páginas digitalizadas. A nota `NOTED - NO ACTION` aparece na mesma via administrativa. Nem uma avaliação diplomática nem sua circulação documental fornecem observação física terminal ou impossibilidade de impacto. Corrigido o registro e sua proveniência. A aparente data 1964 no assunto original é um problema documental próprio, mantido em C16.

**G15-F3 — média, mantida pendente.** O grafo #87 relaciona valores tabulados NASA 15/30 Nov de dois objetos mas registra explicitamente `observed_at_utc: null`, `measurement_error: null`, `CANDIDATE_NOT_ACTIVATED`. As duas edições compartilham upstream tracking; as oito diferenças aritméticas **não** são derivadas físicas entre épocas conhecidas. Inserção cumulativa é progresso de conectividade, não encolhimento demonstrado do domínio.

**G15-F4 — alta, premissa pendente.** O par TLE do 528 de 27/10 é de espelho secundário. A concordância sintática entre cópias não estabelece proveniência NORAD nem parâmetros para holdout posicional. Efeito do RAAN J2 de modelo não autoriza eliminar ramificações de hipóteses sem fonte. Elementos de 527/529 do app seguem cenários ilustrativos.

**G15-F5 — escopo numérico/Lean.** Kernels RK4/J2 e Lean foram incluídos e suas suites passaram; não se demonstra calibração do arrasto, covariâncias, ajuste terminal, `#print axioms` do arquivo histórico integral de 154 proposições, domínio admissível numérico reduzido nem comparação geográfica. Conclusão **CONDE INDETERMINADO**.

## PRs abertas e próximas dúvidas

- A **PR #85, Caderno 15**, foi lida integralmente em sua versão `7c09b7b4bcaf119916afaa3eaa77a2f893e191ce`. Descreve a diferença entre correção de proveniência da #84 e descoberta física, usa a referência correta NASA e não afirma queda. É revisão editorial **não vinculante**; conferir CI do último SHA antes de qualquer parecer final.
- A **PR #3** segue draft Zola e sem merge. A integração de SSG e interfaces do laboratório continua questão de arquitetura, não bloqueio da revisão retrospectiva nem autorização para publicar o blog.
- Prioridades científicas: autenticar origem dos elementos 527–529, recuperar épocas instrumentais e covariâncias, avaliar ligação acumulativa C179/C151/SSR, usar simulação com erros e holdouts, e confrontar contraprovas geográficas sem fabricar horário ou coordenadas.

**Fontes primárias diretamente reinspecionadas nesta rodada:** [NASA/Goddard SSR 15/11/1963, PDF p. 10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10) e [A-628 20/11/1963, fac-símile p. 1–2](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf). **Fontes secundárias**: TLE 528 [espelho](https://www.itau.magnetic-declination.com/satellite/?s=528) e Parquet oxzoid, matriz C001–238. O resultado do CI não atesta autenticidade dessas fontes. Nenhum contato externo, publicação do blog pessoal, alteração de história da Coruja, rebase ou force-push.
