---
type: Experiment
title: "C241: MCMC das massas e semântica GCAT do OPS 0180/Agena B 2313"
description: "Distinção entre massa individual de 306 kg, estágio de 900/870 kg e total de 1176 kg; modelos condicionais sem posterior histórica inventada."
experiment_id: C241-MASS-MCMC-20261113
verification_status: SOURCE_SEMANTICS_AUDIT_SYNTHETIC_MCMC_ONLY
---

# 306 kg, 900/870 kg e 1.176 kg não são a mesma medida

A [documentação oficial do GCAT](https://planet4589.org/space/gcat/web/cat/cols.html) distingue:

- **Mass:** massa de um objeto na inserção orbital, **sem incluir** outros objetos anexados;
- **DryMass:** massa seca desse mesmo objeto, sem propelentes/consumíveis, também sem incluir anexos;
- **TotMass:** massa total de um conjunto inicialmente anexado, registrada em uma das entradas, não necessariamente um quarto corpo físico.

Na [ocorrência C61](../evidence_matrix_C001-C238_2026-11-11.md), os **306 kg** estão associados ao **OPS 0180/S00527**, não ao conjunto inteiro dos objetos 527/528/529. A [auditoria GCAT C241-L40 (PR #629)](https://github.com/franklinbaldo/conde-incident/pull/629) conferiu **Mass=306 kg e DryMass=306 kg para S00527**, isto é, a massa seca nominal da carga útil específica também é 306 kg, **não** a massa seca total da plataforma anexada. O [catálogo do estágio A00324, Agena B 2313](https://planet4589.org/space/gcat/data/cat/auxcat.html) apresenta **Mass=900 kg** e **DryMass=870 kg**. O campo total associado ao OPS 0180 é **1.176 kg**. Os dados de 528/529 continuam sem fichas de massa individuais; os zeros do catálogo de detritos não são massas medidas.

O [currentcat](https://planet4589.org/space/gcat/data/derived/currentcat.html) descreve a reentrada de S00527 como **anexado a A00324**, enquanto S00528 e S00529 foram categorizados como detritos descendentes do conjunto. Assim, a massa orbital dinâmica associada ao **número 527** não pode ser igualada automaticamente a 306 kg: pode compreender a carga útil mais o estágio co-orbitante.

## Contradição nominal e hipóteses

- Massa individual OPS 0180 + massa do estágio na inserção: **306+900=1.206 kg**.
- Massa individual OPS 0180 + massa seca do estágio: **306+870=1.176 kg**.
- Diferença entre estágio na inserção e seco: **30 kg**.
- Diferença entre soma das duas massas de inserção e TotMass informado: **30 kg**.

Não sabemos se o valor total de 1.176 kg mistura definições, se houve consumo de 30 kg, se a ficha do catálogo tem erro sistemático ou se as épocas não são iguais. **Uma coincidência aritmética não é comprovação de consumo de 30 kg de propelente em determinada data**. Não criar 30 kg de um novo componente X, nem contabilizar esses 30 kg duas vezes como propelente e discrepância catalográfica.

O [ledger de semântica](../constraints/C241_L39_stage_payload_mass_semantics_20261113.json) mantém três hipóteses alternativas de inventário: **inserção nominal de 1.206 kg**, **TotMass catalogado de 1.176 kg**, **carga útil + estágio seco de 1.176 kg**. Nenhuma foi validada como inventário exclusivo de três peças na época da separação.

A equação conservativa segue condicional e exige **mesma época** e **sistema fechado corretamente identificado**:

[
m_{527}^{\mathrm{completo}}(t_s)+m_{528}(t_s)+m_{529}(t_s)+X(t_s)
=M_{\mathrm{inicial}}-L_{\mathrm{anterior}}+\varepsilon.
]

Aqui, \(X\) é massa fora dos três corpos na época de partição, \(L\) representa material já perdido após a época de referência inicial, e \(\varepsilon\) é erro da massa catalogada. Defina as fronteiras contábeis para não contar a mesma massa em X e L. Os três objetos numerados não são necessariamente todos os componentes físicos do veículo original.

## Markov/MCMC e como integrar os 306 kg

O [sampler experimental](../../tools/mass_partition_mcmc.py) trabalha com frações positivas de quatro parcelas (527 completo, 528, 529, X) e epsilon. Um prior Dirichlet mostra como a repartição pode variar sob hipóteses diferentes, mas nenhuma é posterior histórica.

A massa de **306 kg é um dado de componente, não medição de m527 completo**. Portanto, deve alimentar um futuro submodelo hierárquico:

[
m_{527}^{\mathrm{completo}}(t)=m_{\mathrm{OPS\ remanescente}}(t)
+m_{\mathrm{Agena\ remanescente}}(t)+m_{\mathrm{outros\ anexos}}(t).
]

As massas remanescentes dependem de separações, combustível e origem exata dos detritos. A verossimilhança para os 306 kg só poderá atuar sobre o **componente OPS** quando o campo e a época forem reconciliados, não diretamente sobre m527 no conjunto orbital.

No cadastro do lançamento, o campo **OrbPay=1,176 t** é gerado pelo GCAT, enquanto **OrbMass=0** é campo não preenchido, não uma medida de massa orbital zero. Não contar OrbPay como evidência independente de TotMass. Os três inventários possíveis não têm pesos históricos conhecidos. O MCMC permite selecionar uma base explicitamente para experimentos **sintéticos**, sem convertê-la em “modelo mais provável”. Quatro cadeias Metropolis-Hastings com sementes independentes, propostas sobre log-razões e epsilon, priors explícitos, observações artificiais de massa e Cd·A/m e diagnósticos rank-Rhat/ESS exercitam o método. Passar diagnóstico de convergência numérico **não autentica dados ou prior**. A primeira inferência histórica só será permitida após obter medições de área/massa ou arrasto calibrado, dados independentes de densidade, genealogia de componentes, erros e referências temporais.

## Diagnóstico numérico real da fixture sintética

A execução de desenvolvimento no Jatobá com a fixture declaradamente artificial passou os testes, mas **as cadeias não convergiram segundo o gate**. Com a semente congelada, o componente residual X apresentou R-hat aproximado **2,56** e ESS bulk próximo de **4,8**, muito aquém das exigências predeclaradas. Assim, mesmo as tabelas de quantis sintéticos produzidas pelo sampler servem **apenas como diagnóstico de desenvolvimento**, não como resultados de uma posterior confiável. O JSON agora expõe `numerical_convergence_gate_passed`, `posterior_marginal_summaries_approved` e `historical_posterior_certified=false`, sem mascarar a falha.

Isso é independente da falta de fonte histórica. Mesmo que corrigíssemos a mistura da cadeia, os 306 kg do componente OPS e os 1.176 kg catalogados ainda não forneceriam, por si, uma verossimilhança que identificasse as três massas. O próximo experimento estatístico deve melhorar o sampler e só depois introduzir, com proveniência, restrições reais sobre área projetada, coeficiente de arrasto ou inventário de componentes.

## Prova Lean da ambiguidade e dos limites de componente

O módulo [MassComponent306.lean](../../formal/Conde1963/MassComponent306.lean) está importado no projeto Lean e prova aritmeticamente:

- 306+900=1176+30 kg, enquanto 306+870=1176 kg;
- a diferença de campos Mass e DryMass do estágio é 30 kg, **não** uma perda de combustível observada em 1963;
- sob hipótese de inventário físico válido, se o objeto dinâmico 527 contiver carga útil remanescente e estágio anexado, sua massa total é pelo menos a massa dessa carga útil remanescente;
- a carga inicial de 306 kg deve estar distribuída entre material retido e material separado, que pode incluir 528, 529 e X; não atribuir toda a carga diretamente ao 527.

O Lean certifica implicações das premissas; não autentica retrospectivamente os valores secundários do catálogo.

## Falsificabilidade e reprodução

```sh
python3 -m unittest discover -s tests -p test_gcat_mass_lineage_audit.py -v
python3 -m unittest discover -s tests -p test_mass_partition_mcmc.py -v
python3 tools/gcat_mass_lineage_audit.py --output /tmp/gcat-mass-semantics.json
python3 tools/mass_partition_mcmc.py --output /tmp/mass-priors-only.json
python3 tools/mass_partition_mcmc.py --synthetic-fixture tests/fixtures/mass_partition_synthetic_c241.json --output /tmp/mass-synthetic.json
```

**Evidência mantida, não resolvida:** a contabilidade exata no instante de separação, a massa individual dos detritos, coeficientes Cd, áreas, covariância orbital, prior de X e precisão dos 1.176 kg permanecem desconhecidos. Nenhuma distribuição posterior histórica, posição ou impacto em Conde foi calculado. **Conectividade documental aumentou; domínio físico Θ inalterado.**
