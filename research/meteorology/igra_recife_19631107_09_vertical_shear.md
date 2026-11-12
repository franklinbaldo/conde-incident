---
type: Guide
title: "C149–C151: cisalhamento vertical observacional em Recife, 7–9 novembro 1963"
description: "Diferenças vetoriais finitas por quilômetro geopotencial em 42 pares de níveis medidos, sem extrapolação regional."
---

# Cisalhamento vertical observado: Recife, 7–9/11/1963

## Pergunta científica

A simplificação de vento horizontal invariável com altitude é compatível **exatamente** com as sondagens históricas de Recife (C149–C151)? **Não.** Entre níveis consecutivos com vento registrado, u e v variam, inclusive em sinais. Este é um teste **local e observacional de invariância vertical**, não modelo de vento contínuo, deriva de fragmentos nem evidência de Conde.

A [série NOAA/NCEI IGRA2.2 da estação BRM00082900](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip) tem 7.834.492 bytes; SHA-256 `0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc`. São três perfis nominais **12h UTC** de 7, 8 e 9/11/1963; hora real de lançamento **desconhecida** em todos (`RELTIME=9999`). As coordenadas catalogadas são latitude −8,0500°, longitude −34,9167° e altitude da estação 7 m ASL, sem demonstração de localização exata em 1963. Todos derivam do mesmo upstream NCDC `ncdc6301` e não são três fontes arquivísticas independentes. Os três excertos brutos preservados no repositório são verificados pelos hashes anteriores em [audit_igra_recife_window.py](../../tools/audit_igra_recife_window.py).

## Extração, unidades e controle de qualidade

O [formato oficial IGRA](https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt) usa pressão em Pa (aqui hPa), altitude **geopotencial** em metros ASL, direção meteorológica `FROM` em graus e velocidade em décimos de m/s. Para cada nível informado: `u=-V sin(d)` (leste) e `v=-V cos(d)` (norte). A diferença entre pontos adjacentes do mesmo perfil é

`S(i,i+1) = 1000·sqrt((u[i+1]-u[i])²+(v[i+1]-v[i])²)/(H[i+1]-H[i])`

em **m/s por quilômetro geopotencial**. É uma diferença finita entre extremos observados, **não uma medição dentro do estrato** e não uma derivada vertical em altura geométrica. A flag `ZFLAG` de geopotencial é preservada para cada extremo; `B` indica passagem por checagens climatológicas tier-1/tier-2 e **não** uma incerteza de medição conhecida. Velocidade zero registrada em 09/11 a 50 hPa não permite interpretar fisicamente uma direção de vento, ainda que conste `0°`.

Por data, 15 níveis possuem u/v completos e 14 pares adjacentes são deriváveis. Foram rejeitados como lacunas os **14/11/11 níveis sem vento**, respectivamente; não se fabricou interpolação desses valores. No nível de 08/11, os 11 níveis sem vento continuam desconhecidos. A resolução numérica do arquivo não é erro instrumental. A altitude real geométrica e qualquer deslocamento da estação em 1963 não foram reconstruídos.

## Diferenças finitas de maior magnitude por quilômetro (somente dentro do perfil)

| Data nominal | Par de pressão | Alturas geopotenciais | `|Δ(u,v)|` | `S` |
|---|---|---|---:|---:|
| 7/11 | 1016–1000 hPa | 10–151 m | 1,070587 m/s | **7,592817 m/s/km** |
| 8/11 | 300–250 hPa | 9.745–11.007 m | 7,719240 m/s | **6,116672 m/s/km** |
| 9/11 | 1016–1000 hPa | 10–151 m | 1,044666 m/s | **7,408979 m/s/km** |

Máximos de `S` **somente entre os 14 pares observados por dia**. Um estrato vertical estreito pode ter maior razão apesar de menor diferença vetorial absoluta. Não usar esses máximos como intensidade verdadeira máxima, limite de turbulência, incerteza, tendência entre dias ou escala de mistura.

O [JSON verificável](igra_recife_19631107_09_vertical_shear.json) contém **42 pares**, pressões, alturas, flags `ZFLAG`, duas componentes assinadas, magnitude, presença de extremidade calma, identificação da sondagem, SHA original e limites de interpretação. O [script reprodutor](../../tools/audit_igra_recife_shear.py) exige os bytes originais com hash e recusa níveis sem altura, pressão fora de ordem ou vetor incompleto. Há sete [testes negativos e positivos](../../tests/test_igra_recife_shear.py).

## Dependências e variável candidata

- **C149–C151**: deriva apenas dos três perfis NOAA/NCDC, sem criar outro sensor. C151 (Recife 8/11) é referência instrumental; estes 42 pares não são 42 medições independentes.
- **C144–C146**: as cartas da Marinha são sinóticas, com pressão superficial de outra custódia, mas não medem estes ventos de altitude nem fornecem erro Recife→Conde.
- **C17–C23**: índices GFZ e fluxo solar canadense descrevem clima espacial, não cisalhamento troposférico/estratosférico local. CelesTrak repete parte das fontes, não é instrumento independente adicional.
- **C193**: Explorer XVII de abril–junho/1963 mediu termósfera em outros meses e altitudes. Estes ventos até ~26,7 km **não** constrangem densidade orbital do NORAD 528.
- **C150**: a hora nominal não é hora efetiva observada. Comparar dias não permite taxa de mudança por hora.
- **Conexão condicional para o 🦫 Castor**: variável `S_Recife,196311DD,H_i,H_j` derivada, unidade m/s/km geopotencial, status `CONNECTED_PENDING_SPATIOTEMPORAL_TRANSFER`. Para uma restrição ativa sobre deriva de fragmentos, exigem-se posição e hora do fragmento, perfil vertical temporal do objeto, vento regional na rota, erro instrumental e de transferência validado, convenção geopotencial→geometria e modelo de arrasto aerodinâmico. Todos ausentes; `regional_transfer_uncertainty_m_s=null` **não significa zero**.

**Resultado:** incremento de conectividade e falsificação da hipótese simplificadora de vento vertical exatamente constante em Recife; nenhuma mudança admissível de domínio de queda ou de arrasto orbital. Não existe aqui vento observado em Conde.

## Reprodução

```sh
python3 tools/audit_igra_recife_shear.py --check
python3 -m unittest discover -s tests -p test_igra_recife_shear.py -v
```

O workflow de integração no HEAD roda todos os `tests/test_*.py`, incluindo essa suíte, e o workflow `prek` verifica formato OKF e tamanho máximo dos novos arquivos.
