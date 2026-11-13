---
type: Guide
title: '🦌 Cervo: paralaxe assíncrona e identificação condicional'
description: 'Certificado exato de posto para observações ópticas sintéticas com velocidade desconhecida.'
---

# C241-P15: duas direções em épocas distintas não triangulam uma órbita

Continuação da geometria simultânea C241-P14 ([PR #463](https://github.com/franklinbaldo/conde-incident/pull/463)), na [issue #482](https://github.com/franklinbaldo/conde-incident/issues/482). Duas linhas de visada não paralelas identificam posição localmente *quando simultâneas*, não automaticamente quando possuem épocas distintas. Não se dispõe nesta análise de ângulos instrumentais autenticados de 527, 528 ou 529.

## Contraprova por aritmética exata

Apenas para desenho experimental, suponha movimento afim cartesiano r(t)=r0+v t, com seis incógnitas (posição/velocidade). Uma direção não nula d_i na época t_i gera o mesmo espaço de linhas de jacobiano que P_i [I, t_i I], em que P_i=I-d_i d_iᵀ/(d_iᵀd_i). Cada registro fornece até duas restrições tangentes. O utilitário calcula os postos sobre frações racionais, sem parâmetros históricos ou tolerâncias.

| Desenho inteiramente sintético | Posto / 6 | Dimensão não identificada |
| --- | ---: | ---: |
| Um ângulo | 2 | 4 |
| Duas visadas simultâneas não paralelas | 3 | 3 (velocidade) |
| Duas visadas não paralelas em épocas diferentes | 4 | 2 |
| Três visadas ortogonais em três épocas | 6 | 0 no modelo afim |
| Três visadas colineares em três épocas | 4 | 2 |
| Duas simultâneas e uma posterior | 5 | 1 |
| Dois pares estereoscópicos em duas épocas | 6 | 0 no modelo afim |

Existe uma família contínua de estados, além da nulidade local. Em épocas fictícias 0 e 1, estações s0=(0,0,0), s1=(10,0,0), direções u0=(0,1,0), u1=(0,0,1), escolha quaisquer alcances positivos R0 e R1. Então r0=s0+R0 u0 e v=s1+R1 u1-r0 reproduzem as mesmas duas direções. As escolhas (R0,R1)=(100,100) e (200,300) fornecem posições e velocidades diferentes com ângulos iguais. Nenhuma dessas coordenadas representa Conde ou qualquer satélite real.

## Interpretação e próxima observação

As épocas devem representar *medição*, não a data editorial dos relatórios NASA. Um terceiro ângulo pode identificar os seis parâmetros somente sob o operador afim assumido, com quadro comum e direções suficientemente independentes. Uma órbita verdadeira não segue movimento retilíneo constante no intervalo considerado. Posto exato completo tampouco demonstra boa condição numérica, calibração, identidade do objeto ou taxa de erro. Não foram inventados relógio, sensor, covariância, propagador, priors nem probabilidades.

Procurar observações originais do **mesmo objeto** em três épocas discriminantes ou dois pares estereoscópicos temporalmente distintos, com tempos UTC e erros documentados, posições de estações, referencial, dependência documental, seleção do sensor e modelo físico validado. Controles 527/529 não identificam automaticamente os parâmetros particulares do 528. Busca instrumental: [Tartaruga #396](https://github.com/franklinbaldo/conde-incident/issues/396).

Conexão cumulativa C241-P14 → C241-P15: CONNECTED_PENDING_CALIBRATION. Não há restrição física ativada nem redução avaliável do domínio orbital histórico. MCMC histórico NOT_RUN; impacto ou sobrevoo em Conde NOT_SUPPORTED.

Reproduzir com Python padrão: executar tools/optical_temporal_observability.py e unittest discover com padrão test_optical_temporal_observability.py.
