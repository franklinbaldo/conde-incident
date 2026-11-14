---
type: Evidence
title: 'CGEO-50: números de cabeçalhos NARA não localizam negativos no catálogo genérico'
description: 'Três consultas HTTP 200 custodiadas, 125374/125370/133002, sem cruzamento demonstrado ao spot number/can locator; instruções oficiais de acesso.'
---

# CGEO-50 | Catálogo genérico não é o localizador de negativos NARA

**14/11/2026.** Retomei os três números manuscritos nos cabeçalhos de quatro *overlays* da unidade [NARA 46716637](https://catalog.archives.gov/id/46716637), RG 373, série 306062, M1765 rolo 317, anteriormente autenticados em **CGEO-47/49**. O número **125374** está sobre o campo impresso `O.P. FILE NO.` da [folha 00248](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00248.jpg). Não é seguro chamá-lo de *spot number* ou número de lata. As etiquetas próximas de **26** e **16** são candidatas para procurar exposições, não fotos da sede confirmadas.

Executei três buscas públicas reproduzíveis via API institucional `catalog.archives.gov/proxy/records/search?limit=10&page=1&q=...` (HTTP 200):

| Busca textual | Resultados totais reportados | Primeiro resultado, não relacionado | Bytes da resposta |
| --- | ---: | --- | ---: |
| `125374` | 183 | Ambassador Arthur Goldberg speech at the United Nations | 40.034 |
| `125370` | 258 | Modernization #40: It Happened in Hadae-ri | 67.956 |
| `133002` | 3.451 | Press Conference USA: Grace Halso | 44.460 |

Cada resposta foi adquirida integralmente e tem SHA256 no [contrato CGEO-50](cgeo50_nara_locator_search.json). Os totais são fotografias do índice em **14/11/2026**, não valores permanentes, e abrangem registros de todo o catálogo: **não houve descoberta autenticada de negativo nessas três primeiras páginas**, mas **não se demonstrou ausência de negativos no acervo nem ausência de outros resultados**.

A [orientação da Cartographic Branch do NARA](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography), revisada em fevereiro de 2025, exige *spot number* e número de exposição para localizar a lata no RG 373. Seu [guia metodológico de 11/09/2019](https://unwritten-record.blogs.archives.gov/2019/09/11/researching-foreign-aerial-photography/) explica que *spot numbers* podem ser só numéricos, mas **sem um identificador efetivo a indexação pode não permitir rastrear a lata**. O *can locator* não está disponível no catálogo público; sua versão digital pode ser solicitada a `carto@nara.gov`. Sem resposta do arquivo, o cruzamento entre `O.P. FILE NO.` e *spot number* continua desconhecido. **Nenhum contato com o NARA foi enviado.**

**Próxima ação verificável de custódia:** pedir ao responsável pelo acesso arquivístico (🦦 Lontra) uma verificação documental junto ao NARA sobre a interpretação de `125374`, da folha `m1765-317-00248.jpg`, e a existência de *spot number*, lata ON/DN e exposições 26/16. Usar as outras folhas 00247, 00249 e 00250 como controles, nunca presumir que `133002` seja único. Caso não haja *spot number*, registrar a impossibilidade de cruzamento nessa rota, sem converter em inexistência de fotografia histórica.

**Limites:** as consultas são resultados de texto, **não fotografias**. Nenhum negativo original, data da exposição da cidade, perímetro do Centro em novembro de 1963 ou local da alegada queda foram autenticados; nenhuma restrição orbital foi ativada.
