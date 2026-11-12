---
type: Guide
title: "C149–C151: consistência hipsométrica condicional, Recife 7–9/11/1963"
description: "78 camadas de pressão/geopotencial NOAA em Recife, sem incerteza instrumental calibrada ou transferência geográfica."
---

# Hipsometria: a coluna local tem espessura, mas não é uma trajetória até Conde

## Fonte, época, lugar e independência

Partimos das três sondagens arquivísticas NOAA/NCEI **IGRA BRM00082900**, datas nominais **7, 8 e 9 de novembro de 1963, 12 UTC**, de [ZIP original](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip) (7.834.492 bytes; SHA-256 `0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc`) e [layout IGRA](https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt). Os excertos imutáveis são verificados pelo `audit_igra_recife_window.py` e pelo script auditado `audit_igra_recife_dry_density.py`: reprocessar os JSONs exige bytes, estação e data íntegros.

Catálogo atual: Recife, latitude −8,05°, longitude −34,9167°, cota de estação 7 m; **não se reconstituiu a localização instrumental em 1963**. Alturas por nível são geopotenciais acima do nível do mar, não altitudes geométricas. O campo `RELTIME=9999` não informa hora real de soltura. As três sondagens pertencem à **mesma família arquivística NOAA/NCDC (`ncdc6301`)**: níveis, campos p/T/GPH e datas não contam como instrumentos independentes.

## Hipótese física mensurável e observável derivado

Os **81 níveis** de pressão, temperatura e altura geopotencial realmente registrados formam **78 pares de níveis adjacentes** com pressão decrescente e geopotencial crescente: 28, 25 e 25 nos três dias. Sem interpolar níveis, a diferença observada é `ΔH = H_upper − H_lower` (m geopotenciais). Sob equilíbrio hidrostático, gás ideal seco e temperatura média da camada **aproximada pelos dois extremos**:

`ΔH_dry_assumed = (R_d/g0) × [(T_lower,K+T_upper,K)/2] × ln(p_lower/p_upper)`, com `R_d=287,05 J/(kg K)` e `g0=9,80665 m/s²`. Invertendo p/GPH, `T_v,implied = g0 ΔH/[R_d ln(p_lower/p_upper)]` é **temperatura média virtual implicada pelo modelo**, não uma medição independente de temperatura. Referência da identidade e da necessidade de temperatura média *virtual*: [Stull, Practical Meteorology, eq. 1.26](https://geo.libretexts.org/Bookshelves/Meteorology_and_Climate_Science/Practical_Meteorology_%28Stull%29/01%3A_Atmospheric_Basics/1.10%3A_Hypsometric_Equation); [MetPy, documentação da integração hipsométrica](https://unidata.github.io/MetPy/v0.10/api/generated/metpy.calc.thickness_hydrostatic.html).

| Dia nominal UTC | Níveis p/T/GPH | Pares adjacentes | Média de \|ΔH observado − seco/extremos\| | Máximo absoluto |
|---|---:|---:|---:|---:|
| 07/11/1963 | 29 | 28 | 10,191581 m | 28,028308 m |
| 08/11/1963 | 26 | 25 | 7,613712 m | 22,969284 m |
| 09/11/1963 | 26 | 25 | 8,428959 m | 24,963429 m |

**Essas diferenças NÃO são erros de instrumento, calibração, limites físicos, incertezas estatísticas nem resíduos independentes.** Temperatura interna da camada não observada continuamente, vapor d'água, arredondamento da pressão/GPH, níveis muito próximos em pressão e hipótese de equilíbrio afetam o contraste. O valor `T_v,implied` pode ser instável quando `ln(p_lower/p_upper)` é pequeno. Não atribuir significado de acurácia instrumental aos dígitos impressos ou usar os máximos como envelopes de Conde.

## Ligação cumulativa sem ativar domínio

- **C149–C151** (`p,T,GPH` das três sondagens) → `ΔH_Recife` observado e `ΔH_dry_assumed` derivado → teste condicional de coerência de camadas e eventual seleção de cenários locais para densidade/arrasto; **não** representa uma nova fonte ou campo contínuo.
- **C144–C146**, cartas de superfície, vêm de uma família documental separada; não são sondagens verticais coincidentes, nem medição de incerteza espacial Recife→Conde. **C17–C23**, índices geomagnéticos/fluxo solar e hipóteses de ligação orbital, pertencem a outro domínio e não corrigem a coluna de Recife. **C193**, Explorer XVII em abril–junho/1963 e outra altitude, não calibra a termósfera orbital em 8/11/1963.
- `ΔH_Recife` → `ρ_Recife(z,t)` **CONDICIONAL** (modelo seco/húmido e metadados instrumentais incompletos); `ρ_Recife` → `ρ_Conde(z,t)` **PENDING** (transferência espacial/temporal e covariâncias desconhecidas); `ρ_Conde` → arrasto/deriva do fragmento **PENDING** (trajetória/propriedades físicas não fixadas). **Nenhuma restrição Θ ativada.**

Entradas para o Castor só como verificação de plausibilidade de um cenário local em Recife, nunca densidade medida em Conde ou longitude/latitude de queda. Os quatro campos de incerteza permanecem `null`, explicitamente **desconhecidos**, e nenhum resíduo hipsométrico substitui estimativa deles.

## Reprodução e arquivos

- `python3 tools/audit_igra_recife_hypsometry.py --check` verifica novamente hashes e igualdade dos três arquivos JSON gerados de originais;
- `python3 -m unittest discover -s tests -p test_igra_recife_hypsometry.py -v` testa 78 pares, unidade SI, independência, não-transferência, adulteração de fonte/época e rejeição de pares impossíveis;
- [`07`](igra_recife_19631107_hypsometric_consistency.json), [`08`](igra_recife_19631108_hypsometric_consistency.json), [`09`](igra_recife_19631109_hypsometric_consistency.json) guardam cada camada com pressão, geopotencial, temperaturas, hipóteses e proveniência.

**Estado científico:** `RECIFE_HYPSOMETRIC_CONDITIONAL_CHECK_NO_TRANSFER`. Resultado verificável de comparação *dentro* da única família sondada; nenhuma observação em Conde nem inferência de reentrada.
