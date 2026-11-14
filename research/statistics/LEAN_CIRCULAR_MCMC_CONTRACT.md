---
type: Guide
title: "MCMC circular: propriedades Lean certificadas e limites históricos"
description: "Equilíbrio detalhado MH e simetria de fase por linhagem, com aritmética exata; sem posterior de Conde"
---

# Ponte Lean para a MCMC circular sintética

**Estado: STRUCTURAL_LEAN_CERTIFIED; SYNTHETIC_ONLY; NO_HISTORICAL_POSTERIOR; NO_CONDE_SITE_PROBABILITY.**
Escopo: métodos da 🦌 Cervo das issues #191 e #219, não observações novas dos
objetos NORAD 527, 528 ou 529. O Polvo formaliza em
[`CircularMCMC.lean`](../../formal/Conde1963/CircularMCMC.lean) duas
propriedades **condicionais** do experimento. A ponte de variáveis já existente
[`raan_phase_mcmc_candidate_C241.json`](../constraints/raan_phase_mcmc_candidate_C241.json)
continua `CONNECTED_PENDING_HISTORICAL_IDENTIFICATION`, com
`active_constraint=false` e `historical_posterior=null`. Sem alteração de Θ.

## 1. Reversibilidade da parte aceita de Metropolis-Hastings

O código `tools/raan_synthetic_phase_mcmc.py` usa quatro cadeias MH no círculo,
com proposta `q(θ'|θ)` em mistura de distribuição uniforme global e normal
enrolada de deslocamento central. **Sob parâmetros fixos e proposta simétrica**,
a razão Hastings se cancela. Para pesos-alvo positivos `w_i`, a probabilidade
de aceitação ideal é `min(1,w_j/w_i)`. Logo, o fluxo não normalizado dos
movimentos aceitos de `i` para `j` é

`w_i q(i,j) min(1,w_j/w_i) = q(i,j) min(w_i,w_j)`.

O Lean implementa a identidade de fluxo **em contagens naturais exatas**
(`acceptedFlow`), com `q` também representado por contagem inteira, e prova:

- `acceptedFlow_detailed_balance`: para todo par de estados e `q(i,j)=q(j,i)`, os fluxos aceitos são idênticos nos dois sentidos;
- `acceptedFlow_list_balance`: o total de fluxos aceitos de saída e entrada coincide em qualquer lista finita de estados;
- `asymmetric_proposal_counterexample`: a conclusão **falha** para um `q` não simétrico, prevenindo a generalização para propostas sem correção Hastings.

O resultado prova reversibilidade do **fluxo abstrato de movimentos aceitos**.
**Não prova** que `random.Random`, amostragem normal de ponto flutuante,
rejeição/autolaço, implementação numérica da taxa MH, cadeias de comprimento
finito ou diagnóstico de convergência correspondam exatamente a esse modelo.
Tampouco prova estacionariedade de um kernel normalizado completo. A ponte
entre a fórmula e o código é testada independentemente com aritmética racional
exata de malha pequena, e o amostrador continua testado numericamente contra
quadratura no próprio módulo Cervo.

### Extensão: propostas assimétricas e correção Hastings exata

A hipótese de proposta simétrica é uma propriedade do protótipo numérico
**atual**, não uma garantia para propostas futuras adaptativas, direcionais
ou de densidade desigual. Para taxas `qᵢⱼ` e `qⱼᵢ` em unidade comum,
a aceitação MH válida produz o fluxo **máximo reversível**:

`F(i,j) = min(wᵢ qᵢⱼ, wⱼ qⱼᵢ)`.

O Lean acrescenta `hastingsFlow_detailed_balance` (sem hipótese de simetria),
`hastingsFlow_le_forward` (capacidade de proposta),
`hastingsFlow_maximal` (maior fluxo admissível nos dois sentidos),
`hastingsFlow_list_balance` (conservação finita do fluxo aceito) e
`hastingsFlow_asymmetric_example` (controle 3:1 corrigido para 2:2).
Testes independentes usam frações exatas e cobrem 625 combinações de
pesos/taxas, além de 500 verificações da razão, incluindo taxas reversas
nulas. Quando `q` é representada por contagens, todas as linhas devem ter
**o mesmo denominador**: caso contrário as contagens não são probabilidades
comparáveis.

**Limites:** não há prova da soma de linha de um kernel estocástico completo,
da medida estacionária normalizada, da convergência de cadeias, da execução de
RNG ou de quaisquer medições de 1963. Esta correção protege a coerência
matemática da eventual implementação de propostas não simétricas; não ativa
nenhuma restrição histórica nem produz posterior para Conde.

## 2. Identificabilidade: fase absoluta × viés de linhagem

A observação RAAN sintética usa previsão congelada `H_i(θ)=H_i(0)+θ`
e um único desvio `b_g` por família de origem documental. No modelo
condicional, cada resíduo angular é

`r_i = (y_i - H_i(0) - θ - b_{g(i)}) mod 360°`.

O Lean modela esse resíduo em **milésimos de grau** com inteiros e módulo
`360000`. Demonstra, para **todo** corpus, fase, deslocamento e função de
vieses de grupo:

`r_i(θ+δ, b_g−δ) = r_i(θ,b_g)`.

Certificados: `residual_gauge_invariant`,
`residualVector_gauge_invariant`, `likelihood_gauge_invariant` e
`unanchored_phase_has_compensator`. O último fornece explicitamente um conjunto
de vieses alternativo com o **mesmo vetor de observações** para qualquer
translação da fase. O controle negativo `fixed_bias_can_break_gauge` mostra
que deslocar a fase **sem** compensar o viés pode mudar o resíduo.

Esta é uma **não-identificabilidade estrutural do modelo conjunto sem âncora**.
Com prior uniforme de Haar para todos os `b_g`, a marginalização circular
preserva essa simetria, como demonstrado numericamente pelo Cervo; o Lean
aqui **não formaliza a integral von Mises/Bessel, a medida Haar contínua nem a
posterior marginal normalizada**. Uma prior sintética concentrada em `θ` ou
`b_g` pode selecionar uma fase, mas isso é informação adicionada pelo prior.
Sem base histórica independente, não é localização inferida.

### Âncora calibrada: condição mínima, não dado encontrado

O teorema `calibrated_anchor_identifies_phase_modulo` agora explicita uma
condição necessária para sair da ambiguidade anterior: se **a mesma correção
angular de linhagem estiver fixada por calibração independente** e duas fases
produzirem o mesmo resíduo circular exato, essas fases são congruentes módulo
360°. `calibrated_anchor_rejects_noncongruent_phase` dá a forma falsificadora.
O controle adversarial Python muda fase e offset conjuntamente e confirma
que a ambiguidade retorna quando o offset não é conhecido.

Esse resultado **não** afirma que um registro NASA, outro registro derivado
de Space-Track ou um simples prior concentrado forneça a âncora. Tampouco
formaliza observação ruidosa, calibração histórica, independência instrumental
ou identificação de local/instante de reentrada. Para ativar restrição física
é necessário documento com instante UTC, referencial/operador, offset
identificado e incerteza correlacionada calibrada; até lá `ΔΘ=0`.

## 3. Inventário dos avanços que permanecem numéricos

| Componente | Estado verificável | O que não comprova |
| --- | --- | --- |
| Likelihood circular com offset compartilhado por linhagem, marginalizada analiticamente | Implementada em `tools/raan_circular_likelihood.py`; comparação com quadratura e testes de entradas | Calibração histórica dos κ ou correlações |
| Quatro cadeias MH, warmup, propostas uniformes e normais enroladas | Implementadas em `tools/raan_synthetic_phase_mcmc.py`, entradas exclusivamente `synthetic:` | Amostragem da órbita 528 de 1963 |
| Quadratura determinística de 1.440 nós | Oráculo independente da **amostragem**, para o mesmo alvo sintético | Validação da física ou da prior |
| R-hat e ESS bulk/tail sobre sen/cosseno | Implementados em `tools/raan_chain_diagnostics.py`, com casos de mistura ruim | Convergência universal, identificação ou independência instrumental |
| Núcleo reversível e gauge estrutural | Teoremas Lean deste módulo | Estacionariedade numérica, integral Haar, posterior histórica ou queda |

Há 123 linhas no extrato secundário de elementos 1963, mas apenas 119 épocas
únicas para os três objetos. Elas são de uma linhagem de catálogo; não
constituem 119 medições independentes. A data de decaimento NASA C197,
08/11/1963, não fornece instante nem coordenada de queda. A partição
cronológica 61/23/35 é retrospectiva, não cega.

## 4. Bloqueios antes de MCMC histórica

1. 🐢 Tartaruga/Lontra: observações instrumentais com época UTC, estação,
   referencial, definição de elemento, calibração e covariâncias, inclusive
   dependências 527/529. Referência: #396 e #647.
2. 🦫 Castor: operador orbital congelado que produza **RAAN catalográfico médio**
   na mesma época, frame e convenção; validação física com holdout independente.
3. 🦌 Cervo: parâmetros identificáveis ou âncora calibrada, prior física,
   modelo de seleção, concentração κ justificada, controles de sensibilidade
   e diagnóstico multivariado; nunca transformar bootstrap/quantidade de
   amostras MCMC em número de sensores.
4. 🐙 Polvo: só codificar novas restrições Lean de Θ a partir de relações
   observacionais com erros e dependências sustentados. Provas sobre
   métodos **não** restringem órbitas sem valores físicos validados.

## Reprodução e política de prova

```
cd formal
lake build
lake env lean Conde1963/CoreAxioms.lean
cd ..
python3 -m unittest discover -s formal/tests -p 'test_circular_mcmc_contract.py' -v
python3 -m unittest discover -s tests -p 'test_raan_synthetic_phase_mcmc.py' -v
```

O gate `lean-core.yml` compila o módulo importado pelo agregador, imprime axiomas
para os teoremas e rejeita `sorryAx`/`unsafe`. O teste Python separado testa
fluxos MH com frações exatas, inclinação assimétrica como contraprova e
invariância de resíduos na malha modular. Isso não substitui a prova Lean.

Referências e contexto: [likelihood circular](CIRCULAR_LIKELIHOOD_CONTRACT.md),
[amostrador e oráculo](SYNTHETIC_PHASE_MCMC_REFERENCE.md),
[diagnósticos](CIRCULAR_MCMC_DIAGNOSTICS.md),
[sensibilidade à âncora](ANCHORED_OFFSET_SENSITIVITY.md),
Metropolis et al. (1953), Hastings (1970), Vehtari et al. (2021).
