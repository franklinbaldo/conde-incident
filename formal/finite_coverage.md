# 🐙 Prova da fronteira de cobertura de grades finitas (issue #15)

O módulo [`FiniteCoverage.lean`](Conde1963/FiniteCoverage.lean) torna
**explícita** a obrigação de exaustividade que faltava entre uma amostra de
parâmetros e a conclusão sobre o domínio físico completo. Um filtro booleano
deve primeiro corresponder ao predicado `AlternativeAllowed` **em cada
ponto efetivamente examinado**. Isso prova que um ponto sobrevivente é um
testemunho de domínio não vazio, mas um resultado vazio da grade **não**
demonstra que a união das fontes RAAN seja inviável.

O teorema `empty_passing_implies_empty_domain_with_coverage` exige ainda
`DomainCoverage`: para **cada** estado globalmente admissível, é preciso
provar que ele aparece na grade. Para domínios orbitais contínuos, não se
pressupõe que tal prova exista para uma lista finita; um integrador com
envelopes intervalares verificados pode exigir outra forma de certificado.
`empty_sample_does_not_eliminate_unseen_branch` fornece uma contraprova
sintética de que uma grade perfeitamente correta pode perder um sobrevivente.

`exhaustive_right_screen_licenses_left_exclusion` conecta essa exigência
ao resultado de `ScenarioEnclosures.lean`: uma conclusão favorável em
apenas uma órbita RAAN **não** decide a união enquanto a outra não tiver
sido excluída com cobertura global. Também requer prova de impacto e de
exclusão na órbita restante; nenhuma foi fornecida nesta rodada.

O contrato de handoff `finite_coverage_interface` para 🦫 Castor
registra as obrigações e permanece com `null` para resultado, filtro
numérico e local, e `false` para provas de cobertura, custódia e holdout.
O CI executa `lake build`, auditoria de `#print axioms` e testes
de invariantes JSON.

**Linhagem reaproveitada, sem nova inspeção de fac-símile:** C25#1 (L118)
e C179#1 (L839) descrevem material orbital secundário. Os valores RAAN
284,1520° e 198,5261° seguem conflitantes, sem TLE primário autenticado.
C131#1 (L502) e C197#1 (L905) são a *mesma* publicação primária:
NASA/Goddard, *Satellite Situation Report*, 15/11/1963, p. 8,
[NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf).
Ela registra um dia catalogado, não hora/local físico. A matriz pinada
está em `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`,
Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7`,
241 ocorrências e colisões C44–C46 preservadas.
O ZIP histórico `Evidence.lean` 154/151 e hashes independentes
permanecem ausentes (`IMPORT_NOT_RUN`).

Reproduzir no HEAD da PR #17:

```sh
cd formal
lake update && lake build
lake env lean Conde1963/AxiomAudit.lean
python3 -m unittest discover -s tests -v
```

Nenhum desses comandos valida um impacto ou recupera observação terminal.
