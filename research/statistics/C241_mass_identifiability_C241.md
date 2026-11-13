---
type: Guide
title: "C241: posto de massa e observações discriminantes"
description: "Auditoria racional de identificabilidade de 527/528/529/X sob a semântica original do GCAT, sem posterior histórica."
---

# C241: identificabilidade da massa, antes do MCMC

**Fonte documental:** C241-L40, [GCAT 1.8.9](https://planet4589.org/space/gcat/web/cat/cols.html), registro de custódia `research/tle_custody/gcat_mass_semantics_C241-L40.json`. É catálogo secundário contemporâneo, não folha de engenharia de 1963. A auditoria vincula o SHA-256 do registro versionado. A massa de 306 kg pertence ao campo `Mass` da linha S00527; 1.176 kg consta em `TotMass` na mesma linha. Os zeros S00528 e S00529 não são pesagens de massa nula. O total não demonstra inventário fechado dos três NORAD numa época comum.

## Resultado estrutural, sem premissas novas

Com vetor físico `(m_527, m_528, m_529, X)`, o catálogo sozinho fornece **zero** equações de massa quantitativas diretamente ativáveis para essa partição: posto 0/4, nulidade 4. Isso **não** significa inexistência de dados documentais; significa ausência de equação instrumental de inventário naquela parametrização.

Somente como cenário, assumir um inventário fechado e uma época/reconciliação válida forneceria a linha `[1,1,1,1]`, posto 1/4 e nulidade 3. Acrescentar medidas independentes de duas massas na mesma época produz posto 3/4. Acrescentar três massas independentes e a soma válida produz posto 4/4. As medidas são contrafactuais, não registros recuperados.

Mesmo observando exatamente `B_j=Cd_j*A_j/m_j`, não se identifica `m_j` sem informação externa sobre `Cd_j*A_j`. A ferramenta fornece uma testemunha racional: uma redistribuição não nula de massa entre 527 e 528 preserva o total e os três valores `B_j` quando `Cd*A` acompanha a redistribuição. Ainda pode persistir o gauge da amplitude de densidade atmosférica, independentemente dessas massas.

## Condições para promover uma restrição

Antes de usar qualquer total em posterior, reentrada ou fragmentação, recuperar: (i) documento físico identificando quais componentes compõem o total e sua época; (ii) inventário fechado ou limites justificáveis de perdas `L`, fragmentos `X` e erro `epsilon`; (iii) correspondência material entre Agena, OPS 0180 e 527/528/529; (iv) medidas ou limitações independentes de massa/área/Cd com unidades e incertezas; (v) hipótese de seleção e likelihood com família documental não duplicada.

**Status:** `CONNECTED_PENDING_CALIBRATION`. `active_constraint=false`; `historical_mcmc=NOT_RUN`; `delta_domain=NOT_EVALUABLE`. O desenho não corrige por si o desacordo de RAAN nem fornece hora ou lugar de reentrada do 528. A solução de posto não escolhe prior nem elimina ambiguidades de modelos físicos alternativos.

Reproduzir no SHA exato:

```sh
python3 -m unittest discover -s tests -p test_mass_identifiability_C241.py -v
python3 tools/mass_identifiability_C241.py
```

Relações: [issue privada Cervo #2](https://github.com/franklinbaldo/cervo/issues/2), [PR candidata #634](https://github.com/franklinbaldo/conde-incident/pull/634) e [PR de integração #641](https://github.com/franklinbaldo/conde-incident/pull/641). Este documento é fatia independente, não autorização para integrar essas PRs antigas.
