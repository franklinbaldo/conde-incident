---
type: Evidence
title: 'CGEO-57: distinguir datas de voo e de preparação nos índices NARA'
description: 'Leitura visual de quatro campos PREPARED BY do RG 373: índices preparados em outubro de 1956 com datas candidatas de voo em setembro de 1942.'
---

# CGEO-57 | Dois relógios, não uma única data

**14/11/2026.** Na inspeção ampliada dos JPEGs originais NARA RG 373, série 306062, microfilme M1765, rolo 317, identifiquei um campo cronológico que não estava estruturado em CGEO-56: **PREPARED BY**. As datas visíveis nele são **5 e 6 de outubro de 1956**, enquanto o campo impresso **DATE (D.M.Y.)** contém leituras provisórias de setembro de **1942**. O documento é uma ficha/overlay cartográfico produzido ou preparado posteriormente ao voo candidato. Não é o negativo fotográfico.

| O.P. FILE NO. | Folhas oficiais | DATE (D.M.Y.), transcrição provisória | PREPARED BY, data de preparação |
|---|---|---|---|
| 125370 | [00247](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00247.jpg) e [00432](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00432.jpg) | 27 SEP 42 | **5 OCT 56** |
| 125374 | [00248](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00248.jpg) e [00431](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00431.jpg) | 7, 14, 18 e 20 SEP 42 | **6 OCT 56** |

O campo **OVERLAY FILE NO.** é diferente entre quadrículas, coerente com arquivamento de duas representações espaciais. A mera repetição de O.P., ORGN/SORTIE e datas pode refletir **a mesma família de informação reindexada em 1956**; não multiplica a quantidade de observações independentes de 1942. Os nomes manuscritos de quem preparou as fichas não são transcritos como pessoas identificadas, pois sua leitura não foi certificada.

**Consequência técnica:** campos distintos precisam ser modelados como `flight_date_candidate` e `index_preparation_date`, nunca como uma única época de fotografia, época geodésica, data de digitalização ou data de observação de impacto. As datas de voo continuam provisórias: sem inspeção do negativo e sem horário de exposição. O contrato tipado desta entrega registra a custódia anterior por hash, mas não conta os mesmos quatro arquivos como nova evidência independente.

**Reprodução:** validar [manifesto](cgeo57_nara_overlay_preparation_dates.json) por `python3 tools/cgeo57_nara_temporal.py`, executar os testes adversariais sob Python normal e `-O`, e reobter os quatro JPEGs originais com `--live` para conferir bytes e SHA-256. O validador confronta os hashes e os cabeçalhos de CGEO-56 (dependência explícita).

**Próxima falsificação:** obter o instrumento do NARA que vincule número *spot*, exposição e lata a O.P. 125370/125374, verificando se há fotograma de Conde. [Guia da Cartographic Branch](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography). Sem foto individual autenticada, datum/controle terrestre histórico ou ponto de queda, `orbital_constraint_activated=false`.
