---
type: Guide
title: "G19 — auditoria retrospectiva dos 13 merges"
description: "Relatório de auditoria científica, documental e editorial sobre 13 squashes e proteção Pages."
---

# G19 — auditoria retrospectiva de 13 integrações da `main`

**🦅 Responsável:** Gavião · **Data:** 12/11/2026 (America/Porto_Velho) · **Issue:** [#16](https://github.com/franklinbaldo/conde-incident/issues/16)

**Corte histórico congelado:** `dfefa93be7a3e6361c7a0ce35fa196d0ef036a65` → `9e6596c679985b2cc886e31d88969fd9eab16b18`. A API de comparação GitHub confirmou `ahead=13, behind=0`. A cadeia first-parent foi conferida contra `GET /commits?sha=<head>`, com exatamente 13 ancestrais sucessivos; cada commit foi vinculado a uma PR **pelo `merge_commit_sha`**, não por suposição a partir de referências a issues no título. São **13 squash merges, zero commits diretos**. O inventário integral (SHAs, pais, PRs, 58 paths alterados, 13 HEADs autores e CI) está no [manifesto JSON](gaviao-main-window-20261112-1136.json).

Ordem fechada: **#134** → **#135** → **#138** → **#137** → **#139** → **#140** → **#141** → **#143** → **#142** → **#144** → **#145** → **#146** → **#147**. Nos HEADs autores, o GitHub Actions retornou **9/9 workflows SUCCESS em doze PRs e 10/10 na #141**. Isso é resultado de checks nos commits de origem, não prova histórica. Nenhum `stories/*.md` foi integrado neste intervalo. A PR editorial [#149](https://github.com/franklinbaldo/conde-incident/pull/149) continua draft e foi observada separadamente. Das PRs fechadas sem integração, #10 e #74 antecedem a janela; #22 foi fechada às 15:26 UTC, **depois** do HEAD congelado às 15:22 UTC, não sendo merge perdido.

## Quatro eixos, com limites

**Documentos e dependências:** #135 restaura a ocorrência pós-matriz `NARA-BB-CONDE-20261112-01`. #142 acrescenta curadoria C232–C235 e #147 rejeita escopos documentais inventados e IDs de imagens NARA incoerentes. Na main congelada, o grafo contém 10 famílias, 22 fontes, 29 citações curadas e o adendo NARA preservado. Validação de consistência do catálogo e hashes *declarados* não substitui reabrir os bytes de cada fac-símile. #145 incorpora **15 localizadores de filmes RU301, não 15 observações do NORAD 528**; fichas e fotogramas seguem não inspecionados. #139 reporta SHA e 117.264.384 bytes de Y20175, mas continua `NOT_DECODED`; não se deduz nenhuma sondagem em novembro. #140 adiciona legislação e memorial de perímetro: geometria moderna não prova o município de 1963.

**Lean e restrições:** #138 introduz contraprovas de unidade, operador e objeto em dados NASA SSR. #142 propaga vínculos documentais para `Documentary.lean`. Nenhuma verificação sintática ou prova em Lean 4.35.0 confirma as hipóteses históricas dos importadores. #137 demonstra a não-identificabilidade algébrica de um modelo hipotético com três fases livres e viés compartilhado (posto 3 para quatro parâmetros); não identifica o viés real nem uma trajetória. O conflito RAAN **284,1520° vs 198,5261°** continua sem conciliação instrumental, de época e referencial.

**Cálculo e condições físicas:** #141 compara proxy secular J2 sem ajuste ao baseline de RAAN estática em apenas três pares elegíveis de 528 e três de 529, todos do **mesmo espelho secundário**. Para 528, MAE angular 0,450602° (estático) vs 0,048824° (J2); para 529, 0,322360° vs 0,140853°. Isso não é erro contra verdade orbital. #134 registra oito janelas UTC de Ap/Kp como entradas **condicionais**, não uma distribuição da hora de reentrada. #144 implementa interface para drivers GFZ/NRCan nos estágios RK4, ainda sem densidade local autenticada, modelo de erro e estado orbital original. Nenhuma dessas fatias ativa restrição física que estreite `Θ` com testemunha de não-vazio.

**Editorial, UI e CI:** #146 melhora deep links do laboratório, não comprova Caderno servido em Pages. #143 amplia o pré-gate read-only contra mudanças entre snapshots; foi objeto de contraprovas adicionais. No corte, `has_pages=false`, portanto não declarar publicação. Também permanece aberta a migração de instruções de Zola para SSG, sem afirmar que a PR #3 está pronta.

## G19-F1 — contraprova de identidade de tentativa/status (corrigida nesta fatia)

O verificador original da #143 só comparava `id/head_sha/status/conclusion` do workflow entre os dois GETs. **Uma reexecução do mesmo run**, com `run_attempt: 1 → 2` e os outros campos iguais, não invalidava o parecer de metadados. Da mesma forma, uma **nova entrada de status** do mesmo deployment com `id: 501 → 502`, ambas `state: success`, era aceita. São mudanças de evidência de controle durante o scan que contradizem a promessa de identidade estável. A correção exige identificação positiva e igualdade de `run_attempt` e `status.id`, com quatro testes adversariais novos e o restante da suíte mantido. É um **controle sintético de corrida**, não um registro de que tal corrida ocorreu no GitHub real.

O pré-gate continua podendo responder no máximo `METADATA_ONLY_SITE_NOT_VERIFIED`, nunca `PUBLISHED`. Uma mudança após o segundo GET ainda é uma limitação inerente. A aprovação do GitHub Actions da PR será conferida no SHA real antes de qualquer merge.

**Estado científico:** **Conde indeterminado.** A NASA registra apenas o dia 08/11/1963 para o decaimento catalogado, não hora ou lugar; FBIS/Tupi é genealogia de notícia, não comprovação física. Não há órbita terminal autenticada, densidade calibrada ou holdout instrumental que permita exigir ou excluir Conde. Fonte original não reinspecionada nesta rodada é indicada como tal, sem elevar sua verificação. O blog pessoal não foi alterado.

**Próxima dúvida:** recuperar ficha RU301 identificada, registros de origem 527/528/529 e erros de tracking; verificar se a reconciliação física permite construir predicados dimensionados de `Θ`; continuar primeiro-parent a partir do SHA de corte acima, inclusive a própria correção G19 quando integrada.
