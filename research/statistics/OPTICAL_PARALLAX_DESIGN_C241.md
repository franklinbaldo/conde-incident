---
type: Guide
title: '🦌 Cervo: identificabilidade de distância em holdouts ópticos condicionais'
description: 'Critério geométrico de parallax para escolher estações, sem simular observações de 1963.'
---

# C241-P14: duas estações não são automaticamente duas dimensões novas

A PR #457 introduziu `src/lib/orbitOpticalHoldout.ts`, um operador angular **condicional** para os controles NORAD 527 e 529. Seu contrato exige posições de satélite e estação no **mesmo referencial inercial e época UTC**, mas o arquivo de custódia `research/constraints/CASTOR-G36_optical_holdout_geometry.json` confirma que ainda não há observações ópticas instrumentais autenticadas para esses dois objetos. O catálogo e os relatórios NASA SSR não fornecem ângulos observados. Esta análise é uma regra para desenhar a busca por fontes úteis, não uma nova medição.

Uma direção observada por uma estação `s` até um ponto espacial hipotético `r` é `u=(r-s)/||r-s||`. O jacobiano da direção com relação à posição é `J=(I-uuᵀ)/ρ`, onde `ρ=||r-s||`. Tem posto **2**, com `J u=0`: a posição ao longo da linha de visada não é identificada por uma única direção no mesmo instante, mesmo com resolução angular infinitamente boa.

Para duas estações na **mesma época**, seja `a=1/ρ₁²`, `b=1/ρ₂²` e `θ` o ângulo entre as direções. Os autovalores da matriz de informação **geométrica, sem covariância instrumental** `J₁ᵀJ₁+J₂ᵀJ₂` são `a+b` e `(a+b ± sqrt((a-b)²+4ab cos²θ))/2`. Assim, duas direções não paralelas têm posto 3 localmente; em estações e alvo colineares, o posto continua 2. Quando `θ` é pequeno, o menor autovalor aproxima zero e a recuperação de distância fica mal condicionada. O cálculo numérico avalia o menor autovalor por `ab sin²θ / λ₊`, evitando cancelamento catastrófico.

**Regra de aquisição:** localizar, para um **mesmo NORAD 527 ou 529**, pares de registros originais com horários coincidentes (incluindo precisão temporal documentada), localizações de estações, frames/equinócios, calibrações, identificadores de filme e proveniência independente. Comparar bases efetivas transversais à linha de visada; meramente duas estações de nomes distintos não bastam. Diferentes épocas exigem um operador físico validado e não podem ser trianguladas como se fossem simultâneas. Controlos 527/529 não identificam automaticamente parâmetros próprios do 528 (PR #403).

O índice de condicionamento geométrico é **descritivo**: nenhum limiar de detectabilidade ou precisão angular de 1963 foi atribuído. Uma matriz geométrica de posto 3 não equivale a inferência calibrada, MCMC histórico, trajetória terminal ou prova de passagem/queda em Conde. Para converter esta regra em um holdout, faltam observações primárias, épocas, transformações de referencial, erros e covariância, dinâmica, seleção do sensor e pré-registro do ajuste. `historical_mcmc=NOT_RUN`; `impact_inference=NOT_SUPPORTED`.

Reprodução, com vetores hipotéticos explicitamente fornecidos pelo pesquisador, não com TLEs/SSR transformados em observações:

```bash
python3 -m unittest discover -s tests -p 'test_optical_parallax_identifiability.py' -v
python3 tools/optical_parallax_identifiability.py --input arquivo-com-vetores-condicionais.json
```

Dependências científicas: [Castor PR #457](https://github.com/franklinbaldo/conde-incident/pull/457), [Cervo PR #403](https://github.com/franklinbaldo/conde-incident/pull/403), [Tartaruga #396](https://github.com/franklinbaldo/conde-incident/issues/396). Não houve recuperação de medida instrumental nesta fatia; o estado das evidências permanece `CONNECTED_PENDING_CALIBRATION`.
