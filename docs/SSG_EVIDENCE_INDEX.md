---
type: Guide
title: Índice documental JSON determinístico para SSG
description: Contrato de custódia e geração sem backend para busca opcional no site Conde.
---

# Dados estáticos, sem criar outra matriz

`tools/export_ssg_evidence_index.py` lê somente `public/data/conde-source-citations.json` e `public/data/conde-declared-dependence.json`. A saída é um manifesto e shards JSON de no máximo 12.000 bytes em `public/data/conde-evidence-index/`. Cada shard recebe SHA-256 em manifesto; as duas fontes originais também recebem hash de seus bytes, e o SHA-1 do snapshot imutável da matriz é preservado.

O script **não inventa status nem testemunhos**: exporta `source_status` literalmente, `snapshot_ref`, `row_sha256`, identificador de fonte, família, obra, localizador, citação, relação, limites, genealogia declarada e `archive_path` para página SSG existente. `independent_physical_observation_count` permanece `null`. A falta de aresta de proveniência não significa independência. O campo `post_matrix_ids_not_in_curated_index` declara explicitamente que os registros posteriores ao snapshot ainda não estão nas páginas curadas. `unmapped_matrix_occurrences` impede alegar cobertura completa.

A jornada sem JavaScript continua no arquivo documental gerado por `scripts/ssg-documentary-archive.mjs`; o manifesto é **um índice de leitura por máquina**, destinado a Raposa (integração) e Morcego (auditoria de navegação), e não uma segunda interface. Abelha deve revisar as regras de consistência genealógica antes de ampliar a cobertura.

Reproduzir com `python3 tools/export_ssg_evidence_index.py --check` e `python3 -m unittest discover -s tests -p test_ssg_evidence_index.py`. Para atualizar após mudança canônica: executar o script sem `--check`, revisar os diffs e submeter PR com CI no SHA final. O workflow Pages executa a checagem antes de preservar `public/data/` para publicação; `ssg check/build/audit` e Prek/OKF continuam como gates separados.

## Ponte verificável JSON → SSG (Lagarto)

`node scripts/verify-ssg-evidence-index.mjs` confere os hashes e tamanhos dos shards, a correspondência literal dos atributos documentais, genealogias, IDs e as rotas individuais `archive_path` com páginas geradas pelo SSG sem JavaScript. Também exige links reversos para fontes, obras e famílias. `node --test tests/ssg-evidence-index-bridge.test.mjs` inclui contraprovas com digest recalculado, rota inexistente e falsa promoção de status. Após `ssg build`, `node scripts/verify-ssg-evidence-index.mjs --built-site` verifica cada HTML da edição real, em vez de supor que o Markdown gerado virou rota publicada. O verificador não identifica sensores independentes, não autentica documentos externos nem valida uma queda.

## Percurso documental auditável (Lagarto, 13/11/2026)

Cada ocorrência apresenta literalmente o código source_status da fonte canônica
(classificação documental, **não** comprovação de impacto), digest row_sha256,
localizador e origem HTTPS. O verificador agora exige no HTML realmente compilado
links clicáveis: índice → ocorrência → documento original e linha imutável da
matriz; ocorrência → família/obra/fonte → ocorrência. Um endereço impresso sem
âncora não satisfaz o gate.

Este percurso usa somente os dois feeds canônicos versionados; não cria
outro catálogo nem observações físicas. Testes adversariais abrangem URL inerte,
status ausente, retorno quebrado e linha imutável sem link. O fixture HTML
sintético valida o auditor; somente o workflow Pages no SHA exato valida o SSG
Rust real. Acessibilidade por teclado e viewport 320 px permanecem para o Morcego.
