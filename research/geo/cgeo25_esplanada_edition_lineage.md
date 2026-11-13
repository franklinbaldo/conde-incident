---
type: Guide
title: "CGEO-25: Esplanada MI-1850 foi editada em 1973; localizar os levantamentos antecedentes"
description: "Catálogo primário SUDENE 1997 e cartas CPRM 1998 custodiados; edições posteriores a 1963 e folhas PETROBRAS 1956–1963 não autorizam coordenadas de impacto"
---

# CGEO-25 | Identificada a edição da folha Esplanada

A pendência CGEO-24 sobre a **época de edição** da folha Esplanada MI-1850 foi parcialmente resolvida com fonte primária. O [*Catálogo das cartas topográficas do Nordeste do Brasil*, 2ª edição, SUDENE (1997)](https://www.gov.br/sudene/pt-br/centrais-de-conteudo/catalogo-1-para-100000-pdf/@@display-file/file#page=125), **página impressa 133, página PDF índice 124**, registra **Esplanada**, SC.24-Z-C-VI, **SUDENE e Cruzeiro do Sul S.A., Rio de Janeiro, 1973**, escala 1:100.000 e quadrícula 11°30′–12°S, 37°30′–38°W. O PDF do catálogo foi obtido integralmente e autenticado por SHA256. **Não obtivemos a folha original de 1973**, apenas a descrição de acervo. A edição é **posterior ao episódio de 8/11/1963**; não deve ser promovida a observação daquele dia.

As duas cartas da [CPRM/Serviço Geológico do Brasil (1998), mapa planimétrico](https://rigeo.sgb.gov.br/server/api/core/bitstreams/69f40826-c61e-4f46-b5a5-b50d2a279627/content) e [mapa topográfico](https://rigeo.sgb.gov.br/server/api/core/bitstreams/c7a40a7e-22d8-48f2-9276-a889e6d1a676/content), do projeto **Acajutiba–Aporá–Rio Real**, citam Esplanada e Buquim SUDENE **1973**, Inhambupe IBGE **1967** e reduções de seis folhas **PETROBRAS/SACS/GEOFOTO na escala 1:25.000, elaboradas no intervalo 1956–1963**: `721-4-2`, `721-4-3`, `721-4-4`, `725-1-1`, `725-1-2`, `725-1-4`. O mapa topográfico também menciona PROSPEC/DNOCS 1:40.000 de 1961. São candidatos **arquivísticos** para investigar bases mais antigas, não folhas individualmente datadas ou verificadas sobre o **Centro de Conde**.

Os três PDFs primários foram adquiridos em 13/11/2026, validados como PDF por assinatura e comparados por bytes e SHA256. URLs, tamanhos e hashes integrais estão em [CGEO-25 JSON](cgeo25_esplanada_edition_lineage.json). As duas cartas de 1998 são produtos derivados, com atualizações posteriores, e não podem transformar seus predecessores em observação independente de 1963. A referência ao período *1956–1963* não prova que cada folha existia **até 8 de novembro de 1963** nem que algum dos seis recortes abrange a sede de Conde. **Não atribuir datum Córrego Alegre da composição de 1998 à folha original de 1973 ou aos predecessores sem ler os originais.**

## Reproduzir custódia e preservar limites

Baixar cada URL exata do JSON para os três nomes em `sources.*.local_filename`, exigir status HTTP 200, PDF real, tamanho e SHA256. Executar `python3 -m tools.cgeo25_esplanada_lineage --sources-dir /tmp/arquivos`. Sem `--sources-dir`, o comando e os testes conferem exclusivamente o **contrato offline**, sem alegar reacesso externo.

A relação investigativa fica: **catálogo 1997 → ficha Esplanada 1973 → cartografia precedente indicada pela CPRM 1998 → folhas 1956–1963 a obter → possível georreferenciamento urbano de 1963**, condicionado à identificação da cobertura, época da tomada, datum e controle independente. Nada dessa cadeia define centro, queda ou polígono de 1963; `can_constrain_orbital_reentry=false`.
