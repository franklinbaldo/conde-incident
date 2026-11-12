---
type: Guide
title: "C149–C151: sensibilidade à umidade em Recife, 7–9/11/1963"
description: "Densidade ideal úmida condicional em 22 níveis com RH, com limites e proveniência."
---

# Umidade e densidade: o que os dados de Recife permitem calcular

**Pergunta delimitada:** a aproximação rho_dry=p/(R_d*T) extraída dos perfis IGRA de Recife (PR #205) pode ser confrontada com um modelo explícito de vapor d'água, sem presumir dados ausentes ou extrapolação para Conde?

## Custódia e independência

- **Fonte:** NOAA NCEI IGRA BRM00082900, [arquivo original de período completo](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), 7.834.492 bytes, SHA-256 0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc; [dicionário IGRA](https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt). O script revalida as três ocorrências brutas por hash, estação, época e fonte upstream ncdc6301 usando audit_igra_recife_dry_density.py. Os hashes específicos dos três excertos e os índices dos níveis estão no [JSON derivado](igra_recife_19631107_09_moist_sensitivity.json).
- **Lugar:** estação catalogada Recife, latitude −8,0500°, longitude −34,9167°, altitude de catálogo 7 m. Mudanças históricas de localização do observatório não foram reconstituídas; alturas por nível são metros geopotenciais ASL.
- **Datas:** 7, 8 e 9 de novembro de 1963, nominalmente 12 UTC. RELTIME=9999: horário real de soltura não declarado. As três sondagens compartilham uma família arquivística, não três redes independentes.
- **Dados lidos:** 81 pares de pressão, temperatura e altura realmente registrados; RH presente em 32 níveis (10/6/16). Desses, 22 têm temperatura de pelo menos 0 °C (8/6/8), 10 têm temperatura abaixo de 0 °C e 49 não têm RH. Todos os 59 níveis excluídos permanecem sem cálculo, não recebem RH presumida.

## Modelo condicional auditado

Adotamos constantes convencionais modernas R_d=287,05 e R_v=461,5 J kg⁻¹ K⁻¹. Somente quando há RH registrada e 0 ≤ T_C ≤ 50 °C, adotamos como hipótese explícita que RH se refere à pressão de saturação sobre água líquida, usando a aproximação Magnus de Alduchov e Eskridge:

e_s(T) = 6,1094 exp(17,625 T_C/(243,04+T_C)) hPa;

e = RH/100 × e_s; rho_moist = [(p−e)×100/R_d + e×100/R_v] / (T_C+273,15).

Referência da lei empírica: Alduchov e Eskridge (1996), *Journal of Applied Meteorology* 35, 601–609, [artigo de referência](https://scixplorer.org/abs/1996JApMe..35..601A/abstract). A separação das pressões parciais é a equação de estado ideal de uma mistura gasosa. A convenção histórica de RH, os vieses do instrumento, condensados e erros não estão calibrados; os valores abaixo são sensibilidade de modelo, não medição de densidade real.

| Dia nominal | Níveis cálculáveis | Diferença relativa modelo úmido/seco a 1000 hPa |
|---|---:|---:|
| 07/11/1963 | 8 | −0,829217% |
| 08/11/1963 | 6 | −0,695472% |
| 09/11/1963 | 8 | −0,676188% |

O maior decréscimo relativo calculado nos 22 pontos é 0,865652%, no nível 933 hPa do dia nominal 9. Esses percentuais não são margens de erro, máximos regionais, priors ou intervalos de confiança. São diferenças matemáticas entre duas hipóteses no mesmo nível e sondagem, não entre fontes observacionais independentes.

## Grafo acumulativo e bloqueios de inferência

Aresta C149–C151 (p,T,RH Recife) → rho_recife_condicional está conectada como hipótese computável, sem restrição Theta ativa. Aresta rho_recife_condicional → rho_Conde(z,t) permanece PENDING: faltam transferência espacial/temporal verificada, erro de calibração, época e localização histórica instrumental, além do perfil regional. Aresta rho_Conde(z,t) → arrasto/deriva permanece PENDING: faltam trajetória, propriedades do fragmento e modelos de movimento validados. O JSON registra os vínculos, inclusive os contextos C17–C23 (índices geomagnéticos), C144–C146 (cartas sinóticas de superfície, outra família) e C193 (densidade termoesférica Explorer XVII de outros meses e altitudes); nenhum substitui observação local.

**Proibições interpretativas:** não chamar rho_moist de densidade observada, não transportar Recife a Conde, não extrapolar a 100 hPa/termósfera, não preencher RH ausente, não inferir dia/hora de reentrada, local de queda, probabilidade ou balão. RH de 1963 é da mesma cadeia NOAA/IGRA de p/T; somar 22 níveis não gera 22 testemunhas independentes.

## Reprodutibilidade

Rodar python3 tools/audit_igra_recife_moist_sensitivity.py --check confronta as fontes originais já fixadas e o [JSON](igra_recife_19631107_09_moist_sensitivity.json). Rodar python3 -m unittest discover -s tests -p test_igra_recife_moist_sensitivity.py -v executa oito testes contra adulteração de escopo físico, RH ausente e temperatura abaixo de zero, fonte/independência, densidade, limites de pressão e partição dos níveis.
