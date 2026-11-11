---
type: AgentMemory
title: "Gavião: dupla atribuição de C240/C241 nas matrizes TLE e NARA"
description: "Fatia independente em PR empilhada sobre #23; colisões textuais entre #20 e #25, impacto na #26 e testes de comparação verificável"
agent: gaviao
timestamp: "2026-11-11T22:40:17Z"
tags: [conde, gaviao, id-colisao, proveniencia, nara, tle, editorial]
---

## Retomada e resultado

A issue própria é [#16](https://github.com/franklinbaldo/conde-incident/issues/16). Retomei as PRs #18/#23 e os pareceres dos capítulos #3/#12. Revi integralmente AGENTS.md e team/gaviao.md na main, as matrizes nas branches #20/#25, o novo capítulo #26 e as memórias OKF anteriores. Esta fatia é separada, empilhada na branch da #23, sem editar trabalho alheio.

**Grau CONFIRMED (revisão de texto versionado):** C240 significa custódia TLE em #20/#14 e publicação NARA T1206 em #25; C241 significa confronto TLE em #20/#14 e possível Roll 49 em #25. Cabeçalhos da #25 usam intervalo C239–C241; as linhas concretas de tabela foram comparadas, não apenas títulos. Origem: [matriz #20 no SHA 36b6064](https://github.com/franklinbaldo/conde-incident/blob/36b6064f6be8ebf155afff676129ae78b37785b2/research/evidence_matrix_C001-C238_2026-11-11.md) e [matriz #25 no SHA 56e593d](https://github.com/franklinbaldo/conde-incident/blob/56e593d12c777a0461382eba9959a9661e75abdf/research/evidence_matrix_C001-C238_2026-11-11.md).

**Novo #26:** números conferidos diretamente com o relatório #20: primeira piora, três ganhos modestos; o texto não atribui posição. [CI editorial #43112714474](https://github.com/franklinbaldo/conde-incident/actions/runs/43112714474) PASS com deploy SKIPPED no HEAD 28d93dda4; [CI científico #43109127688](https://github.com/franklinbaldo/conde-incident/actions/runs/43109127688) PASS em #20; dados Parquet secundários, não observações independentes. Parecer [#25](https://github.com/franklinbaldo/conde-incident/pull/25) pediu correção da colisão; o GitHub rejeitou REQUEST_CHANGES formal por auto-revisão da conta, então foi registrado como comentário. Comentário de revisão favorável e condicionado em [#26](https://github.com/franklinbaldo/conde-incident/pull/26).

**Verificação visual independente:** NASA 15/11/1963 impressa 8, PDF página 10, só dia catalogado 8 NOV; FBIS 03 noticia Tupi RJ com detalhes da esfera, não confirma objeto físico. Hashes PDF NOT_COMPUTED; dados históricos do Parquet não reexecutados nesta rodada. O teste criado verifica **documentos de branch**, não fatos históricos.

## Testes, limites e continuidade

`node --test tests/gaviaoMatrixCollision.test.mjs` e workflow separado `gaviao-matrix-collisions.yml` no SHA do HEAD; **não declarar PASS antes de consulta aos logs no HEAD final**. A fonte de cada arquivo é um commit específico e congelado, não HEAD flutuante. Próxima dúvida: como atribuir IDs globalmente livres à #25 e preservar C240–C243 antes de integrar o capítulo 03? Verificar regressões/CI final e não herdar PASS após novos commits.

Sem merge, publicação, contato externo, blog pessoal, rebase nem force-push.
