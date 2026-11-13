---
type: Guide
title: "C241-L36: ligação cumulativa entre registro ONU e boletim NASA de 1963"
description: "Auditoria de doze diferenças entre valores impressos com datas editoriais distintas para 527, 528 e 529, sem promover taxas orbitais."
---

# C241-L36: valores impressos e épocas ainda latentes

Esta fatia deriva **12 diferenças aritméticas de células publicadas**, ligando as linhas de **1963-3-A/B/C** do registro original dos EUA à ONU ao catálogo NASA de abril, sem fabricar medições novas.

- Fonte anterior: [ONU A/AC.105/INF.30](https://www.unoosa.org/documents/pdf/inf030E.pdf), data do documento **13/03/1963**, com estado declarado até **24:00Z de 31/01/1963**, página PDF índice 1. Células e SHA-256 previamente validados em **C241-L33** (`fbee0e928a2d81e62c97c102eef70d4f4931dd500372a4bf735bd8891c6188b8`).
- Fonte posterior: [NASA SSR nº 9, 30/04/1963](https://ntrs.nasa.gov/api/citations/19630012128/downloads/19630012128.pdf), tabela na página impressa 5, índice PDF 6, *data as of* **14:30Z de 30/04/1963**, capturada em **C241-L16** (`87b8c1be1d074dff4b605b422f6a8836c2ebdf80ca4ac0568373b168cc457a38`).
- Identidade catalográfica internacional/número NORAD: **C241-L32**, [NASA 1977, página impressa 43](https://ntrs.nasa.gov/citations/19780009188), que associa 003A/003B/003C a 527/528/529. O documento de 1977 é retrospectivo, não o instrumento original.

## Resultado numérico reproduzível

Regra para cada célula: **valor impresso NASA abril menos valor impresso ONU janeiro**; diferença nominal exata em aritmética decimal, não taxa temporal.

| Objeto | Período nodal (min) | Inclinação (°) | Apogeu (km) | Perigeu (km) |
|---|---:|---:|---:|---:|
| 527 / 003A | −0,1 | −0,08 | +18,4 | −19,5 |
| **528 / 003B** | **−0,4** | **−0,10** | **−0,5** | **−41,4** |
| 529 / 003C | −0,4 | −0,09 | +5,5 | −39,4 |

**Interpretação limitada:** os **41,4 km** de diferença do perigeu *publicado* do 528 são verificáveis por subtração de `435` e `476,4`, mas não são erro de radar, taxa de decaimento, distância percorrida, intervalo de previsão, nem restrição na posição terminal. As datas de corte dos boletins não identificam as épocas usadas para ajustar as órbitas. Embora haja duas instituições editoras, os dados vêm de um canal governamental dos EUA potencialmente compartilhado com NORAD/SAO, logo não equivalem a dois sensores independentes.

A relação com o 528 preserva quatro observáveis impressos para eventual uso nos operadores de período, inclinação, apogeu e perigeu. Para ativá-los em simulação ou Lean, faltam épocas **instrumentais**, observadores, frame, forma de obtenção das soluções e erros/covariância. A diferença da inclinação não é prova de mudança do plano: quadros, convenções e ajustes não foram identificados.

**Progresso cumulativo:** 12 conexões documentais, zero novas medições instrumentais, zero restrições físicas ativadas, nenhuma probabilidade, horário ou lugar inferido. Status `DOCUMENTARY_PRINTED_DIFFERENCES_NO_PHYSICAL_RATE`.

## Validação

    python3 -m unittest discover -s tests -p test_tle_un_nasa_crosscutoff_audit.py -v
    python3 tools/tle_un_nasa_crosscutoff_audit.py --output /tmp/c241-l36.json

O teste do GitHub Actions repete ainda os hashes dos **dois PDFs oficiais**, sem presumir que o seu conteúdo possa ser deduzido a partir da página de catálogo. Os **18 testes adversariais** rejeitam mudança de identidade ou células, invenção de covariância, promoção a taxa física, prova Lean ou medição adicional.

**Próxima evidência discriminante:** ficha original de rastreamento e determinação do decaimento SPADATS/NORAD do S00528, com estação, época UTC, referencial, erro e método; ou linha soviética de 1963 auditada no fac-símile com esses campos.
