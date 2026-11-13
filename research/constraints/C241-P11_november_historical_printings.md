---
type: Guide
title: "C241-P11: 16 campos NASA de novembro, holdout e controle 3A"
description: "Quatro linhas originais NASA, quantização condicional, erro de previsão fora da amostra e ausência de restrição orbital."
---

# C241-P11: quatro novas linhas NASA, não uma órbita terminal

**Pergunta falsificável (#15/#88):** entre os boletins de 15 e 30 de novembro
de 1963, o objeto 1963 3C apresenta maior diferença impressa de período
nodal e apogeu do que o 3A, sob hipótese de arredondamento? Uma extrapolação
linear das **datas de publicação** bate a persistência em um holdout de
30/11? **Resultado:** 3C apresenta maior queda documental; a extrapolação
vence em 3C, mas **perde para a persistência no apogeu do 3A**.

## Fontes diretamente inspecionadas e hashes dos PDFs

- **C241-L12#1:** NASA, Satellite Situation Report (SSR), 15/10/1963,
  vol. 3 nº 20, tabela OBJECTS IN ORBIT, p. impressa 5 (PDF p. 7);
  [PDF oficial](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf#page=7).
  Ledger anterior, SHA-256 fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2.
- **C241-L19#1:** NASA SSR, 15/11/1963, vol. 3 nº 22, p. impressa 5
  (PDF p. 7), [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=7).
  Fac-símile inspecionado visualmente. PDF oficial baixado integralmente em
  13/11/2026: 327.613 bytes, SHA-256
  0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674.
- **C241-L18 (NTRS 19640002493):** NASA SSR, 30/11/1963, vol. 3 nº 23, p. impressa 5
  (PDF p. 7), [NTRS 19640002493](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7).
  Fac-símile inspecionado visualmente. PDF baixado integralmente:
  1.266.393 bytes, SHA-256
  9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d.
- **C197#1 / C198#1:** o boletim de 15/11 registra 08/11 como dia de
  decaimento de 1963 3B. Não fornece hora ou posição terminal. O 3B não
  está entre as linhas de objetos em órbita usadas nas comparações de novembro.

Os dados são **publicações contemporâneas primárias**, não registros brutos
de sensor. As edições pertencem à **mesma cadeia institucional**
NASA/Goddard, NORAD e Smithsonian, sem independência instrumental demonstrada.

| Data do boletim | Objeto | Período (min) | Inclinação (°) | Apogeu (km) | Perigeu (km) |
|---|---|---:|---:|---:|---:|
| 15/11 | 1963 3A | 94,6 | 81,88 | 536 | 455 |
| 30/11 | 1963 3A | 94,6 | 81,88 | 533 | 459 |
| 15/11 | 1963 3C | 92,6 | 81,87 | 420 | 376 |
| 30/11 | 1963 3C | 92,2 | 81,86 | 390 | 368 |

Quatro linhas oferecem **16 campos publicados**, não 16 observações
instrumentais. A matriz moderna associa 3A a NORAD 527 e 3C a NORAD 529.
O grafo antigo ssr_1963_observable_graph.json contém **94,8 min** para
3A em 30/11; a leitura direta mostra **94,6 min**, em conformidade com a
correção anterior identificada pelo Gavião na PR #194. A nova série
rejeita explicitamente o valor incorreto, sem editar o grafo legado
grande e congelado pela política de 20 KB.

## Diferenças sob hipótese declarada de quantização

Assumindo, apenas condicionalmente, arredondamento ao último algarismo
exibido, tolerâncias para **diferenças** de duas edições são ±0,10 min,
±0,01° e ±1 km. Isso NÃO é sigma de medição orbital.

| Campo (15/11 menos 30/11) | 3A | 3C |
|---|---:|---:|
| Período nodal | −0,10 a +0,10 min | +0,30 a +0,50 min |
| Apogeu | +2 a +4 km | +29 a +31 km |
| Perigeu | −5 a −3 km | +7 a +9 km |
| Inclinação | −0,01 a +0,01° | 0,00 a +0,02° |

O Lean 4.35 formaliza **somente** o confronto quantitativo condicionado
pelas duas edições: a diferença documental do 3C excede a do 3A para
período e apogeu. A diferença de inclinação do 3C pode ser zero.

## Holdout temporal de publicação, com contraprova

Os parâmetros dos dois controles são **congelados em 15/10 e 15/11**.
A tabela de 30/11 não entra na calibração: comparar (a) persistência
do valor 15/11 e (b) prolongamento linear da diferença 15/10→15/11
pelos **15/31 dias entre as datas de edição**. São apenas operadores de
previsão de valores **impressos**, sem reivindicar épocas de medição.

| Objeto e variável | Erro absoluto persistência | Erro absoluto linear | Melhor |
|---|---:|---:|---|
| 3A, período | 0,000 min | 0,000 min | Empate |
| 3C, período | 0,400 min | 0,061 min | Linear |
| 3A, apogeu | **3,000 km** | 5,419 km | **Persistência** |
| 3C, apogeu | 30,000 km | **11,613 km** | Linear |

A perda no 3A falsifica a afirmação de que extrapolar é universalmente
superior. O conjunto de validação tem a mesma família documental de
treinamento e não mede precisão instrumental ou dinâmica gravitacional.

## Estado físico e reprodução

- **Antes/depois:** domínio físico de parâmetros Θ→Θ, **zero cenários
  excluídos**, não-vazio adicional não avaliado. Nenhum filtro físico
  novo é ativado em Lean ou Castor.
- **Faltam** fichas primárias de NORAD 527/528/529 com época UTC de
  observação, estação e geometria de sensor, referencial, definição
  histórica exata do período/apogeu, covariâncias e transformação até o
  catálogo. Erro externo instrumental e propagação terminal **NOT_RUN**.
- **Edição nº 21** próxima do decaimento do 3B: **NOT_RECOVERED**. Obter
  essa tabela poderá acrescentar um registro documental mais próximo.
- Arquivos rastreáveis: ledger C241-L19 em
  [nasa_ssr_nov15_1963_C241-L19.json](../tle_custody/nasa_ssr_nov15_1963_C241-L19.json), mais o ledger C241-L18 da Tartaruga (30/11),
  saída [C241-P11](C241-P11_november_historical_printings.json),
  gerador formal/scripts/compile_ssr_november.py, Lean
  formal/Conde1963/SsrNovember.lean e testes adversariais.

Reprodução: executar o gerador com --check, o unittest
formal/tests/test_ssr_november.py, lake build e a auditoria de axiomas
CoreAxioms.lean. O gerador rejeita mutações dos campos, hashes, páginas,
IDs e alegações de sensor/época fictícios; verifica o HEAD pelo CI.
