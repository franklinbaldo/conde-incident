---
type: Experiment
title: "C241-P29: contraste entre épocas contra densidade atmosférica desconhecida"
description: "Condições algébricas para identificar uma altura de escala com fatores atmosféricos temporais livres, sem observações históricas de arrasto."
experiment_id: C241-P29
model_ref: tools/density_epoch_contrast.py
inputs_ref: research/constraints/baker_nunn_ru301_1963_film_index.json
verification_status: SYNTHETIC_CONDITIONAL_TEST
---

# C241-P29. Um fator atmosférico desconhecido por época invalida o desenho anterior?

**Pergunta falsificável.** O resultado C241-P28 exige conhecer a variação temporal da densidade ao comparar duas altitudes de um mesmo satélite em datas diferentes. Se essa variação for desconhecida, qual desenho ainda distingue a forma vertical da atmosfera?

## Contrato e resultado exato

No operador de arrasto usado em C241-P27/P28, suponha densidade igual a A vezes rho0 vezes q_t vezes exp(-(h-h0)/H), com B_j=Cd*Area/m constante para cada objeto. Após isolar a **aceleração de arrasto** de outros efeitos e normalizar pelo quadrado da velocidade relativa, o observável idealizado é:

\[
z_{jt}=\log A+\log B_j+\log q_t-(h_{jt}-h_0)\gamma,\qquad \gamma=1/H.
\]

Não pressupomos que os fatores q nas duas épocas sejam iguais: cada época tem um multiplicador positivo arbitrário, mas **comum aos dois objetos**. Se os controles 527 e 529 fossem observados em ambas as épocas, o contraste cruzado eliminaria A, ambos os B e os dois fatores q:

\[
D=(z_{527,1}-z_{529,1})-(z_{527,0}-z_{529,0})
=-\gamma[(h_{527,1}-h_{529,1})-(h_{527,0}-h_{529,0})].
\]

Uma **mudança não nula na diferença relativa de altitude** identifica gamma no modelo idealizado, mesmo sem calibrar os multiplicadores q por época. Não identifica separadamente A, B_527 e B_529, nem qualquer parâmetro próprio do 528. Se a atmosfera tiver multiplicadores distintos por objeto/época, ou B_j variar livremente, o contraste já não identifica gamma.

| Desenho inteiramente sintético | Posto de fatores incômodos | Posto com gamma |
| --- | ---: | ---: |
| Quatro células, diferença relativa entre altitudes muda 30 km | 3 | 4 |
| Só três das quatro células | 3 | 3 |
| Quatro células, diferença relativa de altitudes constante | 3 | 3 |
| Quatro células, fator q livre por objeto/época | 4 | 4 |

As altitudes 480/520 km na época 0 e 500/510 km na época 1 são **contrafactuais**, não altitudes observadas em 1963. O contraste tem coeficiente exato -30 km em gamma, e seu condicionamento piora quando a variação relativa de altitude se aproxima de zero.

O erro permanece **condicional**: se cada valor de z possuir erro absoluto no máximo e, o erro absoluto de D fica no máximo 4e, e o erro de gamma na reconstrução simples no máximo 4e/|delta_h|. Se covariâncias forem documentadas, o erro de D deverá usar cᵀΣc, não quatro leituras automaticamente independentes. Nenhum valor histórico foi atribuído a e ou Σ.

## Holdout e exigência instrumental

A quarta célula fornece a primeira equação que identifica gamma após as três primeiras. Ela **não pode simultaneamente funcionar como holdout externo de validação**. Seria necessário reservar outra observação, com desenho congelado antes da análise, depois de calibrar operador e erros. O posto exato do modelo não é posto de um rastreamento angular histórico.

Inventário documental cruzado: o [índice Smithsonian RU301](../constraints/baker_nunn_ru301_1963_film_index.json) contém 15 identificadores de filmes de 1–5/11/1963. Não atribui nenhum ao 528 nem apresenta ângulos calibrados ou acelerações isoladas. O script fixa o SHA-256 **do JSON local**, não do PDF externo. A [fonte institucional](https://sirismm.si.edu/EADpdfs/SIA.FARU0301.pdf) descreve acervo selecionado: não é censo de rastreamento, não é série negativa e não equivale a 15 medições.

Reproduzir com os comandos abaixo, em Python 3:

    python3 tools/density_epoch_contrast.py --check
    python3 -m unittest discover -s tests -p test_density_epoch_contrast.py -v

Os postos usam frações exatas, sem limiar SVD. O [relatório C241-P29](../constraints/C241-P29_density_epoch_contrast.json) registra a fonte, o desenho e os controles negativos.

**Estado científico:** restrição física inativa, MCMC histórico não executado, domínio geográfico de reentrada não avaliável. Nenhuma evidência nova de hora ou lugar de queda do 528 em Conde. Prioridade: recuperar observações reais com épocas, estados, separação entre J2 e arrasto, erro e independência; avaliar se um fator atmosférico comum é válido. Relacionadas: [Castor #4](https://github.com/franklinbaldo/conde-incident/issues/4), [Tartaruga #396](https://github.com/franklinbaldo/conde-incident/issues/396).
