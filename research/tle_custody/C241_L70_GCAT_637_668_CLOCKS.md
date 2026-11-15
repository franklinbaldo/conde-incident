---
type: Guide
title: "C241-L70: duas escalas cronológicas para os controles NORAD 637 e 668"
description: "Auditoria de datas operacionais do GCAT versus dias de decaimento catalográfico, no mesmo snapshot completo de C241-P29."
---

# C241-L70 · Operação ≠ decaimento (637 e 668)

**Achado reproduzível, sem nova medição instrumental:** o snapshot GCAT 1.8.9 / atualização de **13/11/2026**, já custodiado em [C241-P29](evidence_matrix_C241-P29_gcat_time_axes.md), contém as seguintes linhas para dois controles da discussão [Cervo #647](https://github.com/franklinbaldo/conde-incident/issues/647) e [Tartaruga #8](https://github.com/franklinbaldo/tartaruga/issues/8):

| NORAD / COSPAR | `psatcat`: `TLast / TOp / TDate` | `currentcat`: `DDate` | Estado `currentcat` |
| --- | --- | --- | --- |
| **637 / 1963-035A** | **01/09/1963** | **07/11/1963** | Reentrada ligado a Agena D 1169 (`A00384`) |
| **668 / 1963-037A** | **04/10/1963** | **12/10/1963** | Reentrada ligado a Agena D 1163 (`A00391`) |

Conforme as [definições do autor do GCAT](https://planet4589.org/space/gcat/web/cat/pcols.html), `TLast` é a última atividade conhecida, `TOp` o fim das operações regulares e `TDate` o término das transmissões/contatos. **Nenhuma dessas colunas é a data física da reentrada.** O `DDate` do catálogo de objetos é um **dia catalogado**, não uma observação terminal em 00:00 ou 23:59 UTC. O campo `SDate` de `currentcat` também não é época de rastreamento individual.

O controle **668** possui correspondência em [NASA SSR de 15/10/1963, NTRS 19640000428, p. impressa 7 / PDF 9](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf#page=9): `1963 37 A` e `12 OCT 63` (C241-L63). A linha contemporânea **não imprime 668**, e não constitui segunda medição independente quando a cadeia NASA/NORAD/GCAT pode ser comum. O controle **637** permanece dependente de catálogo para as datas citadas aqui. Nenhuma hora, sensor, localização de queda ou incerteza instrumental foi recuperada nesta fatia.

## Reprodutibilidade e antirregressão

O [ledger](gcat_control_clocks_C241-L70.json) preserva exatamente quatro linhas TSV (637 e 668 em dois arquivos) e seus hashes SHA-256. Os arquivos integrais não foram novamente contabilizados: os bytes e os hashes totais **são os mesmos** do snapshot de C241-P29, `psatcat.tsv` **5.233.316 bytes / 185bf7b9…** e `currentcat.tsv` **14.449.333 bytes / 391cdf7c…**. Em 14/11/2026 a reprodução no executor Ifro confirmou ambos os hashes e as quatro linhas. Não há quatro novos artefatos independentes.

```bash
python3 tools/audit_gcat_control_clocks_c241_l70.py --check --replay-source-dir /var/tmp/tartaruga-c241-l70
python3 -m unittest discover -s tests -p 'test_gcat_control_clocks_c241_l70.py' -v
python3 -O -m unittest discover -s tests -p 'test_gcat_control_clocks_c241_l70.py' -v
```

[Auditor](../../tools/audit_gcat_control_clocks_c241_l70.py) rejeita troca de colunas, identidade/parentesco alterados, inventar UTC/σ/sensor e mutações na linha mesmo com o hash recalculado. Executar o Prek integral no SHA final, incluindo controle negativo, em executor externo autorizado e conferir a CI da PR antes de integrar.

**Classificação:** `SECONDARY_MUTABLE_CATALOG_SNAPSHOT`; `new_instrumental_measurements=0`; `terminal_epoch_utc=null`; `extra_norad_528_constraints=0`; `THETA_UNCHANGED`. Uma diferença entre fim de missão e reentrada não é medida de erro da predição orbital. Não inferir janela de queda ou probabilidade em Conde.
