# OKF — Investigação geral — 2026-11-12, cartas meteorológicas primárias

## Fato verificado
- Recuperada coleção **Marinha do Brasil DHN/CHM** “Cartas de Pressão ao Nível do Mar — ano 1963”, ID GeoNetwork `9ea5e9a4-199d-4d14-8b55-682eb4daa211`; arquivo **Nov_1963.pdf**, 30 páginas com cartas sinóticas 12 HMG. Inspeção **visual** das páginas 8/30 (sexta 08/11) e 9/30 (sábado 09/11), com cabeçalhos originais; tratam da pressão à superfície, não de lançamento de balão nem de evento de Conde.
- Fonte: https://idem.marinha.mil.br/geonetwork/geonetwork/api/records/9ea5e9a4-199d-4d14-8b55-682eb4daa211 ; PDF: https://idem.marinha.mil.br/geonetwork/srv/api/records/9ea5e9a4-199d-4d14-8b55-682eb4daa211/attachments/Nov_1963.pdf .
- Decreto nº 52.667 de 11/10/1963 demonstra Distrito de Meteorologia do Leste sediado em Salvador, seção de aerologia e Arquivo Técnico: https://www2.camara.leg.br/legin/fed/decret/1960-1969/decreto-52667-11-outubro-1963-392920-publicacaooriginal-1-pe.html . É norma, não livro de lançamento.
- Localizador GDEX d394001 DOI 10.5065/BYQV-RZ12 identifica acervo FAB de rawinsondes/pibals (1950–1986 com cobertura individual variável), **não** foram obtidas medições nem confirmado perfil de Salvador em 08/11: https://gdex.ucar.edu/datasets/d394001/ .

## Incertos / hipóteses
- H-BAL: lançamento de balão na Bahia durante janela 7–9/11; não verificado. Dados de superfície não fornecem ventos em altitude nem posição de um objeto. H-RUM e H-REENT permanecem abertas. Os novos documentos **não adicionam testemunha** do rumor.
- Não há carta 00 HMG no PDF consultado apesar de o catálogo mencionar cartas duas vezes por dia; arquivo de novembro apresenta 30 folhas 12 HMG.
- Não se testou hash contra outra versão oficial, não se recuperou jornal baiano, TLE ou registro de balão.

## Entrega e próximo passo
- Atualizar a matriz incremental da PR #42 com IDs locais MET-DA-20261112-01 a 04, sem colisão com C001–C238 na PR #1.
- Verificar disponibilidade real por estação/data no GDEX d394001 para 8/11/1963; buscar cadernos de radiossondagem e originais da rede meteorológica do Distrito do Leste. Se obtidos, especificar erros e confrontar com simulação de deriva, reservando holdouts. Não transformar carta em vetor de vento de altitude.
- Nenhuma alteração do blog, contato externo, Lean/simulador ou parâmetros NORAD 528; sem merge.
