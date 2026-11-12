---
type: Guide
title: "Cervo: sensibilidade à âncora angular de viés de linhagem"
description: "Extensão matemática von Mises condicional com conexão cumulativa e testes adversariais, sem posterior histórica"
---

# Âncora circular explícita: sensibilidade, não observação

**Estado: CONDITIONAL_METHOD_ONLY; EXTERNAL_ANCHOR_NOT_RECOVERED; NO_HISTORICAL_POSTERIOR.**
Fatia da issue #202, sobre a verossimilhança Haar uniforme da PR #158, a simetria de gauge da PR #137 e os diagnósticos da PR #193. IDs da matriz: C25#1, C179#1, C180#1, C181#1 e C241-L3. Fonte derivada: [espelho secundário Space-Track para 1963](https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/main/data/tle_1963.parquet): 123 linhas, 119 épocas únicas, uma família documental sem prova de sensores independentes. Não há novo registro primário, precisão angular ou elemento orbital. C197 informa somente o dia catalogado NASA de decaimento 08/11, sem hora/local físico.

## Parâmetros, prior e likelihood condicionais

Defina o resíduo circular r_i = wrap(y_i-H_i(theta)) em radianos, **após** Castor validar a conversão de estado orbital em RAAN no frame, época e convenção catalográfica. O modelo assume condicionalmente erros VM(r_i|b_g,kappa_i) e um único viés b_g por família documental; a independência condicional ainda é hipótese, não fato do espelho secundário.

O modelo antigo assume prior Haar VM(b_g|mu_g,0). Esta extensão permite experimentos hipotéticos VM(b_g|mu_g,lambda_g) com média circular mu_g e concentração lambda_g não negativa. A integral analítica é:

log p(r|H,kappa,mu,lambda) =
  soma_g [log I0(|lambda_g exp(i mu_g) + soma_i kappa_i exp(i r_i)|)
         -log I0(lambda_g)-soma_i log I0(kappa_i)-n_g log(2 pi)].

Lambda é a força do **prior de offset**, não a precisão de cada medida. Com lambda=0 a média do prior é irrelevante e a verossimilhança recupera exatamente o caso Haar, com não-identificação da fase absoluta. Um prior sintético concentrado pode fazer uma observação isolada parecer informativa sobre fase absoluta: demonstra **sensibilidade ao prior**, não identificação histórica. Referências matemáticas: [DLMF 10.32](https://dlmf.nist.gov/10.32) e [DLMF 10.40](https://dlmf.nist.gov/10.40).

A função OffsetAnchor exige source_ref e independence_basis textuais, mas esses campos são **declarações de quem chama a função, não verificação de custódia**. Todos os parâmetros de testes são sintéticos. Um boletim NASA e um catálogo oriundos do mesmo rastreamento não são automaticamente âncoras independentes. Não há prior de theta, ajuste orbital, cadeia MCMC, probabilidade de queda ou localização produzida aqui.

## Holdout e condições de erro

A função anchored_marginal_log_density integra um offset por linhagem. anchored_predictive_log_density(fit,future,anchors) computa log p(Y_future|Y_fit,H,kappa,anchor) por razão das marginais, preservando **H, kappas, grupos e âncora congelados**. A divisão 61/23/35 é retrospectiva, não cega e dentro de uma só linhagem; não valida a posterior.

Os testes verificam quadratura angular independente, limite Haar, giro conjunto de dados/prior, aumento da diferença preditiva em um cenário sintético com âncora forte, holdout sem refit, grupos novos, duplicatas, referências ausentes e overflow explícito. Não substituem calibração instrumental, covariância por época, modelo de seleção, dinâmica nem MCMC.

## Ligação cumulativa sem restrição física fabricada

A [ponte JSON](../constraints/raan_offset_anchor_candidate_C241.json) conserva b_g, mu_g, lambda_g, kappa_i, r_i, H_i(theta), linhagem e dependências. Estado CONNECTED_PENDING_EXTERNAL_ANCHOR_AND_CALIBRATION: novos elos explícitos entre prior e offset, mas **delta de domínio admissível NOT_EVALUABLE**, sem resolver RAAN 284,1520 versus ~198,5261. Nenhuma nova restrição foi ativada, e null significa desconhecido, não zero.

Bloqueios já solicitados, sem duplicatas: 🐢 [Tartaruga inbox #1](https://github.com/franklinbaldo/tartaruga/issues/1), custódia/erros e independência; 🦫 [Castor inbox #1](https://github.com/franklinbaldo/castor/issues/1), H físico compatível com elementos médios TLE e holdout. Uma âncora só terá uso histórico após prova do referencial, fonte independente, precisão, processo de seleção e validação preditiva externa.
