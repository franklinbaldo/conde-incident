---
type: Guide
title: "🦅 G29: retrospectiva de 15 integrações e correção de custódia"
description: "Auditoria SHA por SHA de G28 até HEAD, achado de atribuição documental e limites de inferência."
---

# G29: auditoria retrospectiva

**Corte imutável:** `0031f2a894fcbf6b2c59fb2d80d0f31a3d95e099` → `b3a632d6da60c9b054473b89211579cbb488d525`, 12/11/2026, 20h47–21h41 (UTC−04). **15 integrações primeiro-pai; 14 squash e um merge convencional (#314) contendo três commits laterais, total 18 DAG; zero commits diretos.** [Manifesto integral](gaviao-main-window-20261112-g29.json) guarda SHA, pais, PR, HEAD de autor, arquivos, CI e notas científicas para todos os 15.

## Parecer por integração

- #309 `499acbae`: taxonomia GCAT/KeepTrack de 527/528/529 não identifica a peça material nem fornece observação independente.
- #311 `b0728ef0`: terceira época de RAAN é contrafactual racional exato, sem erro angular, observação e fonte instrumental.
- #312 `0b9d6daf`: correção G28 mantém exceção mutável ao limite 20 KB restrita ao `bun.lock`.
- #313 `0941c9a6`: CI para eventos duplicados; não é autenticação de fonte.
- #314 `0caf16da`: catálogo, captura e auditoria do manual ON20 são documentos dependentes; 1964 não valida layout 1963.
- #315 `39c0ab05`: fotografias com câmeras de 2022 não estabelecem centro municipal/posição de impacto em 1963.
- #316 `28610ff6`: inventário IGRA 1982–1992 não prova sonda, altura ou posição de sensor em Recife 1963.
- #317 `391477f9`: dois replays Wayback 2021/2023 preservam bytes de PDFs; não são novas observações. NASA teve negativo de busca só por URL exata.
- #318 `9049542a`: Lean e JSON ON20 ligam manual 1964 a Y20175 1963 como candidato sem layout/vento decodificado.
- #320 `013ae48e`: TEME→ECI exige R(t), Rdot(t), fonte, época e incerteza; controles sintéticos não são dados de rastreamento.
- #321 `7830cf9c`: remove dependências Google Maps inativas; nenhuma alteração observacional.
- #319 `60757195`: reconcilia ON20 com custódia canônica da Abelha, sem ativar ponte física.
- #322 `274840b6`: painel Wayback **atribui incorretamente NASA a qualquer busca negativa**. Achado G29-F1 corrigido nesta PR.
- #324 `b34603b8`: Coruja confronta relatório NORAD com RU301; 17 câmeras e 15 filmes SC-8 não provam foto de NORAD 528.
- #325 `b3a632d6`: duas tabelas GCAT compartilham linhagem; nome Agena B do 527 e rótulo Agena D de 528/529 não comprovam hardware.

No #314 foram alcançados os três commits laterais `0643fb1c`, `935fbfb2`, `75d2f7de`, não contados como commits diretos. Busca por PRs fechadas sem integração no recorte retornou zero (resultado de consulta, não ausência perpétua).

## G29-F1: contraprova de atribuição

O painel `DocumentArchive.tsx` percorre registros `NO_EXACT_CAPTURE_IN_QUERIED_INDEX`, mas exibia título fixo **NASA SSR 15/11/1963**. Uma linha negativa hipotética de outro arquivo apareceria falsamente como NASA. A correção recupera `source_type` da própria ocorrência e recorre ao ID em caso de título vazio. Testes adversariais incluem uma fonte não NASA e fallback, sem alterar dados históricos.

## CI, ciência e limites

Todos os 15 HEADs autorais tiveram CI `pull_request` SUCCESS (16 ou 17 workflows). Quatorze integrações tiveram `push` integralmente verde; a #316 registrou **16 SUCCESS + Pages CANCELLED**, sem contabilizar como verde integral. Testes de regressão G29 executam no HEAD autoral da correção; consultar workflow pelo SHA e registrar o resultado antes de eventual merge. Fontes externas e `#print axioms` independente **NOT_RUN** nesta rodada. Lean compilado certifica apenas a construção condicional; J2/SGP4 não representam holdout terminal. O conflito de RAAN 284,1520° vs 198,5261° continua sem fonte original que o resolva.

**Resultado:** `CONDE_INDETERMINATE`. Não se identificou instrumento, época terminal, coordenada de impacto nem estreitamento validado do domínio de parâmetros. A auditoria posterior não dispensa os testes de autor; o blog pessoal não foi alterado.
