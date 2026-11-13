---
type: Experiment
title: "C241: limites compartilhados de massa nos modelos orbitais e probabilísticos"
description: "Contratos executáveis de conservação, massa/área/Cd e limites condicionais; auditoria de doze consumidores."
experiment_id: C241-MASS-CROSSMODEL-20261113
verification_status: CONDITIONAL_SOURCE_LINKED_NOT_CALIBRATED
---

# Uma restrição de massa compartilhada por todos os modelos

O inventário condicional utiliza: 306 kg para a carga útil OPS 0180/S00527, 900 kg para o estágio Agena B, 870 kg para o estágio seco e 1176 kg para o TotMass associado, todos oriundos de catálogo secundário. A soma de massas individuais de inserção é 1206 kg; a soma OPS+estágio seco é 1176 kg. Isso **não prova** uma partição fechada entre exatamente os NORAD 527, 528 e 529.

**Fonte C61:** [matriz histórica](../evidence_matrix_C001-C238_2026-11-11.md) e [GCAT satcat](https://planet4589.org/space/gcat/data/cat/satcat.html). A auditoria mais detalhada [C241-L40, PR #629](https://github.com/franklinbaldo/conde-incident/pull/629) ainda precisa ser incorporada/reconciliada como fonte canônica. Orçamento anterior: [C241-MASS-X](../constraints/C241_mass_budget_residual_2026-11-13.json). Essas linhas pertencem à mesma família de catálogo e não constituem sensores independentes.

## Um contrato tipado para as restrições

O [contrato TypeScript compartilhado](../../src/lib/orbitMassConstraints.ts) exige a escolha explícita da base 1176/1176/1206, massa individual positiva para cada um dos três objetos, massa X de material fora deles, perdas anteriores L e erro catalográfico assinado epsilon, todos na mesma convenção contábil:

\[
m_{527}+m_{528}+m_{529}+X+L=M_{\rm base}+\varepsilon.
\]

A verificação é de consistência **aritmética condicional**, e não probabilidade histórica. Um candidato com soma incompatível é rejeitado; um candidato compatível não se torna historicamente verdadeiro. É proibido contar a mesma matéria duas vezes em X e L.

Sem limite independente de epsilon, **não existe teto histórico numérico comprovado** para massas individuais. Com hipóteses explícitas |epsilon|≤E, X≤R, L≤D, o somatório dos três possui limite inferior condicional max(0,M_base−E−R−D) e superior M_base+E. Se uma quantidade da carga útil de 306 kg ficar comprovadamente retida no objeto 527, ela consome a parcela correspondente do total. Os 306 kg NÃO são automaticamente a massa do conjunto orbital completo 527.

## Consumidores e integração real

A [matriz de roteamento](../constraints/C241_mass_crossmodel_routing_2026-11-13.json) enumera doze modelos/consumidores e o [auditor](../../tools/audit_mass_crossmodel.py) verifica sua cobertura e status. Quatro consumidores agora têm interfaces opcionais de cenário de massa:

| Modelo | Efeito real da restrição |
|---|---|
| Propagador cartesiano J2/arrasto | Derivar B=Cd·A/m das massas/áreas/Cd explícitas e encaminhar ao mesmo motor de força, sem alterar a gravidade |
| Atmosfera baseada em drivers MSISE | Injetar o mesmo B condicional na função de densidade com fontes e referenciais, sem inventar densidade |
| Inversão balística | Comparar B inverso à hipótese de massa/área escolhida, sem descartar órbitas históricas por divergência numérica de modelo auxiliar |
| Monte Carlo exploratório | Substituir B sorteado por B do cenário quando explicitamente solicitado, preservando o aviso de simulação não calibrada e nenhuma probabilidade geográfica histórica |

As demais ligações permanecem explicitamente marcadas: o k efetivo do modelo secular não é um CdA/m calibrado; Lean prova apenas as implicações condicionais; MCMC de massas (PR #634) não oferece posterior histórica; contraste angular não recebe sigma universal por saber massas; tela de sensibilidade legada é exploratória; fragmentação/deposição exige material, forma e ablação.

## Dimensões e área projetada

O contrato implementa uma projeção condicional de limites de área quando **três intervalos** estão presentes: massa, coeficiente balístico B e coeficiente de arrasto Cd:

\[
B_{\min} m_{\min}/C_{D,\max}
\leq A_{\rm proj} \leq
B_{\max} m_{\max}/C_{D,\min}.
\]

Se algum fator faltar, a função retorna valores nulos, não um número inventado. O diâmetro equivalente de projeção circular exige escolha expressa dessa geometria. Não representa o tamanho medido da peça real.

## Falhas e limitações preservadas

O dia NASA 08/11/1963 é um registro de catálogo, não instante terminal observado. Não há instrumento com sigma do 528, massa do detrito, geometria, Cd, inventário fechado ou densidade espacial calibrada. O domínio físico histórico Theta permanece não contraído. Massa não corrige a antiga RAAN 284,1520°, não exige diferença angular constante entre objetos e não cria um posterior de Conde.

A diferença entre fontes GCAT, em especial o significado exato dos 30 kg de diferença entre massas de inserção e campo TotMass, continua aberta. A prova aritmética não estabelece perda real de combustível.

## Verificação reproduzível

Executar no HEAD exato do projeto:

    python3 -m unittest discover -s tests -p test_mass_crossmodel_audit.py -v
    python3 tools/audit_mass_crossmodel.py --output /tmp/c241-mass-routing.json
    node --experimental-strip-types --test tests/orbitMassConstraints.test.mjs
    node --experimental-strip-types --test tests/orbitDragDensityGauge.test.mjs tests/orbitSpaceWeatherAdapter.test.mjs

Novas evidências calibradas podem atualizar a mesma interface. Nunca preencher massa ou erro faltante com zero nem afirmar redução histórica sem prova física.
