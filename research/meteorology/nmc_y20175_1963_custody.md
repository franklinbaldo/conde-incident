---
type: ArchiveAudit
title: "Lontra: custódia binária integral de Y20175 (NMC 1963)"
description: "Arquivo GDEX d353000, SHA-256 integral, formato RPTOUT e limites de decodificação"
---

# Custódia integral NMC Y20175 (1963)

**Escopo:** identidade binária e inventário, não meteorologia inferida nem reentrada. **Data:** 12/11/2026. **Responsável:** 🦦 Lontra. **Solicitação:** lontra#1 do Lagarto. **Item preexistente:** MET-NMC-20261112-09.

O catálogo oficial NSF NCAR GDEX d353000, DOI 10.5065/R592-TX59, descreve a série B3 ADP de 1962 a 1972, recomendada pelo próprio acervo apenas para uso acessório. A API de inventário em https://gdex.ucar.edu/api/datasets/d353000/filelist/2/?filter_wfile=Y20175 devolveu HTTP 200; corpo de 1085 bytes e SHA-256 e0d0403fe132578b4c244a8cb2ccce1d47ca166eff35bead134018d5cc47bf91. Grupo Synoptic-Sort-raob, arquivo Y20175, nota literal "non-aircraft ua, 1963 , excluding all throws,", arquivado em 1998-09-28. Essa data é metadata de arquivamento, não data de sondagem.

A URL oficial é https://osdf-director.osg-htc.org/ncar-gdex/d353000/Y20175. O download integral HTTP 200 apresentou 117264384 bytes, SHA-256 afec7c443e0c912f8a742738bb82384197baecc7c743cfb00a2a8bda207b5de4. Primeiros e últimos 64 bytes constam do manifesto JSON. Os 117 MB ficaram apenas no ambiente de execução, NÃO foram versionados no GitHub. A verificação pode ser repetida com a ferramenta tools/verify_nmc_y20175.py, usando argumento --file para o arquivo local ou --download para obtê-lo. O script compara todos os bytes por SHA-256 e verifica tamanho, prefixo e sufixo. Testes offline: python3 -m unittest discover -s tests -p 'test_nmc_y20175_custody.py' -v.

**Limite documental fundamental:** arquivo binário NCAR blocked CRAY RPTOUT, baseado no NMC Office Note 20; não é texto pesquisável. Nenhum decoder ON20/RPTOUT validado foi executado e nenhuma estação/dia foi lida. Assim, Salvador 83229, Aracaju 83096 e Recife 82900 para 7, 8 e 9/11/1963 permanecem NOT_DECODED, não NO_MATCH. Não há horário, nível, unidade, qualidade, erro instrumental nem restrição física nova.

**Documentação do formato:** apêndice A.3 de A Comprehensive Aerological Reference Data Set (CARDS), pp. impressas 43–45, https://scispace.com/pdf/comprehensive-aerological-reference-data-set-cards-5fey360i6i.pdf. As páginas do fac-símile foram vistas; descrevem decodificação difícil de B3 de **1971–1972** (blocos NCAR de 64 bits, campos NMC de 36 bits, erros de sincronização). A experiência de 1971–1972 NÃO valida uma taxa de erro nem a disposição exata de bits do arquivo Y20175 de 1963.

**Cadeia dependente:** GTS/NMC -> NCAR -> d353000 -> Y20175 -> SHA de download. Não é testemunha instrumental independente da eventual medição de uma estação. Integridade por hash de 2026 não comprova origem histórica. Próxima fatia é recuperar conversor RPTOUT/ON20 testado com referência, interpretar tipos/qualidade e depois varrer os três códigos e três datas. Nenhum parecer de ausência foi produzido.
