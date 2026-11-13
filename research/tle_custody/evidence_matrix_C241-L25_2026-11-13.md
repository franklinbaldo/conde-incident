---
type: Guide
title: "C241-L25: cobertura da série NASA SSR no índice NTRS"
description: "Auditoria reprodutível de edições de 1963 sem inferir inexistência por ausência de resultado."
---

# C241-L25: lacuna verificável da edição nº 21

**Pergunta:** a busca atual na API pública NASA NTRS pelo título Satellite Situation Report apresenta a edição volume 3, nº 21 entre os boletins já catalogados?

**Consulta:** POST https://ntrs.nasa.gov/api/citations/search com q = Satellite Situation Report, page.size = 200 e page.from = 0. O auditor exige que a página cubra o total informado antes de registrar ausência. O filtro utiliza o ano em publications[].publicationDate, não o prefixo do ID NTRS.

**Resultado em 13/11/2026:** 136 resultados na pesquisa; entre eles, 11 registros com data de publicação em 1963 e IDs já identificados pelo projeto. Os números de edição relacionados são **2, 8, 9, 13, 15, 16, 20, 22, 23, 24 e 25**, com a proveniência da correspondência indicada individualmente no snapshot JSON. Nenhum registro deste recorte declara explicitamente volume 3, nº 21: status **NOT_LOCATED_IN_THIS_QUERY**.

**Não é prova de inexistência.** Uma entrada indexada sob título diferente, ano incorreto ou sem numeração explícita pode escapar da consulta. A edição nº 21 permanece NOT_RECOVERED; não há demonstração de que nunca tenha existido, de que não haja cópia em outro arquivo nem de seu conteúdo orbital.

A fonte recuperada nesta fatia é **metadado atual da NASA**, não uma observação instrumental de 1963. O [snapshot de projeções do índice](ntrs_ssr_1963_index_C241-L25.json) preserva grafias e numerações literais, inclusive o título Saatellite no NTRS 19630012289 e X-583-63-1 no NTRS 19640000428. A correspondência deste último com o nº 20 depende da inspeção visual anterior C241-L12. O nº 25 depende da C241-L18. Não se presume que os metadados estejam corretos em todos os campos.

O [auditor](../../tools/tle_ntrs_ssr_index_audit.py) permite replay offline sobre a projeção versionada da resposta real e replay online para detectar alterações nos IDs e metadados das onze âncoras. Os [testes](../../tests/test_tle_ntrs_ssr_index_audit.py) mutam a projeção real, sem inventar observações orbitais. O workflow verifica o SHA exato, executa os testes e publica o resultado da nova consulta. Mudanças de indexação exigem revisão, nunca normalização silenciosa.

**Conectividade:** onze âncoras documentais do índice associadas a ledgers já auditados; um vazio catalográfico testável. **Domínio físico:** zero TLE primário, zero época instrumental, zero sensor/frame/σ/covariância e zero restrição nova de simulação ou Lean. NASA/Goddard, NORAD e SAO não se convertem em sensores independentes por republicação. Conde indeterminado.

**Próximo teste:** localizar o fac-símile da edição nº 21 por uma fonte de arquivo identificável, conferir capa, volume, número, páginas da tabela 3A/B/C e SHA dos bytes. Não inferir data de observação nem posição a partir de uma possível data editorial.

