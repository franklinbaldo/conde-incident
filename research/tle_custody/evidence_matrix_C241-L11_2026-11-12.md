---
type: Guide
title: "C241-L11: dois boletins NASA e o caráter incremental da lista de decaimentos"
description: "Fac-símiles de 15 e 30 de novembro de 1963 com hashes, paginação, delta editorial e limites orbitais."
---

# C241-L11: não repetir um decaimento não significa uma nova observação

**Ocorrência C241-L11** da [issue #13](https://github.com/franklinbaldo/conde-incident/issues/13), ligada à [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), [C241-L4](evidence_matrix_C241-L4_2026-11-12.md) e [C241-L10](evidence_matrix_C241-L10_2026-11-12.md). **Duas edições de uma série documental NASA**, não dois sensores de rastreamento e não linhas TLE instrumentais.

## Fontes primárias documentais verificadas visualmente

- [NASA Satellite Situation Report, **15/11/1963**, vol. 3 nº 22, NTRS **19640001198**](https://ntrs.nasa.gov/citations/19640001198), PDF [original](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), **327.613 bytes**, SHA-256 `0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674`. **Página PDF 10/índice 9, página impressa 8:** sob *PLEASE ADD THE FOLLOWING TO THE DECAYED OBJECTS LIST*, `1963 3B` tem `8 NOV 63` na coluna **DECAY**.
- [NASA Satellite Situation Report, **30/11/1963**, vol. 3 nº 23, NTRS **19640002493**](https://ntrs.nasa.gov/citations/19640002493), PDF [original](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf), **1.266.393 bytes**, SHA-256 `9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d`. **Página PDF 10/índice 9, página impressa 8:** lista **novas adições** `1962 SIGMA 1`, `1963 9B`, `1963 45A`; **não inclui** `1963 3B` nessas *novas adições*. Não é uma tabela cumulativa de todos os decaimentos históricos.

**Método:** duas páginas de tabelas digitalizadas rotacionadas foram lidas **visualmente**, não por OCR. No [ledger JSON](nasa_ssr_1963_incremental_lineage_C241-L11.json), cada documento possui URL, data editorial, NTRS, volume, índice de página, transcrição delimitada, comprimento e SHA. O auditor local verifica os **bytes completos** e as invariantes de proveniência. Ele **não** reinterpreta automaticamente pixels do PDF; a extração visual não é comprovada pela máquina. SHA-256 fixa os exemplares recuperados nesta rodada, não autentica medições orbitais de 1963.

## O que os documentos permitem concluir

A NASA **registrou** o dia **08/11/1963** para `1963-003B` na edição de 15/11; na edição de 30/11 não o **readicionou** à relação incremental. Ausência da segunda listagem **não** é contradição, prova de nova observação, prova de permanência em órbita, hora de perda do rastreio ou hora de impacto. São publicações posteriores à data catalogada. A série pode depender do mesmo processo de catalogação NORAD; a independência instrumental permanece `NOT_ESTABLISHED`.

**Relação rastreável:** `C241-L11:NASA_SSR_1963_003B_incremental_edition_sequence` conecta IDs de documentos `19640001198 → 19640002493`, datas de publicação, ocorrência catalogada `1963 3B`, campo **DECAY** com **granularidade de dia** e semântica *adições* das listas. Estado `CONNECTED_PENDING_CALIBRATION`. `t_terminal` **não** é observado; `t=23:59` é indevido. Parquet secundário de 45 épocas 528, frame, incertezas, erros instrumentais e identidade da peça `S00528` **não são calibrados por esta fonte**. Nenhum domínio físico reduzido, prova física Lean ou simulação/holdout foi produzido. RAAN secundária `198,5261°` permanece distinta da RAAN legada `284,1520°` sem origem autenticada, que segue inativa. **Conde: INDETERMINATE**.

## Validação

```bash
python3 -m unittest discover -s tests -p test_tle_nasa_ssr_delta_audit.py -v
curl -fLsS https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf -o /tmp/19640001198.pdf
curl -fLsS https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf -o /tmp/19640002493.pdf
python3 tools/tle_nasa_ssr_delta_audit.py --ledger research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json --pdf15 /tmp/19640001198.pdf --pdf30 /tmp/19640002493.pdf --output /tmp/c241-l11.json
```

O workflow específico confere HEAD exato, hashes e publica somente o relatório derivado; **não arquiva os PDFs** nem consulta pessoas/arquivos. Resultado negativo: nenhum par TLE primário 527/528/529, checksum instrumental histórico, frame, sigma, identidade material ou instante terminal recuperado. A pesquisa futura precisa de catálogo primário de rastreamento ou documentação de engenharia distinta da série SSR.
