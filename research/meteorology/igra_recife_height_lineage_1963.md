---
type: Guide
title: "C149–C151: procedência da altura geopotencial em Recife"
description: "NOAA/NCEI documenta dependência p/T/GPH e limites da precisão de relato; camada hipsométrica não calibra instrumento."
---

# Altura geopotencial de Recife: teste de coerência, não segunda testemunha

## Fonte e achado verificável

O [NOAA/NCEI IGRA v2.2 Product Description Supplement](https://www.ncei.noaa.gov/pub/data/igra/igra2-product-description-supplement.pdf), publicado em **janeiro de 2023**, foi examinado nas **páginas impressas 12 e 20**. É documento institucional sobre o processamento histórico, **não** manual do instrumento recifense em 1963. Na seção 3.1.3 (p. 20), o NCEI explica que **tradicionalmente a pressão era medida e a altura geopotencial era inferida a partir da pressão, temperatura e umidade na origem**. O IGRA distribui esses valores como recebidos e não produz novos valores estimados. Esta prática geral **não autentica** o algoritmo ou aparelho específico em Recife em 1963.

Na tabela 3.1 da mesma página, alturas geopotenciais em níveis de pressão apresentam **precisões usuais de relato de 1 ou 10 m**. O texto afirma que a precisão de representação **pode diferir da precisão de medição** e varia entre fontes e épocas. Portanto, 1 m e 10 m **não são incertezas instrumentais, limites de erro nem calibração da sondagem C149–C151**.

A seção 2.1.3 (p. 12) explicita que, para estações fixas, o catálogo e cabeçalhos de sondagens IGRA podem repetir a **posição conhecida mais recente** e não a posição histórica do instrumento. Assim, latitude catalogada −8,05°, longitude −34,9167° e elevação 7 m não constituem geolocalização instrumentada confirmada em 1963.

## Dependência cumulativa

As sondagens [NOAA BRM00082900 de 7, 8 e 9 de novembro de 1963](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), às **12h UTC nominais** e com hora real de soltura desconhecida (`RELTIME=9999`), pertencem à fonte `ncdc6301`. O ZIP integral previamente preservado tem SHA-256 `0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc`. As **29 + 26 + 26 observações de nível** formam as mesmas **28 + 25 + 25 = 78 camadas** da [auditoria hipsométrica anterior](igra_recife_19631107_09_hypsometric_consistency.md); não são observações novas nem fontes instrumentais independentes.

A comparação `ΔH(p,GPH)` versus espessura hidrostática assumida com `T` pertence, portanto, a um **único conjunto de variáveis possivelmente interdependentes**. Os resíduos previamente calculados continuam verificáveis, mas **não constituem validação instrumental independente de GPH**, tampouco estimam `σ`. Uma conclusão ainda mais forte, de que *esta* estação realmente aplicou *aquela mesma fórmula*, seria indevida: a documentação técnica recuperada é geral, e a rotina/identificação histórica recifense específica segue desconhecida.

A [ficha estruturada desta auditoria](igra_recife_height_lineage_1963.json) liga a relação **C149–C151 → p/T/GPH → residuais condicionais → hipótese de densidade/arrasto pendente**. C144–C146 documenta cartas de superfície, C17–C23 a atividade solar e geomagnética e C193 medições termoesféricas em outra época/altura; nenhum deles identifica a covariância instrumental recifense ou fornece vento medido em Conde. Não se ativou restrição sobre o domínio físico de queda, altitude terminal, posição ou momento de reentrada.

## Reprodução, resultados negativos e próximo teste

Executar `python3 -m unittest discover -s tests -p test_igra_recife_height_lineage.py -v` para confirmar os três arquivos históricos e os controles negativos contra fonte independente fictícia, alteração de data, transformação de resolução de relato em `σ` e transferência espacial inventada. **Sem nova medição, sem altitude geométrica direta, sem estimação de erro de Conde.**

Próximo teste: confrontar a estação BRM00082900 com o histórico `igra2-metadata.txt`, código de instrumento histórico e documentação do processamento original de GPH em 1963, **somente em acervos públicos existentes, sem contato com pessoas ou arquivos**.
