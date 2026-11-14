---
type: Experiment
title: "C241: janelas condicionais de plano orbital sobre uma câmera de Vila do Conde"
description: "Geometria de plano para NORAD 528/637, duas hipóteses J2 e dois cortes civis; não identifica queda em Conde"
experiment_id: C241-PLANE-20261114
verification_status: SECONDARY_LINEAGE_MODERN_GEO_PROXY_NOT_HISTORICAL_CONSTRAINT
---

# Dois planos sobre Conde: ensaio condicional, não reconstrução do impacto

**Pergunta:** as orientações catalográficas dos planos do NORAD 528 e do NORAD 637 produziriam janelas de cruzamento distintas nas datas de 6 a 9 de novembro de 1963, sem pressupor fase orbital? Issue [#870](https://github.com/franklinbaldo/conde-incident/issues/870).

**Insuma:** o Parquet histórico secundário `tle_1963.parquet`, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, do espelho Space-Track; apenas a **última época pré-janela** de cada objeto, sem trocar designações. 528: 27/10/1963 14:40:16 UTC (RAAN 198,526093°, inclinação 81,861504°). 637: 05/11/1963 07:54:43 UTC (RAAN 269,681000°, inclinação 81,876602°). Últimos dois movimentos médios por objeto alimentam uma secante pré-corte, não dados futuros. Leia `c241_plane_index.json` para SHA-256 dos três arquivos geográficos versionados e identificação da imagem.

**Geografia bloqueada:** `CGEO-20` distingue CENTRO20 e VILA20, mas **nenhum dos dois possui ponto geocodificado histórico**. `conde_ibge_2022_sirgas2000.json` descreve o polígono municipal de 2022, não a sede nem o local de queda. Para testar o operador sem inventar coordenada, usamos exclusivamente a posição da **câmera fotográfica CGEO15-CAMERA-01, de setembro de 2022**, lat. −11,7988°, lon. −37,621475°, próxima à igreja da Vila, **não como ponto de queda, centro de 1963 ou observação orbital**. O ramo `CENTRO20` permanece `NOT_EVALUATED_NO_CUSTODIED_POINT`. É uma análise contrafactual dessa posição moderna, não a geometria validada do relato.

**Operador:** plano não orientado, normal `(sin(i)sin(Ω), −sin(i)cos(Ω), cos(i))`, distância absoluta `|n·r_ECI|` em km até a reta normal do plano. GMST analítico com UTC aproximando UT1 e raio geocêntrico WGS84 como aproximação; em 1963 não há EOP/sigma instrumental custodiado. Precessão secular `J2`, inclinação e excentricidade persistentes; dois ramos: semieixo constante e decaimento linear por última secante (528: −3,350306 km/dia, 637: −7,588396 km/dia). Esses valores **não** medem massa, arrasto terminal ou posição em órbita.

| Dia UTC | 528, referência moderna, hora da Bahia (a constante, aprox.) | 637, referência moderna, hora da Bahia (a constante, aprox.) |
|---|---|---|
| 06/11 | 05/11 21h09; 06/11 08h51 | 06/11 02h33; 14h15 |
| 07/11 | 06/11 21h01; 07/11 08h43 e 20h52 | 07/11 02h24; 14h06 |
| 08/11 | 08h34; 20h44 | 08/11 02h15; 13h57, **fora do corte NASA em ambas as leituras** |
| 09/11 | 08h26; 20h35, **fora do corte NASA em ambas as leituras** | 09/11 02h06; 13h48, **fora do corte NASA em ambas as leituras** |

Os horários da linha 07/11 incluem cruzamento às 00:00 UTC (21h00 local de 06/11), para não confundir dia UTC com dia da Bahia. No ramo de `a` variável as horas diferem em menos de um minuto no período estudado. As janelas de **50, 100 e 200 km** são cenários geométricos, não tolerâncias do sensor; perto de uma raiz a largura integral da janela de 50 km é aproximadamente **3,69 minutos**. O script publica início, fim, duração e cortes por interpretação de cada janela, além de curvas em intervalos de três minutos. Os contadores com 256 amostras gaussianas usam o RMSE de RAAN do próprio espelho secundário (528: 0,039199°, 637: 0,054968°) multiplicado por 1, 3 e 10: **fração de sensibilidade computacional, não posterior nem probabilidade de queda**.

**Dia de decaimento:** registro NASA atribui apenas **07/11 ao 637** e **08/11 ao 528**, sem hora e fuso de queda. São aplicados dois cortes hipotéticos ao fim do dia: UTC e dia civil da Bahia (UTC−3). Os campos `UTC_CIVIL_DAY_valid_rows` e `BAHIA_CIVIL_DAY_valid_rows` truncam as curvas. Cruzamentos fora do domínio são exclusivamente extensões geométricas não interpretáveis como presença do objeto.

**Confronto documental adversarial:** o FBIS imprime `RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 2330 8 NOV 63 W` (CGEO-18). **Se**, e somente se, `2330` representar GMT, é **20h30 da Bahia**; é carimbo de transmissão, **não hora do fenômeno**. A raiz condicional do 528 para a câmera moderna cai cerca de 20h43 local, diferença de ~13 minutos da transmissão sob essa interpretação. Logo nem sequer uma coincidência de relógios demonstrada, muito menos um ponto de impacto. O ramo alternativo do significado/fuso de `2330` permanece aberto; o 637 já ultrapassara as duas leituras possíveis de seu dia catalogado ao horário de transmissão. Nenhuma inferência deve usar esse carimbo como tempo de evento.

**Reprodução:** `uv run --with pyarrow python tools/c241_conditional_plane_windows.py --parquet <arquivo_pin> --output-dir research/statistics`; acrescente `--check` para comparar bytes de 21 saídas versionadas, sem rede nem download implícito. Controle de SHA em ingestão, código sem uso de estado futuro e testes adversariais: órbita polar, latitude acima da inclinação, RAAN +180°, truncamento civil, tamper de ponto geográfico, intervalos aninhados e replay. A confiança dos cruzamentos é **condicional aos insumos e operadores**, não observacional.

**Decisão:** `phase_constraint=NOT_EVALUATED`, `posterior=false`, `active_constraint=false`. O ensaio pode orientar **qual documento com hora do evento seria discriminatório** e mostrar que diferentes planos cruzam a região em horários distintos. Não prova que 528/637 estavam sobre o lugar, que um fragmento tocou o solo, nem localização, instante ou probabilidade de queda em Conde.
