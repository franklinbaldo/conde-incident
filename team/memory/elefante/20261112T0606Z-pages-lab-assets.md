---
id: elefante-20261112-pages-lab-assets
agent: elefante
date: 2026-11-12
scope: franklinbaldo/conde-incident
issue: 6
kind: integration-memory
status: proposed-not-merged
---

# 🐘 Publicação: laboratório HTTP 200 não basta

## Contexto lido e estado retomado

- Contrato vigente na main: `AGENTS.md`, `team/elefante.md`; issues/PRs abertas e matriz cumulativa C01–C238 na branch da PR #1 (`research/evidence_matrix_C001-C238_2026-11-11.md`).
- Retomada da issue #6 e da sequência #7 → #33 → #46 → #49 → #52. A #52 segue draft e não foi integrada; esta fatia foi isolada em branch filha, sem alterar branches de terceiros.
- Pages na main não está verificado; a PR #3 ainda gera Zola, enquanto #22 exige SSG Rust. A #1 contém evidências e App/Navigation; exigem reconciliação para preservar ambas seções.

## Achado, verificação e correção

- Problema: o auditor podia certificar a presença da página de laboratório, mas não a disponibilidade do JavaScript e CSS que ela referencia. HTTP 200 do index não garante carregamento do bundle.
- Código: `scripts/check-pages-release.mjs` agora lê referências externas de script e stylesheet, limita 20 recursos, consulta somente paths locais canonizados, confere HTTP 200, tipo MIME e corpo não vazio; URL malformada/duplicada/faltante rebaixa para NOT_VERIFIED.
- Testes em `scripts/check-pages-release.test.mjs` incluem 404, HTML fallback, CSS ausente, MIME, URL externa/traversal, duplicatas e parser de atributos. Estes são cenários **sintéticos de integridade de publicação**, não observações de 1963.
- Documentação revisada: `research/PUBLICATION_AUDIT.md`. Os resultados do CI e SHA final serão apontados na PR, sem antecipar aprovação.

## Proveniência, independência, grau de verificação

- Fontes operacionais: [API Pages](https://docs.github.com/en/rest/pages/pages), [API Deployments](https://docs.github.com/en/rest/deployments/deployments), [Vite public base](https://vite.dev/guide/build#public-base-path) e PR #52. Independência: ferramentas e HTML são do mesmo pipeline; não constituem atestação externa dos bytes nem prova de origem histórica.
- Grau: implementação proposta com testes de contraprova, **aguardando CI no SHA final e parecer independente do Gavião**. Não equivale a deploy público.
- Pesquisa: NASA 15/11 p.8 confirma somente data de decaimento de 1963-003B; conflito RAAN 284,1520° vs 198,5261° permanece sem custódia primária resolvida; C197–C202 registram correção documental. Nenhuma inferência de local/horário de impacto nesta rodada.

## Fila científica e dúvida seguinte

- Custódia TLE 527–529/RAAN #13/#14, prioridade 95; restrições Lean condicionais #15/#17 e método #28, prioridade 90; holdout 529 #19/#20, prioridade 85; integração física #4/#5, prioridade 80. Não reduzir domínios por RAAN conflitantes tratados como simultâneos.
- Próxima dúvida: como vincular hashes dos bytes JS/CSS renderizados pelo SSG/Vite ao artefato Pages do SHA de `main`, e como verificar execução real do laboratório sem substituir testes físicos pelos testes de entrega? Demandas prévias: SSG Rust na #3, compatibilidade de navegação #1, revisão independente e CI.
