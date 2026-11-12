# 🦎 Lagarto: entradas históricas condicionais de clima espacial, 7–9/11/1963

Inspeção de 12/11/2026. Complementa C17–C23, C144–C151 e C193. A planilha JSON ao lado preserva as séries diárias e trihorárias, URLs exatas, SHA-256 dos documentos brutos, relógios e os vetores de entrada que podem alimentar um modelo termoesférico. **Não há medida de densidade ou ventos de Conde, nem localização/horário de queda. Estado CONNECTED_PENDING_CALIBRATION.**

## Fontes auditadas, lugar, altitude, incerteza e independência

| Fonte | Registro histórico, unidade, época e posição | Origem, incerteza e independência |
|---|---|---|
| [GFZ Potsdam, API](https://kp.gfz.de/en/data) | Índices planetários: Kp quasi-logarítmico e ap linear em intervalos de **3h UTC**, Ap diário. Rede global de observatórios, **não Conde**, altitude física não aplicável. Capturados 4–10/11/1963. | Retornaram status definitivo em todos os 56 intervalos Kp/ap e sete dias Ap. Hash e URLs de cada chamada estão no JSON. Erro/covariância histórica **não disponibilizados**: nulos. Kp, ap e Ap são **uma família observacional**, não três medições independentes. |
| [Natural Resources Canada, F10.7 1947–1996](https://www.spaceweather.gc.ca/solar_flux_data/daily_flux_values/F107_1947_1996.txt) | Rádio solar 10,7 cm em **sfu** (10⁻²² W·m⁻²·Hz⁻¹). Série canadense da fase Ottawa em 1963; não há altitude de atmosfera terrestre. Uma data por linha; hora efetiva de observação não decodificada. | Baixados **1.184.761 bytes**, SHA-256 **60c51e8878dc70561e615b5cefb26315c201116fe4560799ec19237bed691c61**. Colunas observada, ajustada e URSI-D são distintas. Escolhida exclusivamente a **observada** para cumprir NRLMSISE. Erro medido não inferido. Família solar distinta da família GFZ; CelesTrak reapresenta dados, não constitui terceira observação. |
| [NOAA IGRA Recife](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), C149–C151 | Vento/pressão/altitude da estação **Recife**, com data 7–9/11/1963 e hora **nominal** 12 UTC, RELTIME=9999. | Observação instrumental em outro lugar; não mede densidade termoesférica de novembro, não transfere vento para Conde sem erro espaço-temporal. Não se recontaram observações como independentes do NCDC/UADB. |
| Explorer XVII, C193 | Medidas termoesféricas de abril–junho de 1963, outras datas e trajetórias. | Instrumento independente, **não** mede diretamente novembro de 1963 sobre Conde. Usar para discutir variabilidade, jamais para impor densidade local em 8/11. |

## Variáveis completas e limites de interpretação

A [implementação científica NRLMSISE-00 em NCAR/GLOW](https://github.com/NCAR/GLOW/blob/master/nrlmsise00.f) documenta o fluxo observado F10.7 do **dia anterior**, média **centrada** de 81 dias de fluxo solar e os sete componentes do histórico geomagnético ap: Ap diário; ap dos instantes t, t−3h, t−6h, t−9h; média de oito bins de t−12h a t−33h; e média de oito bins de t−36h a t−57h.

As horas **12 UTC de 7/8/9 novembro** são **pontos de avaliação escolhidos somente para verificar o vetor**, não horários de lançamento ou reentrada. A média de 81 dias retrospectiva inclui valores coletados após a data de avaliação. NRLMSISE também requer posição geodésica, altitude em km, hora UTC e hora solar local, não preenchidas no arquivo. O estado orbital, as incertezas do arrasto e o modelo de discrepância também não foram identificados.

| Época de avaliação UTC, artificial | F10.7 dia anterior (sfu) | F10.7 81 dias observada (sfu) | Ap diário | Vetor ap 7 posições |
|---|---:|---:|---:|---|
| 07/11 12 UTC | 78,6 | 82,190123 | 39 | [39, 27, 48, 22, 39, 13,875, 2,375] |
| 08/11 12 UTC | 76,6 | 82,265432 | 46 | [46, 32, 32, 80, 67, 43,75, 13,875] |
| 09/11 12 UTC | 75,4 | 82,374074 | 33 | [33, 32, 18, 32, 22, 42,625, 43,75] |

Conferência cruzada: no dia **8/11 Ap=46**, o pico Kp **6** ocorreu no bin 06–09 UTC, equivalente a **ap=80** naquele bin, **não** a ap=6; F10.7 **observado em 8/11 é 75,4 sfu**, que entra na avaliação *do dia seguinte*, 9/11. São índices planetários, sem resolução espacial que permita identificar trajetória de um fragmento ou atmosfera específica de Conde.

**Conexão física futura:** entrada do modelo com F107, F107A e série ap → densidade condicional rho(t, latitude, longitude, altitude, hipóteses) → arrasto condicional se houver trajetória e coeficiente balístico. Não preencher rho sem localização, altura, calibração do propagador e erros. Nenhuma restrição numérica nova foi ativada; as **três épocas e seus históricos** constituem nova conectividade de observáveis com **dois** circuitos de origem.

**C20:** benchmark anterior de ganho com Ap/F10.7 melhorou dois cortes e piorou dois; este trabalho **não afirma melhora preditiva**. **C21:** último TLE do 528 no espelho consultado ainda é de 27/10; não há observação de reação a perturbação de 7–9/11. **C193:** Explorer XVII prova variabilidade em outros meses, não uma densidade em novembro. **C144–C151:** carta de pressão de superfície da Marinha e ventos de Recife não geram inferência geográfica para Conde.

## Reprodução offline

Executar: python3 tools/validate_1963_space_weather.py research/meteorology/space_weather_msise_inputs_1963_11_07_09.json

O verificador testa a série de 85 dias F10.7, 56 bins trihorários GFZ, sete dias Ap, a relação de médias entre ap e Ap e recomputa os vetores de 7 posições e fluxos centrados de 81 dias. Rejeita os campos de local, altitude, densidade, erro físico e hora solar preenchidos sem fonte. O CI roda isso no HEAD da PR. Os SHA-256 e tamanhos da captura direta permitem repetir coleta e identificar alteração posterior do provedor.

**Entrega ao Castor:** utilizar esses inputs como condicionais explícitos após selecionar época/estado; não tratar disponibilidade histórica do índice como calibração independente do arrasto de NORAD 528 ou localização da notícia.
