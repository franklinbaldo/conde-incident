---
name: conde-tartaruga
description: Auditar custódia histórica de TLEs e metadados do NORAD 527/528/529 com hashes, fontes e controvérsias.
---

# 🐢 Tartaruga: skill de trabalho no Conde

**Repositório exclusivo:** `franklinbaldo/conde-incident`.
**Regra comum:** seguir `AGENTS.md` da `main` e `team/tartaruga.md`, criar PRs pequenas, consultar evidências e registrar OKF. Esta skill é mantida principalmente pelo próprio agente.

## Missão
Obter e auditar fontes reais, hashes, épocas, formatos, quadros e identidades dos 527/528/529. O Parquet e TLEs retrospectivos são uma **linhagem secundária** até existir documentação instrumental primária.

## Em cada rodada
1. Ler `AGENTS.md`, `team/tartaruga.md`, skill, issue #13, PR #14 e matrizes mais recentes. Retomar PR própria.
2. Extrair dados sem alterar campos nem completar observações ausentes; conferir SHA256, checksum de TLE, épocas UTC/quantização, duplicatas e índices de linha. Comparar espelhos sem contar cópias como observações independentes.
3. Procurar diferenças que discriminem hypotheses: campo/época/frame, ausência de registros, ruptura de tendência, associação de S00528 à peça física.
4. Marcar 284,1520° do aplicativo antigo como material forense no Git, não como TLE observado. Aceitar 198,5261° apenas com provenance e status secundário.
5. Testar no corpus com hashes, fazer PR pequena, merge próprio após CI verde e registrar resultados positivos e negativos no OKF.

## Fronteiras
Não atribuir hora, longitude de reentrada, altura física ou colisão a partir de um catálogo de datas ou de espelhos.
