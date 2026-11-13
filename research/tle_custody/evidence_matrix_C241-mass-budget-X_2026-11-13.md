---
type: Guide
title: "C241: conservação de massa dos 527/528/529 com residual X e erro de referência"
description: "Orçamento físico condicional 1176 kg + epsilon, com X não catalogado, provas Lean, testes e vínculo futuro ao arrasto."
---

# Orçamento de massa: três objetos, X e incerteza da referência

## Evidência e grau epistemológico

A [matriz C61](../evidence_matrix_C001-C238_2026-11-11.md) atribui ao [GCAT satcat](https://planet4589.org/space/gcat/data/cat/satcat.html) uma massa total *associada* de aproximadamente **1.176 kg** e uma massa seca útil aproximada de **306 kg**, grandezas diferentes. O registro **não comprova** que 1.176 kg seja a massa da soma exclusiva dos três objetos NORAD 527/528/529 numa mesma época física. A ocorrência C241-L14 identifica 528 e 529 como detritos de pai catalogado 527, mas não fornece peças, massas, áreas nem análise completa do desmembramento. Valores nulos ou zero dos detritos nos catálogos são *ausência de informação*, nunca massa física zero. Documento secundário, com taxonomias conflitantes Agena B/D; não é ficha de engenharia primária. C61 é uma linha de matriz legada com hash de blob congelado; esta fatia não altera o acervo.

**Modelar a hipótese não exige aceitá-la como fato.** O [manifesto JSON](../constraints/C241_mass_budget_residual_2026-11-13.json) registra variáveis e dependências com estado CONNECTED_CONDITIONAL_NOT_HISTORICAL_BOUND.

## Equação de inventário em um tempo de referência

Denote m527, m528 e m529 as massas físicas positivas dos três corpos naquele inventário. Acrescente:

- **X ≥ 0:** massa da referência inicial fora dos três corpos conhecidos, incluindo outras peças, propulsante perdido ou matéria já desprendida anteriormente *somente se* a época contábil inicial e a genealogia do sistema incluírem essas parcelas. X não é necessariamente um quarto satélite, nem se deve contar duas vezes a mesma massa. Se a referência é posterior à perda, atualize o inventário de origem; não some uma perda anterior sem justificativa.
- **epsilon (assinado):** diferença entre a massa realmente abrangida pelo inventário inicial e o valor aproximado publicado pelo GCAT. Não é material físico nem "quarta massa". Sem ficha técnica e erro de medição, epsilon não possui sigma, distribuição ou limite numérico conhecido.

A hipótese de conservação fechada é:

    m527 + m528 + m529 + X = 1176 kg + epsilon

Somente quando o valor catalogado corresponder à massa inventariada, a época estiver definida e todas as outras saídas forem incluídas em X essa igualdade ganha significado físico. A equação sem epsilon e sem X é uma *subhipótese* particular, não premissa histórica estabelecida.

## Limites matemáticos

Caso **epsilon = 0**, há um resultado certo *condicional*: a soma dos três é no máximo 1.176 kg, e cada massa individual positiva é estritamente menor que 1.176 kg. A soma só é igual a 1.176 kg se X = 0.

Caso se obtenha, futuramente, um limite **|epsilon| ≤ E** e outro **0 ≤ X ≤ R**, haverá:

    max(0, 1176 - E - R) ≤ m527+m528+m529 ≤ 1176+E
    0 < cada m_i < 1176+E

As expressões usam kg. O limite inferior zero é somente ínfimo matemático para três massas positivas, não a previsão de que desapareceram. Sem erro E conhecido **não há teto numérico histórico**, mesmo que R seja especificado. Sem R conhecido mas com E limitado, a soma pode consumir quase todo o inventário em X e não há mínimo positivo uniforme.

Pode-se explorar um cenário **X pequeno**, por exemplo impondo R fornecido externamente. Não declarar esse cenário provável sem medições. A prova Lean inclui propositalmente um contraexemplo artificial com X maior que metade do total para demonstrar que conservação de massa NÃO implica residual pequeno.

## O que o arrasto consegue identificar

A dinâmica já implementada usa B_j = Cd_j * A_proj_j / m_j em m²/kg, multiplicado pela densidade e pelo fator cinemático. Um orçamento de massa compartilhado acopla os três m_j, mas **não fixa** área, forma, Cd nem densidade. O modelo de triagem orbital 528 da [PR #619](evidence_matrix_C241-orbital-screen_2026-11-13.md) identificou um coeficiente **efetivo de perda de altura**, NÃO B_j calibrado. O gauge de densidade e área/massa discutido em [C241-P27](../statistics/DRAG_DENSITY_SCALE_GAUGE_C241.md) continua em aberto. Não converter k em quilogramas, não atribuir ao fragmento a massa do corpo principal.

## Provas e reprodução

[Lean 4.35.0](../../formal/Conde1963/MassBudget527529.lean): massa individual menor que a referência sob premissas, soma limitada, equivalência entre soma exata e X nulo, contraexemplo X grande, e cota do orçamento com epsilon e R.

    python3 -m unittest discover -s tests -p test_mass_budget_527_529.py -v
    python3 tools/mass_budget_527_529.py --output /tmp/mass-budget-default.json
    python3 tools/mass_budget_527_529.py --error-max-kg 26 --untracked-max-kg 50 --output /tmp/mass-budget-example.json
    cd formal && lake build

O exemplo numérico com E=26 e R=50 é **somente hipótese de sensibilidade**, não medição do projeto. Os testes recusam tolerâncias/áreas inventadas e a promoção indevida do orçamento como limite físico histórico.

## Próximos documentos discriminantes

Conferir a definição original da massa 1.176 kg, massa seca, combustível e época (Agena B A00324/S00527). Recuperar a lista de peças desprendidas e suas épocas, massa expelida e eventual catalogação adicional. Com um orçamento verificável, poderemos introduzir priors geométricos explicitamente declarados e então validar estimativas físicas de B_j com dados orbitais e meteorológicos. O fato de três objetos terem datas de decaimento diferentes, isoladamente, não identifica seus pesos.

**Estado:** conexão científica nova; zero massa individual autenticada; nenhuma contração histórica de Θ, inferência de impacto ou dimensão física de 528 demonstrada.
