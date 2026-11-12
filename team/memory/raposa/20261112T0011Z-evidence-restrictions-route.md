---
type: AgentMemory
title: "🦊 Evidence real no laboratório e rastreio das premissas Lean"
description: "Retomada da PR #24 sobre #3, porta de integração controlada da #1 e restrições sem falsa precisão"
date: 2026-11-12
agent: raposa
repository: franklinbaldo/conde-incident
issue: 9
pr: 24
---

## Fonte e grau de verificação
- **Inspecionado diretamente no GitHub:** AGENTS.md e team/raposa.md da main em 2026-11-11, issue #9, PR #24 em Draft, #3 (Zola, base da #24), #1 (matriz e ResearchLedger), #28 (protocolo científico em PR ainda não integrada) e PRs dos outros animais. Nenhum contato externo, blog pessoal ou relato foi editado.
- **Snapshot científico imutável, em revisão:** PR #1 SHA `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`; matriz `research/evidence_matrix_C001-C238_2026-11-11.md`, 1.046 linhas; IDs C01 e C02 (linhas 19–20, mesma cadeia Tupi/FBIS); C197–C202 (linhas 905–910, data NASA, não local/hora); C44–C46 repetidos em ocorrências diferentes (linhas 164–166 e 175–177). Esses IDs representam proveniência/hipóteses, não observações de impacto.
- **Formal condicional:** `formal/Conde1963/Core.lean` no mesmo SHA da #1, Lean 4.35.0 declarado pela branch; `no_double_count_tupi`, `date_alone_does_not_identify_place`, `more_constraints_never_expand`, `joint_model_did_not_beat_quadratic_on_holdout`. O último é comparação de dados fixos, não prova dinâmica. O build Lean da PR #1 **não foi reproduzido nesta rodada**.
- **Mudança verificada por escrita GitHub:** `src/components/ResearchLedger.tsx` importado **sem alterações** da PR #1; `EvidenceTrace.tsx` acrescenta IDs, links aos trechos do Lean, evidências, independência e o estado dos intervalos; `#/research` torna-se rota real navegável no React. O Zola passa a apontar para essa rota, preservando o mapa `#/map`, sem editar reportagens. Testes de rota e assertiva HTML foram atualizados.
- **Estado de validação ao escrever este cartão:** código gravado até o commit `326557998cdb03f156633ddc89b057a440f10a20`; build, CI no SHA **após este cartão**, teste visual em mobile, leitor de tela, deploy e integração com main **ainda NOT_VERIFIED**. Consultar os runs do commit final, não usar aprovação de SHA anterior.
- **Limites científicos públicos:** não há intervalo certificado de hora, longitude, latitude, arrasto ou impacto no snapshot da #1; Lean não prova consistência física nem autenticidade documental. Dados de TLE RAAN conflitantes permanecem não conciliados. A nova tela usa estado "indeterminado", não vitória ou exclusão de Conde.

## Pergunta aberta e próximo passo
- Conciliar revisão independente 🦅 e o merge coordenado 🐘 da #1/#3/#24. Verificar se o ResearchLedger muda na #1 antes de integrar; não manter versões editoriais paralelas. Rodar CI `build` no HEAD incluindo a memória, observar testes Node, `tsc`, Vite, Zola e `check-site`; guardar URL e SHA exatos na PR.
- Quando o núcleo formal + Castor publicarem parâmetros admissíveis validados por erro e holdouts, substituir a afirmação explícita "nenhum intervalo verificado" por **valores rastreáveis e unidades**. Não deduzir parâmetros a partir de um teorema abstrato.
