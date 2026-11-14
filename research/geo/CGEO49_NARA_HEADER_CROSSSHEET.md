---
type: Evidence
title: 'CGEO-49: quatro cabeçalhos NARA e números manuscritos ainda sem spot number'
description: 'Comparação visual do campo O.P. FILE NO. em quatro overlays de 1942–1943; fontes reais, sem identificar negativo ou centro de Conde.'
---

# CGEO-49 | Cabeçalhos NARA 1942–1943: identificação sob reserva

**14/11/2026.** Comparei visualmente quatro originais da [unidade NARA 46716637](https://catalog.archives.gov/id/46716637), RG 373, M1765 rolo 317, com bytes/tamanho/SHA já custodiados por **CGEO-47**. São índices de voo, não quatro fotografias aéreas nem observações independentes do núcleo urbano.

| Folha original | Número manuscrito sobre a linha O.P. FILE NO. | Data aparente |
| --- | --- | --- |
| [00247](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00247.jpg) | **125370** | **27 SEP 42** |
| [00248](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00248.jpg) | **125374** | **7, 11, 18, 20 SEP 42** |
| [00249](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00249.jpg) | **133002** | **21 AUG 43** |
| [00250](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00250.jpg) | **133002** | **21 AUG 43** |

**Novo achado transversal:** o mesmo manuscrito **133002** figura em *duas folhas diferentes*. Isso demonstra que tal anotação não identifica univocamente uma folha ou exposição. Os números 125370, 125374 e 133002 aparecem na região do campo impresso **O.P. FILE NO.**, mas **não estão autenticados como spot number, exposição, filme ou lata**. Todas as datas são **leituras humanas provisórias do cabeçalho**, não datas individualizadas de fotografia da cidade. A folha 00248 continua candidata à faixa 26–16 da CGEO-48.

O [guia oficial da NARA](https://unwritten-record.blogs.archives.gov/2019/09/11/researching-foreign-aerial-photography/) explica que um *spot number* pode ser alfanumérico ou apenas numérico, e que o localizador de latas **não está disponível online**. Não é seguro afirmar nem excluir identificação de spot pela simples forma numérica. Só a confrontação com o arquivo e o localizador permite a passagem para negativo original. Nenhum contato institucional foi enviado nesta rodada.

O contrato cgeo49_nara_header_crosssheet.json fixa os hashes e a classe de incerteza. O comando python3 tools/cgeo49_nara_headers.py valida a derivação; --cached-directory verifica novamente bytes originais locais e --live exige HTTP 200 e SHA integral dos quatro JPEGs. Testes adversariais rejeitam substituição, spot/can inventado, data promovida a exposição, perímetro 1963 e restrição orbital.

**Próximo passo:** confrontar os números **125374** (folha 00248, exposições 26–16), **125370** (00247), **133002** (00249–50) com o localizador NARA ou assistência arquivística. Não equiparar esses voos ao SGB ROLL 58 de 1964–1970. Não se conhece a geometria do Centro de Conde em novembro de 1963, nem negativo que comprovadamente cubra sua sede, nem o lugar da alegada queda. Nenhuma restrição orbital foi ativada.
