---
type: Guide
title: "🦌 Cervo: MCMC circular sintético e teste contra quadratura"
description: "Fase livre RAAN, gauge, priors explícitos e quatro cadeias MH; nenhuma posterior histórica"
---

# Referência MCMC sintética: fase angular, não reentrada

**Estado: SYNTHETIC_ONLY; NO_HISTORICAL_POSTERIOR; NO_CONDE_SITE_PROBABILITY.**
Issue #219. Este componente de estatística não substitui a dinâmica física do
Castor, não lê dados reais, não estima a hora de reentrada nem modifica a
posterior histórica inexistente. Os exemplos dos testes são **inventados
deliberadamente e marcados como brinquedos matemáticos**, nunca observações.

## Contrato do modelo e simetria

A fase escalar livre theta em S1 representa uma translação angular
hipotética comum em um observável RAAN catalográfico:

- Predição congelada por época: H_i(theta) = H_i(0) + theta (mod 360 graus).
- Resíduo angular: r_i(theta) = wrap(y_i - H_i(theta)).
- Erro condicional: VM(r_i | b_g, kappa_i), com b_g compartilhado
  por linhagem documental g; condicionalidade e forma VM não calibradas.
- Offset: b_g ~ VM(mu_g, lambda_g). lambda=0 equivale à prior Haar.
- Fase: theta ~ VM(mu_theta, kappa_theta). kappa_theta=0 é Haar.
- Likelihood integrada: código já aprovado nas PRs #158 e #206.
  O novo módulo apenas avalia o alvo condicional para theta.

Se lambda_g=0 para todos os grupos, a verossimilhança é **invariante**
à translação de theta. Mesmo infinitas réplicas da mesma linhagem
não fixam a fase absoluta. Uma prior de theta concentrada pode dar
uma posterior concentrada, mas essa concentração vem **da prior**,
não de observação histórica adicional. Uma âncora do viés só resolveria
a simetria cientificamente se fonte e precisão independentes fossem
demonstradas, o que não ocorreu.

## Algoritmo, reprodutibilidade e oráculo

Quatro cadeias Metropolis-Hastings independentes (RNG inicializado com
seeds determinísticas distintas), inícios separados em 90 graus.
Proposta q simétrica: mistura de uniforme em S1 com normal enrolada
centrada no estado corrente. A regra de aceitação usa a diferença
de log-alvo; a razão de propostas cancela por simetria.
Warmup é descartado; sem adaptação a holdout.
O RNG, warmup, deslocamento, salto global e taxas de aceitação são
reportados. O resultado inclui diagnósticos rank-Rhat e ESS
seno/cosseno já existentes em tools/raan_chain_diagnostics.py;
PASS numérico é necessário mas insuficiente para validade histórica.

Um segundo procedimento não usa MCMC: quadratura determinística
periódica de 1.440 nós sobre theta para calcular E[exp(i theta)].
É oráculo **independente do mecanismo de amostragem**, embora compartilhe
o mesmo log-alvo matemático. Os testes verificam momento circular do
MH versus quadratura, invariância 360 graus, gauge Haar, prior forte
que domina fase não identificada, reproduzibilidade, inputs inválidos
e cadeias artificialmente travadas detectadas pelos diagnósticos.

## Proveniência, conexões e bloqueios

Ocorrências compartilhadas: C25#1, C179#1, C180#1, C181#1, C241-L3;
fonte secundária de RAAN (119 épocas únicas, 123 linhas, 1 linhagem).
NASA C197 informa **somente a data catalogada 08/11/1963**,
não hora/local de queda. Os registros históricos NÃO entram nos testes
de MCMC. A partição cronológica 61/23/35 é retrospectiva não cega e
não é reutilizada como se fornecesse independência.

A conexão pendente do modelo ao grafo cumulativo está em
research/constraints/raan_phase_mcmc_candidate_C241.json.
Aumenta conectividade entre parâmetro theta, H, offset, erro,
prior e holdout, sem ativar restrição física ou reduzir domínio.

Dependências ainda não atendidas: operador físico no mesmo tipo
de elemento médio TLE, escala e covariância do sensor, independente
referência angular, função de seleção, tratamento de linhagens,
prior físico de theta, identificação do referencial e avaliação
preditiva externa. Não inventar kappa, lambda, priors ou
probabilidade de impacto a partir do harness sintético.

**Como testar:** python3 -m unittest discover -s tests
-p 'test_raan_synthetic_phase_mcmc.py' -v.
Referências matemáticas: Metropolis et al. (1953);
Hastings (1970), Biometrika 57(1) 97-109, DOI 10.1093/biomet/57.1.97;
Vehtari et al. (2021), DOI 10.1214/20-BA1221 e
https://mc-stan.org/docs/reference-manual/analysis.html.
