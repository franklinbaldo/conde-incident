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
