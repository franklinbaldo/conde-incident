---
type: Guide
title: 'C241-ABELHA-R50: inferência da milha STL sem ativação orbital'
description: 'R53 ligado a reprodução NASA R51, hipóteses Lean e parâmetros latentes, mantendo proveniência e dependência.'
---

# C241-ABELHA-R50 · Unidade documental e domínio orbital

**C241-LONTRA-R51:** NASA TM X-59315, página impressa B-12 (PDF 105/117), fac-símile oficial https://ntrs.nasa.gov/api/citations/19670008638/downloads/19670008638.pdf; SHA-256 custodiado f77b0e8998d467dd457d0ab8e8012e6e9d69c60fb6180aa3d68f1e8422b32786. A legenda impressa diz *miles* e reproduz *STL Space Log*, vol. 3, n. 4. O fascículo STL original não foi recuperado.

**C241-LONTRA-R53:** SHA-256 do manifesto 65c2db57f9ee7c573d07b360623b79656895c9a1513e8dfc3857daf18b643454. Cinco linhas da MESMA página (duas 1963 3A, Cosmos 13, duas Syncom 1). Sob modelo de Kepler de dois corpos e constantes fixas, milha terrestre apresenta resíduos menores que milha náutica ou quilômetro. **É uma inferência numérica sobre subtipo de unidade, não uma certificação da legenda STL original nem outro instrumento.** O relatório R51 e a auditoria R53 não são duas observações independentes.

**Rastreabilidade:** o exportador tools/export_stl_mile_subtype_bridge.py valida SHA-256 do manifesto R53, SHA-256 do JSON científico R51, regeneração da ponte R51 e auditoria quantitativa R53. Saída determinística em public/data/conde-stl-mile-subtype-bridge.json. O DAG preserva IDs, página, obra original não recuperada, origem editorial e quinze dependências para hipóteses/Lean/parâmetros. O estado Lean é candidato não compilado: faltam original STL, definição das duas colunas, época UTC, estação, referencial e covariância. Contagem física desconhecida é null, não zero afirmado.

**Efeito físico:** nenhum dado R53 identifica NORAD 528 em novembro de 1963. A linha impressa 1963 3A é de janeiro e não deve ser promovida para 1963-003B. As variáveis PARAM:historical_printed_altitude_scale, PARAM:orbit_prior_527 e PARAM:orbit_prior_528 permanecem null/inativas, Θ inalterado. A genealogia NASA→STL é atribuição editorial; a relação da tabela soviética R49 com STL continua candidata, não provada.

**Contraprovas:** testes normais e sob Python -O rejeitam hash adulterado, objeto trocado, original falsamente recuperado, fonte duplicada como sensor, subtipo supostamente certificado e ativação. A matriz C01–C238 é preservada. Próximo teste falsificável: recuperar as páginas e legendas do STL v.3 n.4 e localizar fontes instrumentais do 528 com UTC, estação, frame e erro.
