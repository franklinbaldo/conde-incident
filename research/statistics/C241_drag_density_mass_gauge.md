---
type: Guide
title: 'C241: o gauge massa, área e densidade no arrasto orbital'
description: 'Diagnóstico de posto exato e holdouts hipotéticos; não atribui massa a NORAD 528.'
---

# C241: arrasto de três objetos não identifica automaticamente a massa do 528

**Questão para as drafts [#634](https://github.com/franklinbaldo/conde-incident/pull/634) e [#641](https://github.com/franklinbaldo/conde-incident/pull/641):** três objetos e mais épocas de decaimento, sozinhos, resolveriam a massa específica do 528? Não, se densidade e área aerodinâmica não forem calibradas. Este teste é exclusivamente um **desenho estrutural contrafactual**, não uma estimação orbital de 1963.

A fonte de custódia [C241-L40](../tle_custody/gcat_mass_semantics_C241-L40.json) registra Mass=306 kg e TotMass=1176 kg associados ao 527, mas **não** uma massa instrumental do 528, nem um inventário fechado. O auditor exige que esse veto permaneça verdadeiro.

## Modelo simplificado e posto exato

Para três objetos hipotéticos em duas épocas, com operador dinâmico e fatores de velocidade conhecidos, escrevemos um proxy positivo e calibrado de arrasto por

z(i,t) = -q(i) + g(i) + s(t),

onde q=ln(m/m0), g=ln(Cd·A/(Cd·A)0) e s=ln(rho/rho0). As referências positivas são fixas e conhecidas. A variável z é um log-proxy adimensional hipotético, **não B* de TLE**. Assumimos artificialmente a mesma densidade efetiva s(t) para os três objetos em cada época, condição que não segue da genealogia orbital real. As oito coordenadas são (q527,q528,q529,g527,g528,g529,s0,s1).

As seis linhas de observação (3 objetos × 2 épocas) têm **posto racional exato 4/8** e nulidade 4. Duas simetrias independentes deixam cada observável inalterado: alterar simultaneamente q528 e g528, e alterar todas as massas juntamente com o nível comum de densidade. Ambas mudam a massa do 528. Duplicar uma mesma observação ou chamar uma cópia de outro sensor não aumenta o posto, ainda que medições realmente independentes possam melhorar a precisão sob um modelo de erro adequado.

| Canais **hipotéticos** disponíveis | Posto / nulidade | q528 estimável? |
| --- | --- | --- |
| Seis proxies de arrasto apenas | 4/4 | Não |
| Arrasto + densidade absoluta calibrada em e0 | 5/3 | Não |
| Arrasto + Cd·A do 528 calibrado | 5/3 | Não |
| Arrasto + densidade em e0 + Cd·A do 528 | 6/2 | Sim, condicionalmente |
| Arrasto + massa e Cd·A do 527 calibrados | 6/2 | Não |
| Arrasto + massa e Cd·A do 527 + Cd·A do 528 | 7/1 | Sim, condicionalmente |

O posto é propriedade das equações idealizadas, **não** prova de que os canais existiram em 1963. Nem mesmo o caso 7/8 valida a transferência de densidade entre órbitas: necessita co-localização, modelo de transporte e dinâmica calibrados.

## Holdout discriminante

Usando apenas os três proxies na época e0, o proxy do 528 em e1 **não** está no espaço de linhas do treinamento, pois o nível atmosférico e1 é livre. Acrescentar um único proxy da época e1 para o 527 **ou 529** permite predizer o proxy relativo do 528 em e1, *somente* sob o mesmo nível atmosférico para ambos. Isso **não identifica a massa do 528**. Essa diferença entre estimabilidade preditiva de um observável e estimabilidade de um parâmetro impede que uma validação bem-sucedida de arrasto seja promovida indevidamente a posterior de massa.

**Aquisição discriminante preferencial:** observação de arrasto individual do 528 com geometria/atitude e Cd independentes, mais densidade efetiva calibrada na mesma época, ou um controle coetâneo com massa/geometria conhecida e transporte atmosférico validado. Exigir instrumento, UTC, quadro, seleção, incertezas não nulas, proveniência binária e independência antes de alimentar uma verossimilhança.

Limites: sem medição nova de 528, nenhum estado ou densidade histórica reconstruída, nenhuma covariância ou prior calibrada; posto local em log não resolve ambiguidades globais. historical_mcmc=NOT_RUN, historical_constraint_active=false, posterior e probabilidade de impacto nulas, sem estreitamento geográfico de Conde.

Reproduzir: python3 -m unittest discover -s tests -p test_drag_density_mass_gauge_C241.py -v e python3 -m tools.drag_density_mass_gauge_C241.
