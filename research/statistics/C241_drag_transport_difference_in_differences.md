---
type: Guide
title: 'C241: testar o transporte atmosférico antes de usar o 527 para prever o 528'
description: 'Contrastes diferença-em-diferenças com posto exato entre objetos e épocas, sem dados históricos novos nem posterior.'
---

# Um holdout do 528 depende da hipótese de transporte da atmosfera

**Pergunta falsificável:** observar o proxy de arrasto dos objetos 527, 528 e 529 na época e0 e novamente o 527 na época e1 basta para prever o proxy do 528 em e1? A [análise compartilhada anterior](C241_drag_density_mass_gauge.md) respondia sim, **sob densidade efetiva comum e conhecida até um nível por época**. Esta fatia prova em quais modelos a resposta deixa de valer. São canais *contrafactuais*, não medições de 1963.

## Equação e três modelos encaixados

Considere `z(i,t)=-q(i)+g(i)+s(t)+delta(i,t)` como proxy hipotético de log-arrasto **calibrado**, com q=log massa, g=log(Cd·área projetada), s=log densidade comum. `delta(527,t)=0` fixa um referencial convencional, não comprova densidades idênticas. Os três modelos são:

1. **Compartilhado:** delta=0 nos três corpos, seis proxies, oito parâmetros, posto exato 4.
2. **Desvio relativo constante:** delta(528) e delta(529) desconhecidos, mas estáveis em e0/e1, dez parâmetros, posto 4.
3. **Desvio relativo variável:** delta(528,e0/e1) e delta(529,e0/e1) livres, doze parâmetros, posto 6.

| Teste idealizado | Compartilhado | Desvio constante | Desvio variável |
| --- | --- | --- | --- |
| Proxy futuro do 528 estimável com e0 de todos + 527 em e1 | Sim | Sim | **Não** |
| Massa 528 estimável com massa e CdA do 527 e CdA do 528 calibrados | Sim | **Não** | **Não** |
| Acrescentar um delta(528) ou delta(528,e0) diretamente calibrado | Desnecessário | Identifica massa, condicionalmente | Identifica massa, condicionalmente |

A prova utiliza apenas independência linear de linhas racionais, sem erros observacionais assumidos. Assim, uma série longa da **mesma linhagem catalográfica** não deve ser contabilizada como calibração adicional de densidade, geometria ou independência instrumental.

## A observação que discriminaria os modelos

A diferença-em-diferenças coetânea é:

`D=[z(528,e1)-z(528,e0)]-[z(527,e1)-z(527,e0)]`.

No modelo compartilhado e no de desvio estável, `D=0` exatamente. No modelo variável, `D=delta(528,e1)-delta(528,e0)`. Uma medição calibrada, independente, do **drift relativo** permite novamente predizer o proxy futuro, **sem identificar a massa**. Isso separa acerto de previsão de parâmetro físico identificado. A habilidade de detectar `D != 0` depende de um erro instrumental calibrado; não atribuí limiar estatístico nem p-valor.

Um `D` diferente de zero **não prova variação real de densidade**: também pode resultar de atitude/CdA variáveis, erro na dinâmica e viés temporal de catálogo. Não é lícito somar TLEs espelhados como réplicas independentes. Se as altitudes ou trajetórias não coincidirem, a hipótese de mesmo s(t) precisa de transporte físico verificado.

**Aquisição discriminante mínima:** para testar a previsão, requer proxies do 528 em e0 e e1 e do controle 527 nas duas épocas, com UTC, escala, operador dinâmico, matriz de incerteza e genealogia de sensores. Para identificar massa, requer também geometria/Cd do 528 e sua densidade efetiva calibrada, direta ou por controle com desvio relativo medido. As fichas de engenharia do Agena 2313 e registros SPADATS/SAO específicos do 528 são candidatos de busca, não comprovação de canais disponíveis.

## Estado histórico

A [custódia C241-L40](../tle_custody/gcat_mass_semantics_C241-L40.json) não atribui massa instrumental ao 528, nem autoriza tratar os 1.176 kg como inventário fechado dos três NORAD. Não recuperamos nesta fatia novos arrastos calibrados nem transporte atmosférico de 1963. **MCMC = NOT_RUN**, posterior de massa e probabilidade de impacto nulas, **nenhuma redução do domínio geográfico de Conde**. A prova condicional não altera esses fatos.

Reprodução: `python3 -m unittest discover -s tests -p test_drag_transport_difference_in_differences_C241.py -v` e `python3 -m tools.drag_transport_difference_in_differences_C241`. Contraste de sensibilidade das drafts [#634](https://github.com/franklinbaldo/conde-incident/pull/634) e [#641](https://github.com/franklinbaldo/conde-incident/pull/641).
