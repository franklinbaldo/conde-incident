---
type: Guide
title: "GHCN-Daily: chuva arquivada em Conde, 7–9 novembro 1963"
description: "Recupera 33 dados diários de 11 postos próximos, com hashes integrais, flags de origem e limites temporais explícitos."
---

# Um registro de chuva de 8 de novembro em uma estação chamada Conde

Em **13/11/2026**, recuperei os arquivos brutos `*.dly` de onze postos da [NOAA GHCN-Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily), além do catálogo de estações, inventário e [manual original de formato e flags](https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt). É uma **família arquivística diferente da NOAA/ISD**, objeto da auditoria anterior #506. Nenhuma dessas observações foi inventada ou preenchida; o manifesto JSON conserva SHA-256 de cada arquivo integral, oito caracteres originais por data e as três flags.

| Posto do catálogo GHCNd | Distância ao ponto médio da bbox municipal IBGE 2022 | 07/11 | 08/11 | 09/11 |
| --- | ---: | ---: | ---: | ---: |
| **CONDE**, BR048346820 | 10,5 km | 0,0 | **3,5** | 0,0 |
| Altamira (IAA) | 17,7 km | 0,0 | 0,0 | 0,0 |
| Palame | 23,1 km | 0,0 | 0,0 | 0,0 |
| Esplanada | 29,9 km | 0,0 | 0,0 | 0,0 |
| Timbó (VFFLB) | 33,1 km | 0,0 | 0,0 | 0,0 |
| Itapicuru | 40,8 km | 0,0 | 0,0 | 0,0 |
| Entre Rios (FABA) | 41,9 km | 0,0 | 0,0 | 0,0 |
| Indiaroba | 42,5 km | 0,0 | **2,4** | 0,0 |
| Cambuís | 42,5 km | 0,0 | 0,0 | 0,0 |
| Cristinápolis | 43,6 km | 0,0 | 0,0 | 0,0 |
| Aracaju | 126,3 km | 0,0 | 0,0 | 0,0 |

**Unidade: milímetros de precipitação diária**, correspondendo a `PRCP` original em décimos de milímetro (35→3,5 mm; 24→2,4 mm). Todos os 33 valores estão presentes, sem `QFLAG` e com `SFLAG=I`, definido no manual GHCNd como *International collection* de dados não norte-americanos obtidos por contatos. Esse código **não demonstra** a identidade do observador, do pluviômetro, da instituição brasileira, a independência entre os onze postos, nem a origem de cada cópia histórica. `QFLAG` vazia **não mede** erro instrumental.

**O que muda:** há um **registro arquivístico diário associado a uma estação denominada CONDE em 08/11/1963**, não apenas um posto regional distante. Isso corrige a lacuna da busca anterior restrita à família ISD. Os 0,0 mm dos postos vizinhos não negam o registro: precipitação local varia espacialmente, e sem controle de horário, revisão do documento original e erro de captura não há motivo para harmonizar artificialmente as séries. Também não foi comprovada a coordenada de 1963, que pode diferir da ficha retrospectiva.

**O que não muda:** a data diária pode refletir convenções locais de leitura e acúmulo desconhecidas; **não sabemos se choveu durante a hora da suposta ocorrência**, nem no ponto alegado. Chuva diária não mede vento, pressão, perfil vertical, resistência aerodinâmica ou queda orbital. Não usar os 3,5 mm como condição de contorno do Castor. A origem `I` é diferente da `N/BRAZ` do ISD Caravelas, mas isso **não prova independência instrumental**. Vincular esse observável documental ao grafo C149–C151/Caravelas apenas como `CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION`.

**Próximo teste falsificável:** localizar a ficha pluviométrica brasileira original da estação CONDE (provável série de posto, origem institucional não autenticada), coordenada de funcionamento em 1963, horário de leitura, convenção do dia pluviométrico e as observações originais vizinhas. Só então distinguir chuva real contemporânea, transcrição e localização.

Reprodução pinada: `python3 tools/audit_ghcnd_conde_rain_1963.py --source-dir /tmp/ghcnd-1963 --check`. O workflow correspondente recupera as 14 fontes integrais, confronta os SHA-256, recompõe as 33 observações e executa testes adversariais. Nenhum `.dly` completo foi inserido no Git por ser fonte externa recuperável.
