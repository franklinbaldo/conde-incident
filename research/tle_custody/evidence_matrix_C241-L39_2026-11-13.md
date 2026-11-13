---
type: Guide
title: "C241-L39: partição condicional de massa com residual X para 527/528/529"
description: "Modelo matemático proposto pelo proprietário, ainda sem prova de que 1176 kg correspondam à massa conjunta dos três objetos na mesma época."
---

# C241-L39 · Conservação de massa com incógnita residual

**Pergunta científica:** se **1.176 kg** designavam a massa disponível ao grupo orbital 1963-003A/B/C (NORAD 527/528/529), qual restrição física seria legítima? O proprietário propôs repartir esse total entre os três corpos e preservar uma incógnita **X** para material perdido antes da separação, fragmentos adicionais ou massa não contabilizada.

**Status epistemológico:** hipótese do proprietário, **não verificada por fonte primária**. Não identificamos documento, página, hash, definição de massa (úmida/seca/estágio/carga útil) ou instante comum que comprovem 1.176 kg. Uma massa do lançamento inteiro não se torna automaticamente massa dos três objetos após separação; três números NORAD tampouco certificam que não houve outros fragmentos. Nenhuma restrição física histórica está ativa.

## Identidade matemática condicional

Em **uma mesma época física** \(t_0\), se os 1.176 kg forem válidos para um inventário completo, com erro total \(\delta\):

\[
m_{527}(t_0)+m_{528}(t_0)+m_{529}(t_0)+X(t_0)=1176+\delta\ \mathrm{kg},
\quad m_i,X\geq0,\quad |\delta|\leq\varepsilon.
\]

**X** é massa não contabilizada no **mesmo inventário** e **não** deve ser chamada de pequena ou residual em sentido quantitativo sem prova. A tolerância \(\varepsilon\) permanece desconhecida: não inventar ±1 kg nem desvio padrão. Se **hipoteticamente** \(\delta=0\), cada \(m_i\leq1176\) kg. A desigualdade só é **estrita** quando há alguma massa positiva nos outros termos. As massas não são iguais por definição. Uma única igualdade não determina a partição dos quatro termos (três graus de liberdade com soma exata).

**Cronologia:** a soma só pode usar massas na mesma época \(t_0\). Datas NASA de decaimento catalogado (528 em 08/11/1963, 529 em 31/12/1963, 527 em 09/01/1969: C241-L32) não são massas finais nem demonstração de queda no solo; não se podem somar como observações simultâneas. Ablação, propulsão e descarte precisam de inventário dinâmico específico.

**Órbitas e arrasto:** a [PR #619](https://github.com/franklinbaldo/conde-incident/pull/619) estima arrasto **efetivo**, não \(C_dA/m\) medido. Mesmo se 1.176 kg forem comprovados, a soma não identifica áreas, orientação, \(C_d\), densidade atmosférica ou massas individuais. Não transformar a hipótese em posterior, limite de área ou posição geográfica de reentrada.

**Fonte:** afirmação do proprietário nesta investigação em 13/11/2026; não é documento físico do objeto. Manifesto [C241-L39](mass_partition_C241-L39.json). Testes offline: executar o arquivo de tools mass_partition_C241_L39.py e a suíte tests/test_mass_partition_C241_L39.py via unittest. Os exemplos numéricos da suíte são apenas contramodelos hipotéticos de unicidade, **não** novas massas observadas.

**Para ativar:** recuperar fonte original de massa, identificar exatamente os componentes e a definição, demonstrar a correspondência com 527/528/529 e época de separação, contabilizar estágios e fragmentos, distinguir erro do número \(\delta\) de massa física X e obter limites demonstráveis. Até lá permanecem inativos: restrição física, uso no ajuste de arrasto e prova histórica Lean. O domínio orbital Θ não se altera.

## Retificação de proveniência complementar: C241-L40

A auditoria posterior [C241-L40](evidence_matrix_C241-L40_2026-11-13.md) recuperou as linhas exatas do **GCAT** e sua semântica documental: o valor 1176 kg está em **TotMass na linha S00527**, que inclui massa de objetos ligados, enquanto 528 e 529 exibem zeros catalográficos sem medição física. O lançamento imprime **OrbPay=1.176 t**, carga orbital gerada automaticamente, não massa medida da soma dos três. Há ainda Agena B **A00324** com 900 kg Mass e 870 kg DryMass, o que cria duas composições numéricas (306+900=1206; 306+870=1176), sem reconciliação instrumental conhecida. Isto **não valida** uma partição física dos três NORAD; o modelo desta matriz permanece contrafactual.
