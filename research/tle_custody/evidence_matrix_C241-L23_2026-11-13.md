---
type: Guide
title: 'C241-L23: lacuna editorial de 10 para 30 de abril de 1963'
description: 'O fac-símile NASA nº 8 não lista 1963 3A/B/C; nº 9 lista, sem implicar data de detecção, ausência orbital nem novo sensor.'
---

# C241-L23: ausência numa edição não equivale a ausência no espaço

**Nova fonte primária documental:** [NASA Goddard, *Satellite Situation Report*, vol. 3 nº 8, 10/04/1963, NTRS 19630012127](https://ntrs.nasa.gov/citations/19630012127). [PDF oficial de sete páginas](https://ntrs.nasa.gov/api/citations/19630012127/downloads/19630012127.pdf), arquivo com **206.176 bytes**, SHA-256 `f71ddf0477213e3ee1f47f5094f1d9afe7a52044e94cf18840805bdb48ba5f42`, conferido em 13/11/2026. Capa PDF p. 1 confirma edição/data; apresentação PDF p. 2 registra compilação *as of 1430Z*. As cinco páginas seguintes, PDF p. 3–7 (impressas 1–5), contêm a tabela rotacionada *OBJECTS IN ORBIT*. Todas as cinco foram examinadas visualmente, não só pela camada OCR degradada.

**Constatação delimitada:** nenhum dos designadores **1963 3A, 1963 3B, 1963 3C** figura nas cinco páginas da lista em órbita da edição nº 8. Controles positivos na última página (PDF p. 7, impressa 5) incluem **1963 4A, 4B, 9A e 9B**, portanto a tabela tem lançamentos de 1963 e não se encerra simplesmente em 1962.

Na edição NASA [vol. 3 nº 9, 30/04/1963, NTRS 19630012128, PDF p. 7/impressa 5](https://ntrs.nasa.gov/api/citations/19630012128/downloads/19630012128.pdf#page=7), os **três designadores aparecem** com períodos publicados 94,6, 94,1 e 94,3 minutos, respectivamente, já auditados em **C241-L16**. São **20 dias entre publicações**, não um intervalo delimitado de aquisição de sensores. O cruzamento com NORAD 527/528/529 depende separadamente de **C241-L10**, porque os IDs NORAD não constam dessas células de 1963.

## Significado e restrições

Há uma **mudança na presença editorial da família 1963-003** entre duas edições NASA. É proibido transformá-la em alegação de que os objetos não existiam, estavam fora de órbita, eram secretos, foram detectados pela primeira vez entre as datas, foram lançados no intervalo ou receberam parâmetros instrumentais novos. A omissão pode ter causas editoriais, de seleção ou de disponibilidade de registros, **não identificadas** por esses dois PDFs.

O [ledger de custódia](nasa_ssr_apr10_listing_C241-L23.json) fixa fonte, escopo negativo, controles positivos e interpretação. O [grafo cumulativo](../constraints/ssr_apr10_listing_C241-L23.json) conecta **três indicadores de listagem documental** a C241-L10 e C241-L16, sem criar estados físicos nem três observações de radar. O operador `publication_listing_indicator(document,designator)` atua sobre uma **edição e um rótulo**, não sobre posição, órbita ou instante de medição. É distinta da ausência catalogada de um objeto após decaimento.

**Desconhecidos:** origem da omissão, época instrumental de cada elemento, sensor, estação, referencial, σ/covariância, identificação material do 528, hora/posição de reentrada e boletim nº 21. Nenhuma restrição física ou Lean foi promovida. O intervalo apenas orienta nova busca de logs/edições, mantendo **Conde indeterminado**.

O [auditor](../../tools/tle_nasa_ssr_apr10_audit.py) e os [testes adversariais](../../tests/test_tle_nasa_ssr_apr10_audit.py) verificam integridade, proveniência, relações e recusam falsos efeitos físicos. O gate remoto repete o download da NASA e o SHA: mudança de PDF exige nova verificação visual e nova custódia, não atualização silenciosa. O teste de hash **não substitui** a leitura humana já documentada das células.
