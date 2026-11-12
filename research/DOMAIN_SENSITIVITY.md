# Diagnóstico de quais restrições realmente estreitam o domínio

**Escopo:** auditoria lógica/aritmética sobre os contratos das PRs #37 e #43, não uma análise orbital. Mantém cenários RAAN de origem não reconciliada separados e nenhuma conclusão sobre Conde.

Execute: node scripts/audit-domain-sensitivity.mjs arquivo.json

O arquivo pode obedecer a conde.admissible-domain/v1 ou conde.alternative-domains/v1. Cada intervalo é processado pelo motor de racionais exatos já testado na #37. Antes de qualquer diagnóstico, o programa valida a totalidade do registro, inclusive ID, ocorrência, fonte, cadeia, status Lean declarado e premissa.

- Em domínio não vazio, individually_pivotal identifica a restrição cuja remoção isolada alargaria o intervalo final. not_individually_pivotal NÃO significa inútil: restrições redundantes/coincidentes podem importar conjuntamente.
- Em intervalo vazio, deletion_minimal_conflict é uma sublista de restrições que ainda gera a contradição e da qual nenhuma restrição pode ser removida sem restaurar um intervalo não vazio, sempre considerada a faixa inicial declarada. Não há garantia de cardinalidade global mínima nem autenticação empírica.
- No contrato de cenários alternativos, todos os diagnósticos são feitos separadamente. Uma contradição de cenários apresentados não prova exaustividade do catálogo, exclusão geográfica, trajetória ou impacto.
- Saídas marcadas DECLARED_NOT_AUDITED / NOT_VERIFIED / NOT_RUN jamais devem ser chamadas de prova Lean, calibragem física ou dado observado. O diagnóstico é sensibilidade de PREMISSAS e serve para pedir à Tartaruga custódia do dado influente, ao Polvo formalização condicional e ao Castor holdout de hipóteses independentes.

Critérios: testes sintéticos de limites ativos, redundância, par inconsistente, conflito com o intervalo inicial, dois parâmetros, frações decimais arbitrariamente precisas, provenance, falsa prova Lean, cenários RAAN separados e CLI 0/1/2. Workflow Alternative evidence scenarios executa essas suítes no SHA do ramo; no merge, exige revisão independente do 🦅 Gavião e CI verde no HEAD.

**Proveniência da decisão:** AGENTS.md e team/elefante.md de main consultados em 12/11/2026; matriz cumulativa C01–C238 na PR #1 consultada, com C197 corrigida pela PR #61, e contradição RAAN listada no documento. Dados de NORAD 527/528/529 são secundários/contestados e não entram como intervalos numéricos neste código. Fonte: https://github.com/franklinbaldo/conde-incident/pull/1 e https://github.com/franklinbaldo/conde-incident/pull/14. Nenhum dado histórico novo nem página publicada.
