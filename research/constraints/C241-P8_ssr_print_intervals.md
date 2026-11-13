---
type: Guide
title: "C241-P8: limites condicionais de arredondamento nas tabelas NASA de abril e outubro de 1963"
description: "Intervalos rastreáveis de períodos nodais publicados com contraexemplo de 3A, sem promoção a medida instrumental."
---

# C241-P8 — O que não é explicável só por uma casa decimal

**Pergunta pré-declarada:** os períodos nodais impressos nas edições NASA/Goddard *Satellite Situation Report* de 30/04/1963 e 15/10/1963 diferem mais do que a perda de resolução por exibir uma casa decimal? Trata-se de comparação **documental**; publicação não é época de sensor. Nenhum período verdadeiro é identificado.

## Duas ocorrências, uma linhagem institucional

- **C241-L16**, NASA SSR 30/04/1963, nº 9, tabela *Objects in Orbit*, página impressa 5/PDF índice 6, [fonte oficial](https://ntrs.nasa.gov/api/citations/19630012128/downloads/19630012128.pdf), SHA-256 dos bytes inspecionados `87b8c1be1d074dff4b605b422f6a8836c2ebdf80ca4ac0568373b168cc457a38`.
- **C241-L12**, NASA SSR 15/10/1963, nº 20, mesma tabela, página impressa 5/PDF índice 6, [fonte oficial](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf), SHA-256 da variante validada `fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2`. Há outra variante servida pelo mesmo URL; não se trata de uma nova medição.

Os designadores impressos 1963 3A, 3B e 3C não contêm os NORAD IDs na própria tabela. Sua correlação moderna com 527/528/529 depende de outra fonte. Ambas as publicações integram a mesma linhagem NASA compilada, não duas medições independentes de radar.

## Operador e resultado falsificável

**Hipótese condicional adicional H:** um período apresentado com uma casa decimal foi arredondado ao **décimo de minuto mais próximo**. O procedimento editorial não está confirmado, portanto H não é instrumentação calibrada. Nesse modelo, cada valor real que foi arredondado para a impressão deve pertencer a `[impresso - 0,05; impresso + 0,05]` minuto. O arquivo Lean representa os valores em uma grade discreta de **0,01 minuto**, e prova, para **qualquer** par de valores nessa faixa, os limites de `abril - outubro`. A escolha das extremidades inclusivas torna a desigualdade conservadora em caso de empate no arredondamento.

| Designador | Abril (min) | Outubro (min) | Intervalo condicional abril − outubro (min) | Mudança maior que erro de arredondamento? |
| --- | ---: | ---: | ---: | --- |
| 1963 3A | 94,6 | 94,6 | −0,10 a +0,10 | Não demonstrável |
| 1963 3B | 94,1 | 92,4 | +1,60 a +1,80 | **Sim, condicional a H** |
| 1963 3C | 94,3 | 93,3 | +0,90 a +1,10 | **Sim, condicional a H** |

Também são mantidos os deltas **impressos** de apogeu (−6/−104/−73 km) e perigeu (+2/−59/−29 km) para 3A/3B/3C. São valores de tabelas, não taxa temporal nem perfis físicos calibrados. O controle 3A não apresenta diferença de período acima da resolução, o que impede afirmar um padrão universal de redução de período para os três objetos.

## Integração cumulativa e fronteira epistemológica

As entradas são variáveis documentais conectadas à matriz por C241-L16/C241-L12, exportadas em [C241-P8 JSON](C241-P8_ssr_print_intervals.json). São restrições condicionais **do valor impresso**, não restrições do estado orbital verdadeiro. Falta observar a época efetiva de cada solução, convenção de período nodal, sensores, covariâncias e método de arredondamento editorial. A NASA publicou tabelas em datas diferentes, mas isso não identifica quando os elementos foram ajustados. Consequentemente, o domínio físico Θ de 528/527/529 permanece inalterado; nenhuma janela de passagem, horário terminal, cratera ou conclusão sobre Conde é inferida.

**Reprodução:** `python3 formal/scripts/compile_ssr_print_intervals.py --check` e `python3 -m unittest discover -s formal/tests -p test_ssr_print_intervals.py -v`; compilar em `formal/` com `lake build`. O compilador verifica o ledger original já auditado, impede uma troca de designador/período/época e gera três teoremas quantificados, não provas de autenticidade histórica. Mutação adversarial de cada um dos seis períodos impressos e de dados físicos inventados faz o teste falhar.
