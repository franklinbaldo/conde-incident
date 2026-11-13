---
type: Guide
title: "IGRA: cobertura de Natal e Salvador em 1963 e estabilidade dos recortes de Recife"
description: "Auditoria de arquivos integrais NOAA/NCEI e hashes de sondagens de novembro de 1963, sem inferir ausência histórica nem criar restrições físicas."
---

# Controle regional IGRA e deriva de versão do ZIP de Recife

**Questão falsificável:** os arquivos de estação NOAA/IGRA atuais de Natal (82599) e Salvador (83229) permitem comparar, em novembro de 1963, o vento vertical de Recife (82900) com sondagens contemporâneas de outros locais? **Não nesses dois arquivos.** Isso não significa que não ocorreram observações nas cidades naquela época, nem exclui outros arquivos ou receptores.

Em **13/11/2026**, foram baixados integralmente os três ZIPs de [NOAA/NCEI IGRA `data-por`](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/) e a [lista institucional de estações](https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt) (SHA-256 da lista: `9515d29b0c61fcfc912028830c37f47e723ba32c14d88fb48cf6d8bf727060ab`). O [manifesto JSON](igra_nearby_1963_source_refresh.json) preserva SHA-256 integral e tamanho de cada ZIP, ano de observações e limites temporais. A auditoria enumerou **todos os cabeçalhos reais** `#` de cada arquivo; não pesquisou apenas o primeiro/último ano nem preencheu lacunas com zero físico.

| Arquivo | Cabeçalhos totais | Em 1963 | Primeiro registro do intervalo posterior à lacuna | SHA-256 do ZIP observado |
|---|---:|---:|---|---|
| Natal / BRM00082599 | 20.448 | **0** | 18/01/1967; período anterior termina em 28/02/1946 | `e8ffc9be391d97674b95624eda8d57cd94ddac599404cdea775aa6e95202f7be` |
| Recife / BRM00082900 | 14.977 | **346** | 01/01/1964 | `df4fcd10e1920723b3cf337b745301b505810ee1dc8a6c5006b84e52b2c871df` |
| Salvador / BRM00083229 | 7.954 | **0** | 02/01/1970, primeiro registro desse arquivo | `d6bd80590ec72906726def8959df95b99f6abf9be0752b505c7c7d0c33c5e240` |

**Achado de proveniência adicional:** o ZIP integral atual de Recife tem SHA-256 `df4f...`, diferente do ZIP previamente pinado nos trabalhos C149–C151 (`0655b3ea...`). No entanto, os **excertos brutos completos dos três lançamentos de 7, 8 e 9/11/1963 são idênticos byte a byte** aos recortes base64 versionados, com os hashes já verificados `d77a3...`, `577224...` e `73e963...` (completos no manifesto e no verificador). A causa da diferença no ZIP integral **não foi estabelecida**. Não se deve reescrever o hash do acervo antigo como se o ZIP atual fosse o mesmo objeto. Os resultados científicos dependentes desses três excertos permanecem reproduzíveis **para os bytes comparados**, não necessariamente para todos os demais bytes do arquivo.

**Genealogia e limites:** duas fontes de estação não têm cobertura naquele ano, enquanto a mesma família `ncdc6301` de Recife continua com três perfis de datas nominais 12 UTC, horários reais de soltura desconhecidos. Não se criou prova de que Natal e Salvador não lançaram balões em 1963; não se obteve medição independente contemporânea de vento próxima a Conde; não se determinou covariância, erro de transporte, densidade, arrasto, trajetória nem faixa geográfica. Conectar com C149–C151 como **`CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION`**, sem promover ausência de dado a observação ou tornar `null` igual a zero.

**Reprodução:** após baixar os três ZIPs com seus nomes originais, executar `python3 tools/audit_igra_neighbors_1963.py --source-dir /caminho/para/zips --check` para revalidar todos os bytes e cabeçalhos. Sem os binários, `python3 tools/audit_igra_neighbors_1963.py --check` e `python3 -m unittest discover -s tests -p test_igra_neighbors_1963.py -v` verificam os hashes dos recortes C149–C151 e as invariantes do manifesto; **não** substituem a leitura independente dos ZIPs integrais. Uma versão posterior da NOAA pode modificar os arquivos novamente, hipótese a registrar como nova captura em vez de ignorar erro de hash.
