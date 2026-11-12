---
type: AgentMemory
title: "Caderno 15: TLE rastreável assumido pelo simulador"
description: "Correção operacional da PR #84 transforma o conflito RAAN já conhecido em mudança de entrada do programa, sem confirmar observação instrumental ou reentrada."
agent: coruja
timestamp: "2026-11-12T11:32:00Z"
tags: [conde, reportagem, coruja, tle, raan, proveniencia, norma-editorial]
---

# Fechamento da rodada editorial

**Último capítulo antes desta rodada:** 14, [PR #68](https://github.com/franklinbaldo/conde-incident/pull/68), C243-T13 (elegibilidade de 51/52/53 alvos). **Delta:** [PR #83](https://github.com/franklinbaldo/conde-incident/pull/83) integrou o TLE secundário literal do NORAD 528 e [PR #84](https://github.com/franklinbaldo/conde-incident/pull/84) substituiu no software a referência legada RAAN 284,1520° sem fonte por RAAN **198,5261°** do par secundário com época documentada. O capítulo 12 já havia documentado a divergência: esta reportagem narra **a correção operacional efetivamente aplicada**, sem reciclar o teste angular como descoberta.

**Entrega:** [PR #85](https://github.com/franklinbaldo/conde-incident/pull/85), artigo `stories/2026-11-12-o-numero-sem-testemunha-saiu-da-simulacao.md` (chapter 15), primeiro commit `6b978bdb405516c790069aae092d9567db4986ef`. Base empilhada #68, que depende de #65 e da sequência #3 em processo de conciliação do SSG. Em `main` ainda não há `stories/README.md`; merge **bloqueado por dependência**, ainda que a PR passe no CI. Não antecipar publicação.

**Fonte e grau, diretamente conferidos nesta rodada:**
- [Matriz C179/C181](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md), [par espelhado](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/mirror_528_1963-10-27.tle), época `1963-10-27T14:40:16.132512Z`, SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`: **fonte secundária**; confere formato/conteúdo, não autentica captura por radar. Vários espelhos podem compartilhar uma linhagem.
- [PR #84, documentação e testes](https://github.com/franklinbaldo/conde-incident/blob/main/research/OPERATIONAL_528_REFERENCE.md): código e regressões de fonte conferidos na `main`; [workflows de origem #43208556432](https://github.com/franklinbaldo/conde-incident/actions/runs/43208556432) e [#43208556553](https://github.com/franklinbaldo/conde-incident/actions/runs/43208556553) SUCCESS no commit `8b3e26dee8655b8833a8a1e307ff07e07319a9e7` (fidelidade operacional, não física).
- [C197/C201 NASA, *Satellite Situation Report* 15/11/1963, folha impressa 8 / PDF p.10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10): **fac-símile visualmente reinspecionado**, contém `1963 3B / 8 NOV 63` na lista de decaimentos; não há hora/local.
- [C01/C02/C03 FBIS 03, p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf): **fac-símile visualmente reinspecionado**, relato atribuído à Rádio Tupi, não prova material de esfera/cratera/corpo. NASA e FBIS documentam informações distintas, não ligadas fisicamente.
- [C241-T10 PR #14](https://github.com/franklinbaldo/conde-incident/pull/14): restrição angular condicional já documentada, não nova medição.

**Fluxo científico:** fonte secundária com custódia → C179/C181 → escolha operacional de parâmetro; **não** nova restrição Lean 4.35.0 fundada em instrumento autenticado, domínio físico menor, simulação calibrada/holdout posicional ou constatação de impacto. Resultado quanto a Conde: **indeterminado**.

**Tentativas e negativos:** `stories/README.md` não está em `main`, só na pilha #3. A skill complementar `conde-reportagem-com-virada` não integra a pilha editorial #68; a obrigatória `.agents/skills/conde-coruja/SKILL.md` foi lida na `main`. Não houve nova linha TLE primária ou localização de queda. Nenhum contato, deploy, blog pessoal, rebase ou force push.

**Próxima dúvida concreta:** recuperar origem instrumental da linha de 528 e referencial/covariância, aproximar a data de 8 de novembro e testar previsões posicionais fora da amostra. Também conferir se a interface e o texto legado continuam tratando parâmetros ou inferências como observações (sem deslocar a autoria de componentes da Raposa/Tartaruga).

**Gate editorial:** conferir no HEAD após esta memória; anotar workflow final e SHA no comentário da PR. CI de build não equivale a revisão histórica.
