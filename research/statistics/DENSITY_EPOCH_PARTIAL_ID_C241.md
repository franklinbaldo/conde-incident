---
type: Experiment
title: "C241-P30: identificabilidade parcial sob heterogeneidade atmosférica"
description: "Limites exatos de altura de escala quando a densidade espacial difere entre 527 e 529, sem importar hipóteses como observações."
experiment_id: C241-P30
model_ref: tools/density_epoch_partial_id.py
inputs_ref: research/constraints/C241-P29_density_epoch_contrast.json
verification_status: SYNTHETIC_CONDITIONAL_TEST
---

# C241-P30. Quanto da identificação sobrevive se a atmosfera não for comum?

O [desenho C241-P29](DENSITY_EPOCH_CONTRAST_C241.md) cancela o fator atmosférico compartilhado por época nas quatro observações ideais dos objetos 527/529. Mas os objetos podem atravessar regiões atmosféricas diferentes. **Uma igualdade de fatores q entre eles não é uma medida atmosférica.** Esta etapa substitui essa igualdade por limites explícitos, não estimados.

Em unidades adimensionais logarítmicas, considere z_{jt} = alpha + b_j + q_t - (h_{jt}-h0) gamma + eta_{jt} + e_{jt}, com gamma=1/H em km^-1. Para cada época t, a diferença espacial de densidade d_t = eta_{527,t}-eta_{529,t} é **desconhecida**, mas poderia ser limitada por uma calibração física independente, |d_t| <= kappa_t. Com erro de contraste combinado |e| <= E e Δh = (h527,1-h529,1)-(h527,0-h529,0), o contraste observado C satisfaria:

    |C + Δh gamma| <= kappa_0 + kappa_1 + E.

Intersectar essa banda com gamma >= 0 fornece um **conjunto identificado parcialmente**, não uma distribuição posterior. O fator temporal q_t e os coeficientes b_j desaparecem do contraste, mas as diferenças espaciais d_t **não** desaparecem. A covariância e os erros do operador físico precisam estar incluídos em E: quatro sensores não são automaticamente independentes.

## Resultados com números exclusivamente sintéticos

O mesmo desenho contrafactual do P29 usa Δh=30 km e contraste C=-0,6 (não observado em 1963), com gamma de referência 1/50 km^-1.

| Premissa sobre fatores espaciais e erro | Gamma admissível (km^-1) | H (km) |
| --- | --- | --- |
| kappa0=kappa1=E=0 | exatamente 1/50 | 50 |
| kappa0=kappa1=0,1; E=0,05 | [7/600,17/600] | [600/17,600/7] |
| kappa0=kappa1=0,3; E=0 | [0,1/25] | [25,+infinito] |
| Sem limite de heterogeneidade | todo gamma >= 0 | não limitado |

O modelo exato permite uma falsa certeza pontual. Mesmo desvios de 0,1 em log-densidade por época, **supostos e não medidos**, transformam a solução em intervalo. Se C tem sinal incompatível com gamma>=0 e E=0, o operador deve ser **rejeitado**, não forçado a ajustar uma órbita.

O comprimento da banda de gamma antes da interseção física é 2(kappa0+kappa1+E)/|Δh|. Um Δh grande ajuda apenas se diferenças espaciais, épocas, erro de estado/arrasto e seleção dos pares forem calibrados. Sem limite finito nas diferenças espaciais, mais precisão numérica do contraste não identifica H.

## Observação que discriminaria e guarda de fonte

Exigir **duas épocas instrumentais reais**, com 527 e 529 rastreados e ligados a altitude, velocidade relativa e arrasto isolado, e limite externo da diferença de densidade em cada par (altitude, latitude, longitude, hora). O controle meteorológico comum precisa ser demonstrado para aqueles locais, não assumido porque os registros dividem uma data editorial. O quarto dado integra o contraste; um holdout futuro deve ser independente e pré-separado.

O [manifesto C241-P30](../constraints/C241-P30_density_epoch_partial_id.json) é derivado do [manifesto C241-P29](../constraints/C241-P29_density_epoch_contrast.json) com SHA-256 dos bytes locais. Reproduzir:

    python3 tools/density_epoch_partial_id.py --check
    python3 -m unittest discover -s tests -p test_density_epoch_partial_id.py -v

**Estado:** constrangimento histórico inativo; MCMC histórico NOT_RUN; redução de domínio do 528 NOT_EVALUABLE. Nenhuma medida nova de densidade ou aceleração foi recuperada; B528 continua livre sem observação instrumental própria. Não inferir posição ou hora de reentrada em Conde. Dependências: [Castor #4](https://github.com/franklinbaldo/conde-incident/issues/4), [Tartaruga #396](https://github.com/franklinbaldo/conde-incident/issues/396).
