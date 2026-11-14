---
type: Guide
title: 'C241-L61 · Mudança de ramo A.1–WWV em 1º/11/1963'
description: 'Complemento imutável ao C241-L44; página visual e testes para a escala temporal SAO, sem converter o NORAD 528 em UTC.'
---

# C241-L61 · Relógio SAO em novembro de 1963

**Fonte:** Smithsonian Astrophysical Observatory, *Catalog of Precisely Reduced Observations*, P-17 / SAO Special Report 275, publicado em **14/05/1968**, [NASA NTRS 19680020675](https://ntrs.nasa.gov/citations/19680020675). Fac-símile [PDF](https://ntrs.nasa.gov/api/citations/19680020675/downloads/19680020675.pdf), 10.988.993 bytes, 176 páginas, SHA-256 `6b77e832e4273f7781cb61bfea7d38685c99d63e2f6b370a76d0b28a225ddf86` (reobtido 14/11/2026). Mesmo PDF custodiado em **C241-L44**; não contar uma segunda observação ou editar silenciosamente o ledger anterior.

**Leitura visual direta:** página impressa **3**, página **7** do PDF: a escala de todos os registros é a A.1 preliminar suavizada, corrigida em relação ao sinal **WWV emitido**, com dois ramos:

```text
1963-01-01 0.0 <= MJD < 1963-11-01 0.0:
  A.1 - WWV emitted = 2.292725 s + 0.001118458 (MJD - 38030.0) s
1963-11-01 0.0 <= MJD < 1964-01-01 0.0:
  A.1 - WWV emitted = 2.392725 s + 0.001118458 (MJD - 38030.0) s
```

A diferença entre interceptos é de **0,100000 s** no marco de 1º/11/1963, **não** um erro de posição nem uma nova observação orbital. Em MJD **38341.0** (8/11/1963, somente como teste matemático de calendário) a expressão dá **2,740565438 s** para A.1−WWV. Isto **não** é um horário de observação do 528 e não resolve A.1↔UTC/UT1 sem a cadeia adicional do relógio WWV e suas convenções históricas. Não transportar o ramo de antes de novembro para observações datadas depois da transição.

A mesma página impressa 3 explicita coordenadas **topocêntricas FK4, equador/equinócio 1950.0**, e colunas de RMS para **os 11 objetos impressos**, nenhuma das quais é 1963-003B. Página impressa **5**, PDF **9**, tabela 1, registra 9008 = **Shiraz, Irã** e 9114 = **Cold Lake, Canadá**, com coordenadas **x/y/z em megâmetros** e elipsoide **SAO Standard Earth** (a=6.378155 Mm, f=1/298.25). A lista também aparece em outras fontes do projeto; aqui serve para confronto de referência, não para inventar geodésia ou observações do 528. A correspondência com SC-8/RU301 exige a genealogia já catalogada, sem deduplicações artificiais.

**Limite e aplicação:** C241-L44 continua certificando que P-17 é um **catálogo publicado seletivo**, sem 527/528/529. O suplemento C241-L61 só cria um operador temporal condicional e verificável para **eventuais fichas originais identificadas por estação, objeto, quadro e relógio**; `epoch_utc_528=null`, nenhuma covariância, **zero restrições físicas** ou conclusão sobre queda em Conde. Executar `python -m unittest discover -s tests -p 'test_tle_sao_p17_wwv_step_c241_l61.py'` e `-O`. Para replay original `python tools/tle_sao_p17_wwv_step_c241_l61.py --pdf <arquivo>` com `pypdf==6.1.3`.
