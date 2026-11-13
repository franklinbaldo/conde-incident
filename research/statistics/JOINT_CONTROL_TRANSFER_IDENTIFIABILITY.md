---
type: Guide
title: '🦌 Cervo: limites da transferência de controles 527/529 para o 528'
description: 'Contraprova racional de identificabilidade entre corpos, sem dados históricos nem inferência geográfica.'
---

# 🦌 Cervo: controles 527/529 não identificam automaticamente a trajetória do 528

**Contexto documental:** [issue #396](https://github.com/franklinbaldo/conde-incident/issues/396), que solicita mais observações instrumentais de 527/529 posteriores a 08/11/1963 e medidas primárias dos três objetos; C241-L18 e C241-P10. **Nenhuma medida foi lida ou adicionada por esta demonstração.** O resultado é uma contraprova algébrica condicional, não uma estimativa orbital.

## Questão de identificação

É possível que um parâmetro dinâmico seja compartilhado entre três corpos, mas que cada corpo também tenha parâmetros próprios desconhecidos (estado inicial, arrasto, coeficiente balístico, etc.). Observações mais tardias dos dois controles não revelam automaticamente os parâmetros particulares do corpo ausente. Para tornar essa limitação testável, usamos deliberadamente um **modelo escalar de brinquedo**, sem a cinemática RAAN nem um propagador espacial:

\[ y_j(t)=a_j+v_j t+\tfrac12(g+b_j)t^2,\quad j\in\{527,528,529\}. \]

Aqui `g` é uma curvatura comum, `b_j` é uma curvatura própria e `a_j,v_j` são próprios. As épocas racionais `0,1,2,3` são **instantes artificiais adimensionais**, sem relação com datas, unidades, velocidades ou sensores de 1963. As linhas são funcionais exatos de dez parâmetros; seu posto é calculado sem arredondamento. Uma previsão é *estimável* somente quando sua linha pertence ao espaço de linhas do conjunto de treino. Isso é apenas um requisito algébrico; não demonstra predição calibrada no mundo físico.

| Cenário ilustrativo | Posto / 10 | Previsão do 528 no tempo 3 estimável? |
|---|---:|---|
| Controles 527 e 529 nos tempos 0, 1, 2; 528 nos tempos 0, 1 | 8/10 | Não |
| Mais observações dos **controles** no tempo 3 | 8/10 | Não |
| Terceira observação do **528** no tempo 2, antes do holdout | 9/10 | Sim, no modelo assumido |
| Uma curvatura própria de controle calibrada externamente | 9/10 | Não |
| Curvaturas comum e própria do 528 calibradas externamente | 10/10 | Sim, no modelo assumido |

Duas contraprovas exatas explicam a tabela. A transformação `g → g + 1`, `b_j → b_j − 1` para os três objetos preserva *todas* as observações e previsões: `g` não é identificável isoladamente sem informação externa. Já `v_528 → v_528 − 1/2` e `b_528 → b_528 + 1` preserva as observações do 528 nos tempos 0 e 1 **e qualquer quantidade de observações dos controles**, mas altera a previsão do 528 no tempo 3 em exatamente três unidades artificiais. São dois mecanismos diferentes de não identificação.

## Próximo dado discriminante

Priorizar registros primários instrumentais identificados como 528 em épocas distintas **anteriores ao holdout**, com observável, frame, época, erro, seleção, custódia e independência justificáveis. Em paralelo, observações tardias de 527/529 são valiosas para avaliar e falsificar uma hipótese de **dinâmica realmente compartilhada**, desde que suas diferenças físicas (balística, atitude, arrasto, atmosfera) sejam modeladas e calibradas. Uma aproximação ou igualdade entre coeficientes individuais deve ser identificada como **hipótese**, jamais disfarçada de resultado dos dados.

Não transferir a linha de 529 para o 528, não tratar a data catalogada como hora terminal, não usar dados do holdout para ajustar o modelo e não computar probabilidades de impacto com pressupostos inventados. O caso histórico continua com `active_constraint=false`, `historical_mcmc=NOT_RUN` e `geographic_exclusion=NOT_AUTHORIZED`. A demonstração não afirma que os parâmetros reais são não identificáveis sob **qualquer** modelo físico: prova apenas que o compartilhamento parcial de parâmetros não basta em geral.

Reprodução (sem rede nem dependências externas): `python3 tools/joint_control_transfer_identifiability.py --check` e `python3 -m unittest discover -s tests -p 'test_joint_control_transfer_identifiability.py' -v`. O JSON vizinho é um certificado determinístico e o CI de integração executa o teste adversarial.
