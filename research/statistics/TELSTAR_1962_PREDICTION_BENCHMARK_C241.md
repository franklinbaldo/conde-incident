---
type: Guide
title: "C241: contraste empírico de previsão óptica Telstar 1 (1962)"
description: "Benchmark histórico fonte-ancorado de erro de previsão por visada, separado de precisão instrumental do 528."
---

# Telstar 1962: pares observados e previstos em fonte contemporânea

**Recuperação histórica verificável em 13/11/2026:** A. J. Claus et al., *Orbit Determination and Prediction, and Computer Programs*, *Bell System Technical Journal*, vol. 42 (1963), páginas 1357–1382, NASA NTRS [19640000981](https://ntrs.nasa.gov/citations/19640000981). [PDF NASA](https://ntrs.nasa.gov/api/citations/19640000981/downloads/19640000981.pdf), SHA-256 `98cbd80eb06d381df2d4e78c6c92a6d4436ec3ea3f55b2c4e92baf6640a776b9`, 1.148.397 bytes. Tabela VII na página impressa **1380**, índice PDF **23** (zero-based). A transcrição CSV possui SHA-256 `50c09ca2ac44f48b037e2efa5e4ad6c96740d6ca10f4f0189684a4845ac7d061`.

## O que é efetivamente medido

A tabela contém **38 linhas** de azimute e elevação **observados** e **previstos**, em graus com duas casas, distribuídas em **cinco passagens** (124, 133, 143, 151 e 160), entre 23 e 27 de julho de **1962**. A passagem 143 atravessa a meia-noite UTC de 25 para 26 de julho; é uma única passagem de sete registros. Trata-se de **Telstar 1** acompanhado pela estação Andover, **não** NORAD 527/528/529, nem dados de novembro de 1963.

Os autores declaram que as previsões de até cinco dias utilizavam elementos calculados com as observações dos cinco dias anteriores; os ângulos comparados foram observados pelo rastreador de precisão. Isso constitui um **exemplo histórico efetivo de confronto previsão/medição futura** segundo o relato metodológico original, não uma inferência criada por repetição de números de catálogo. As 38 linhas não são 38 previsões estatisticamente independentes; o horizonte exato e o momento de emissão de cada previsão não constam da tabela.

O auditor calcula separação angular da visada esférica, não diferença plana de azimute. A equivalência de primeiro grau de pequenos resíduos, `delta_az * cos(elevacao)`, é explicitada no próprio artigo. Para o extrato de 38 pontos, obtém **RMS descritivo de 0,0334590°** e máximo de **0,0730545°**. Por passagem os RMS são 0,0244658°, 0,0201106°, 0,0270227°, 0,0330430° e 0,0513264°, nessa ordem. Esses números **não** são erro-padrão do sensor, desvio-padrão independente, covariância orbital, previsão terminal ou distribuição de cauda para 528.

A resolução decimal publicada (0,01°) não identifica a regra de arredondamento, a resolução física do rastreador ou o erro verdadeiro de cada observação. A seleção da tabela é editorial, examinada retrospectivamente, não um holdout cegamente registrado agora. A incerteza de 528 permanece `null`.

## Sensibilidade ao bloqueio por passagem (sem validação preditiva)

A análise adicional exclui integralmente uma das **cinco passagens** por vez e recalcula o RMS *dos 30 ou 31 registros restantes*, sem alterar o modelo que produziu as previsões históricas. Não é leave-one-pass-out cross-validation: **não há retreinamento, novas previsões, nem holdout cego**. O exercício mede somente quanto o descritivo publicado depende de cada cluster da própria tabela, sem inferir independência entre passagens.

| Passagem excluída | Linhas remanescentes | RMS descritivo (graus) |
|---|---:|---:|
| 124 | 30 | 0,0354742 |
| 133 | 31 | 0,0357907 |
| 143 (cruza meia-noite) | 31 | 0,0347478 |
| 151 | 30 | 0,0335691 |
| 160 | 30 | 0,0267494 |

O intervalo dos cinco RMS recalculados é **0,0267494°–0,0357907°**, largura **0,0090413°**; o RMS de todas as linhas era **0,0334590°**. A passagem 160 tem RMS próprio 0,0513264°, e sua exclusão causa a maior redução no agregado. Isso é heterogeneidade **descritiva de seleção**, não evidência de que a passagem 160 está errada nem estimativa de variância entre passagens. A tabela foi selecionada pelos autores e lida retrospectivamente; não há base para IC/SE, jackknife inferencial, distribuição preditiva de outra campanha ou sigma do NORAD 528.

O próximo teste realmente discriminante deve reservar passagens/estações **antes do ajuste** e exigir previsões datadas e observações posteriores independentes, com logs de origem e erros instrumentais. Nunca sortear 38 linhas como 38 unidades independentes.

## Diagnóstico de identificabilidade e próximo discriminante

- **Identificável nesta fonte:** resíduos de apontamento *impressos* para o satélite, local e passagens publicados; estatísticas descritivas condicionadas à amostra, com unidades explícitas.
- **Não identificável:** erro do sensor individual, distribuição preditiva generalizável para 1963, covariância de elementos do NORAD 528, correlação temporal completa, viés de Andover, última posição/instante do 528 e local de impacto.
- **Próximas observações discriminantes:** previsões NASA/NORAD originais emitidas antes da reentrada, com épocas e soluções de elementos, e rastreamento posterior independente dos mesmos objetos ou controles físicos comparáveis. Pré-registrar partição por **passagem, estação e linhagem**, nunca por linha da mesma passagem.
- **Ligação ao grafo:** fonte histórica NTRS 19640000981 → método de validação temporal exemplificado → dependência de fonte e de estação → candidato a protocolo de erro de previsão de #647 → `CONNECTED_PENDING_CALIBRATION`; `active_constraint=false`. Não se deduz nada sobre latitude, longitude ou queda em Conde.

O mesmo artigo (p. 1361, índice PDF 4) apresenta **outro teste explicitamente sintético** que adicionou ruído gaussiano assumido de 0,2 mrad a ângulos gerados; sua matriz de correlações dos elementos tem componentes próximas de ±1, e os autores alertam na p. 1362 para possíveis matrizes indefinidas. Esse **0,2 mrad é premissa artificial do teste**, jamais valor transferível para Telstar real ou 528.

Outra fonte com medições de arrasto de **oito objetos diferentes**, Jacchia e Slowey, *Smithsonian Contributions to Astrophysics* 8(1), 1963, [fac-símile](https://repository.si.edu/bitstreams/5abbb2c6-ec9d-42cd-b37d-063c88806aad/download), p. 1, tabela 1, cobre dados de 1958–1961; é candidata à calibração externa da **estrutura de arrasto**, não covariância do 528, e foi apenas triada. Nenhum valor foi transplantado.

## Replay e gates

```sh
python3 -m unittest discover -s tests -p 'test_telstar_1962_prediction_benchmark.py' -v
python3 tools/telstar_1962_prediction_benchmark.py --check
python3 tools/telstar_1962_prediction_benchmark.py --source-pdf /caminho/19640000981.pdf --check
```

A primeira verificação usa a transcrição congelada. A última exige bytes originais da NASA que correspondam ao SHA; o PDF não entra no Git por superar o limite de 20 KB. CI no SHA real é gate de integração. **MCMC histórico NOT_RUN; nenhuma probabilidade nem redução geográfica de 528.**
