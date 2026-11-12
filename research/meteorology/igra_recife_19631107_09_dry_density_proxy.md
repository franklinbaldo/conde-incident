---
type: Guide
title: "C149–C151: temperatura e proxy de densidade ideal seca em Recife, 7–9/11/1963"
description: "81 pares históricos pressão-temperatura NOAA, uma fórmula explicitamente assumida, sem calibração para Conde nem termósfera."
---

# Recife: pressão e temperatura observadas, densidade seca apenas condicional

## Pergunta e resultado

As sondagens originais NOAA/IGRA **BRM00082900**, arquivadas com épocas nominais de **12 UTC de 7, 8 e 9 de novembro de 1963**, contêm temperatura, pressão e altura geopotencial nos **29, 26 e 26 níveis originais**, respectivamente. Esta fatia calcula **81 valores condicionais** de densidade pelo gás ideal *seco*, sem atribuir densidade medida a Conde, ao objeto ou à trajetória orbital.

Fonte arquivística: [NOAA NCEI, ZIP integral da estação](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), 7.834.492 bytes, SHA-256 0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc; [layout oficial dos registros](https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt). Excertos dos três dias, mantidos byte a byte em base64, passam por SHA-256 definido em [audit_igra_recife_window.py](../../tools/audit_igra_recife_window.py). Todos vêm do upstream **ncdc6301**: não são três fontes meteorológicas independentes. Longitude catalogada −34,9167°, latitude −8,0500°, estação a 7 m acima do nível do mar; **não** há reconstrução confirmada da estação exata de 1963. O horário **real de lançamento é desconhecido** (RELTIME=9999) apesar da hora nominal 12 UTC.

## Observável e hipótese

O IGRA registra PRESS em Pa, TEMP em décimos de °C, GPH em metros geopotenciais ASL; TFLAG indica filtros de qualidade, **não erro instrumental**. O script preserva flag de temperatura, flag de altura e RH conforme disponível (sem substituir ausências por zero).

Assume-se gás ideal seco com **R_d = 287,05 J/(kg K)**, a formulação meteorológica usual de p = rho R_d T, em que T_K = 273,15 + T_C. Resulta a variável **derivada**, não diretamente observada:

rho_dry_proxy(p,T) = p_Pa / [287,05 (273,15 + T_C)] em kg/m³.

Sem umidade/temperatura virtual validada, isso **não é medição de densidade de ar úmido**. Mesmo com RH informado, a campanha não apresentou erro instrumental calibrado. Resolução decimal não equivale a intervalo de confiança. A hipótese seca serve para testar dependências e como entrada de cenário **somente no local, altitude e horário nominal da sondagem**. Requer-se tratamento de umidade, temperatura virtual, localização, tempo real e erro de transferência antes de condicionamento fora de Recife.

## Amostra reproduzida em níveis isobáricos comuns

| Pressão | 7/11 (kg/m³) | 8/11 (kg/m³) | 9/11 (kg/m³) |
|---|---:|---:|---:|
| 1000 hPa | 1,161044372 | 1,161044372 | 1,164148250 |
| 850 hPa | 1,027287630 | 1,024090124 | 1,027287630 |
| 700 hPa | 0,863679670 | 0,862152925 | 0,864598315 |
| 500 hPa | 0,651770559 | 0,651039738 | 0,649583002 |
| 300 hPa | 0,434107619 | 0,432669879 | 0,435373502 |
| 100 hPa | 0,182441144 | 0,180363119 | 0,181490682 |

São 18 valores derivados **dentro da mesma família NOAA/NCDC**, não 18 instrumentos independentes. Os 81 valores completos, junto com a temperatura, geopotencial, pressão, flags e RH publicado, estão nos [três arquivos por dia](igra_recife_19631108_dry_density_proxy.json) em JSON. Níveis com RH informado: **10/29**, **6/26** e **16/26**. Níveis sem RH continuam null, sem correção de umidade inferida.

## Relações com o grafo da pesquisa e transferências não autorizadas

- **C149–C151**: esta extração usa **as mesmas três sondagens** e acrescenta o eixo termodinâmico, não fonte independente, e não altera C152 (teste de deriva com aproximações explícitas).
- **C144–C146**: as cartas de superfície da Marinha pertencem a outra custódia, mas não são medidas verticalmente emparelhadas de temperatura/umidade em Recife, nem de densidade local em Conde.
- **C17–C23**: GFZ Kp/Ap e NRCan F10.7 são entradas de clima espacial, não fornecem temperatura ou densidade nos 81 níveis de Recife. CelesTrak é redistribuidor, não terceira instrumentação.
- **C193**: Explorer XVII (abril–junho de 1963) mede outra altitude/época; **os perfis de Recife chegam a ~30 km e não calibram a termósfera orbital** para o NORAD 528 em novembro.
- **🦫 Castor (contrato condicional)**: rho_dry_proxy_Recife(date_nominal,p,T,GPH) permite conferir dependência física de p,T em um cenário local. Para tornar restrição de arrasto/deriva, faltam perfil espaço-temporal apropriado, erro instrumental, umidade ou temperatura virtual, órbita/altitude, coeficiente balístico e modelo validado. uncertainties=null é **desconhecido**, nunca zero.

**Estado:** RECIFE_PT_OBSERVED_DRY_PROXY_CONDITIONAL_NO_TRANSFER. Nenhuma queda, densidade termoesférica do 528, horário de reentrada ou posição de Conde é inferida.

## Reprodução offline

- python3 tools/audit_igra_recife_dry_density.py --check
- python3 -m unittest discover -s tests -p test_igra_recife_dry_density.py -v

Os três JSON são gerados por --day 07, 08, 09 a partir dos excertos históricos com hash, sem interpolação.
