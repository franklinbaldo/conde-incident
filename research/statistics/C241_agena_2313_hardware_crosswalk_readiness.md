---
type: Guide
title: 'C241: nomenclatura Agena 2313 não identifica massa nem peça do 528'
description: 'Triagem reproduzível de fontes 1963-003 e requisito observacional para tornar um dado de engenharia discriminante.'
---

# C241: proveniência antes de atribuir massa ao NORAD 528

O conflito de rótulos discutido no [Cafezinho #16](https://github.com/franklinbaldo/cafezinho/issues/16) é de **nomenclatura e escopo**. NASA SP-4004 (1964, p. 502, verificação visual no projeto) e índice textual NSA de 1975 chamam o **lançador** de Thor-Agena D; GCAT denomina o **estágio** Agena B e outra compilação denomina o lançador Thor Agena B. Um rótulo de lançador e um de estágio não são automaticamente observações concorrentes da **mesma peça física**; tampouco a coincidência entre duas publicações certifica duas inspeções técnicas independentes. A imagem do relatório NSA ainda carece de custódia binária e inspeção visual. O arquivo [de alegações](../tle_custody/c241_agena_2313_name_claims_20261114.json) conserva precisamente os escopos, famílias e estados de verificação.

## A pergunta discriminante

Para passar de uma nomenclatura do voo 2313 a massa física do objeto 528, faltam **duas pontes diferentes**: (i) ficha primária do equipamento específico, com componente, época, massa e convenção wet/dry; (ii) associação documentada entre esse componente e o catálogo **1963-003B/NORAD 528**, incluindo continuidade física entre épocas. Mesmo um manual Agena B ou D com massas nominais não substitui essas pontes. Falha de bateria da missão 7153 também não estabelece separação nem reentrada.

O verificador `tools/c241_agena_crosswalk_readiness.py` rejeita converter rótulo de classe, massa total de lançamento, mera contagem de páginas ou proxy de arrasto em massa individual. Uma candidata hipotética de massa direta do 528 precisa de identidade certificada, época UTC, referência de calibração, massa positiva, incerteza finita estritamente positiva, convenção e hash binário. A rota alternativa exige massa por componente e ligação de voo específica no **mesmo instante**, além de continuidade física documentada; **a ferramenta não confere autenticidade de uma alegação só porque seu campo foi preenchido**. Os testes favoráveis são integralmente sintéticos.

Um registro positivo, depois de verificado externamente, poderia acrescentar no modelo de seis massas uma linha na coordenada `m528`, posto condicional +1. Não resolveria `X`, perdas `L`, viés de inventário, geometria `CdA`, nem densidade atmosférica. Novos holdouts orbitais de 527/529 serviriam para testar transporte dinâmico, não para fornecer por si mesmos a ponte de hardware. O histórico continua em posto de observações diretas de massa **0**. Nenhuma distribuição posterior ou redução geográfica foi produzida.

## Aquisições prioritárias e testes

Priorizar: ficha específica do voo 2313 e lista as-built de seus componentes; relatório de separação/deploy com referência 1963-003B; registro individual NORAD/SPADATS com época, observável, estação e incerteza. Registrar também resultados negativos de busca com acervo e query delimitados. Não transformar documento de inventário de caixa Smithsonian RU263 em conteúdo não consultado.

Reproduzir: `python3 -m unittest discover -s tests -p test_c241_agena_crosswalk_readiness.py -v` e `python3 -m tools.c241_agena_crosswalk_readiness`. Estados históricos: `historical_constraint_active=false`, `historical_mcmc=NOT_RUN` e `domain_reduction=false`.

Este gate serve de veto ao consumo prematuro pelas drafts [#634](https://github.com/franklinbaldo/conde-incident/pull/634) e [#641](https://github.com/franklinbaldo/conde-incident/pull/641), não como desbloqueio delas.
