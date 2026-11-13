---
type: Guide
title: "Conde 1963: alinhamento nominal dos dias chuvosos GHCNd"
description: "Teste de defasagens de rótulos diários em 11 postos com SHA integral, QC e apoio temporal constante; não estima hora nem trajetória."
---

# O dia do pluviômetro é o dia do acontecimento?

A evidência [MET-GHCND-CONDE-19631107-09-01](ghcnd_conde_precip_19631107_09.md) preserva **3,5 mm rotulados 08/11/1963** no posto CONDE (BR048346820). A pergunta nova é se postos próximos tendem a marcar chuva no mesmo **dia nominal**, ou com diferença de um dia. Não é possível autenticar um horário de leitura a partir de arquivos .dly já compilados.

## Experimento reproduzível

Usamos as **11 séries .dly integrais** e os SHA-256 fixados no manifesto anterior, sem imputação de zeros em datas ausentes. Para cada par CONDE × outro posto, convertemos PRCP de décimos de milímetro para **choveu (>0) ou não choveu (=0)**. Descartamos valores ausentes, datas inválidas e valores com QFLAG preenchida; todos os valores incorporados mantêm SFLAG=I.

Calculamos a associação binária **phi** para os rótulos do posto vizinho em t + lag, com lag de **−2, −1, 0, +1, +2 dias** em relação ao rótulo t de CONDE. As cinco avaliações de cada par usam **exatamente as mesmas datas de CONDE**, exigindo presença do vizinho nos cinco deslocamentos. Assim, a maximização descritiva não muda artificialmente o conjunto de datas dentro de um par. Um máximo de phi entre cinco alternativas **não é estimativa da hora de leitura**, não é significância estatística e não informa causalidade; chuva pode ser espacialmente heterogênea, sazonal, seriada, assimétrica e registrada com práticas distintas.

## Resultados de 1963

- CONDE possui **365 datas válidas**, das quais **136 são positivas**.
- Entre os **dez outros postos**, a defasagem de maior phi é **0 dia em cinco**, **−1 dia em quatro** e **+1 dia em um**. Não há deslocamento uniforme que justifique harmonizar os rótulos diários automaticamente.
- Os suportes comparativos fixos variam conforme a cobertura: **88 datas para Cambuís**, **118 para Palame** e **até 361 para postos mais completos**. Não confundir lacuna com dia seco.
- Foi identificado e excluído o valor de **100,1 mm** de Timbó em 06/08/1963, com **QFLAG=S** (*failed spatial consistency check* no manual da NOAA). A presença do valor no arquivo não valida sua qualidade.
- Como controles observacionais, em **08/11** somente **2 de 11** postos têm precipitação positiva (Conde 3,5 mm; Indiaroba 2,4 mm), enquanto **13/11 e 14/11** registram **8 de 11** postos positivos em cada data. Esses contrastes mostram que a rede arquivada distingue eventos espacialmente mais disseminados, sem provar que os postos são instrumentalmente independentes nem fixar sua hora de leitura.

O JSON adjacente contém para cada par as cinco tabelas de contingência, phi, cobertura fixa, máximos descritivos nos semestres e a exceção de qualidade. Os hashes são herdados **explicitamente** do manifesto pinado anterior, e conferidos de novo sobre cada arquivo inteiro. Nenhuma fonte nova foi simulada ou preenchida.

**Cadeia epistemológica:** a NOAA define I como coleção internacional, formada historicamente por dados obtidos por contatos; isso **não identifica** instituição, horário, equipamento ou convenção de virada do dia do observador brasileiro. O GHCNd é arquivo de resumos diários integrado, com testes gerais de qualidade, não fac-símile de caderneta de 1963. Ver [manual de flags](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt), [página NCEI sobre coleção internacional](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily) e o manifesto pinado anterior.

**Conclusão formalmente limitada:** não inferimos mudança de relógio da estação, chuva na hora da ocorrência, vento, dispersão, arrasto, trilha ou local de queda. Preservar CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION e as dependências do grafo C149–C151. O próximo teste com potencial de retirar essas incertezas exige ficha brasileira original, hora de leitura e identificação de estação em 1963, além de comparação com fontes primárias distintas.

Reproduzir: python3 tools/audit_ghcnd_conde_wetday_alignment_1963.py --source-dir /tmp/ghcnd-1963 --check. O CI baixa novamente as fontes .dly sem estimar ausência pelo ano extremo do catálogo, valida hashes completos e executa testes adversariais.
