---
type: Guide
title: '🦌 Cervo: relógio compartilhado e observabilidade óptica condicional'
description: 'Auditoria por posto racional do viés temporal comum com estações fixas ou trajetória conhecida.'
---

# C241-P16: três ângulos podem identificar seis estados e não o relógio

Fatia [#503](https://github.com/franklinbaldo/conde-incident/issues/503). Continuação do diagnóstico de paralaxe [C241-P14](https://github.com/franklinbaldo/conde-incident/pull/463) e de observabilidade temporal [C241-P15](https://github.com/franklinbaldo/conde-incident/pull/486). **É um experimento sintético, não observações de 1963.** A pergunta é se o suposto posto 6/6 de três medidas ópticas continua suficiente quando a época instrumental compartilha um deslocamento desconhecido.

## Contrato do operador local

Admitimos, *apenas como desenho contrafactual*, posição alvo `r(t)=r0+v*t`, estação `s_i(t)=s_i0+w_i*t` em quadro cartesiano inercial comum e tempo real `t=t_reportado+δ`. Os sete parâmetros são as três posições iniciais, três velocidades e o deslocamento **comum** do relógio `δ`. Para cada direção `u_i` o projetor tangente `P_i=I-u_i*u_iᵀ/(u_iᵀu_i)` produz o jacobiano local (à parte fator não nulo de alcance) `[P_i, t_i P_i, P_i(v-w_i)]`. Postos são racionais exatos, sem erro de medição ou inferência bayesiana.

| Desenho sintético | Posto / 7 | Relógio identificado localmente? |
| --- | ---: | --- |
| Três ângulos ortogonais, observadores fixos | 6/7 | Não |
| Quatro ângulos, observadores fixos | 6/7 | Não |
| Quatro ângulos, velocidade transversal de uma estação conhecida | 7/7 | Sim, somente no operador assumido |
| Quatro ângulos, velocidade dessa estação paralela à visada | 6/7 | Não |

Direções artificiais `x,y,z,(1,1,1)` nas épocas 0,1,2,3, com `v=(2,-1,3)` e, no terceiro desenho, `w_4=(1,0,0)`; as velocidades de outras estações são nulas. Os números não representam sensores, órbitas, Terra, Conde ou velocidades de 1963. Há estações sintéticas compatíveis com todas as direções escolhidas, porque a posição inicial de cada estação pode ser definida a partir de um alcance positivo arbitrário.

## Simetria exata e condição discriminante

Com observadores estacionários e relógio comum, a transformação `δ→δ+ε`, `r0→r0−vε`, `v→v` preserva **cada direção prevista**, para qualquer ε. Não é mera insuficiência de otimização: o relógio e a posição no marco temporal absoluto não são separáveis pelos ângulos, mesmo com mais medidas. O posto 6/7 pode identificar v no operador sintético, mas a posição de referência permanece ambígua na direção de v.

Uma trajetória de estação conhecida em **tempo absoluto** pode quebrar localmente essa simetria se sua velocidade transversal às visadas oferecer informação independente. Um movimento exclusivamente ao longo da visada não basta. Posto completo é **local**: não prova unicidade global, condicionamento, qualidade do relógio ou propagação orbital. Se a própria trajetória da estação não estiver calibrada no relógio externo, a conclusão 7/7 não se aplica. Relógios individuais das estações, erros de orientação, rotação da Terra, referencial e dinâmica real exigiriam novas colunas e validações.

## Encadeamento e próximo dado

`C241-P14 (paralaxe)` → `C241-P15 (épocas distintas)` → `C241-P16 (viés de tempo compartilhado)`; variáveis novas `δ` e `w_i`, ligação ao operador angular e exigência de efemérides das estações calibradas em tempo absoluto. Estado da restrição histórica: **CONNECTED_PENDING_CALIBRATION**, domínio orbital **NOT_EVALUABLE**. Recuperar na [Tartaruga #396](https://github.com/franklinbaldo/conde-incident/issues/396) horários observacionais, identificação de estação, bases de tempo, erro de sincronização, referenciais e efemérides com proveniência primária antes de avaliar 527/528/529. Não extrapolar ao local de queda ou sobrevoo; MCMC histórico **NOT_RUN**.

Reproduzir: `python3 tools/optical_clock_bias_observability.py` e `python3 -m unittest discover -s tests -p 'test_optical_clock_bias_observability.py'`.
