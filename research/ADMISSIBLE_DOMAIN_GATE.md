# Gate de domínio admissível: limites do que o código demonstra

Esta fatia implementa um controle algébrico para a etapa **domínio não vazio e reduzido** do fluxo científico proposto na [PR #28](https://github.com/franklinbaldo/conde-incident/pull/28). A [matriz cumulativa C01–C238](https://github.com/franklinbaldo/conde-incident/pull/1), a custódia TLE [#14](https://github.com/franklinbaldo/conde-incident/pull/14), o núcleo Lean [#17](https://github.com/franklinbaldo/conde-incident/pull/17) e o holdout [#20](https://github.com/franklinbaldo/conde-incident/pull/20) são **dependências empíricas externas**. Não são presumidas como integradas, verificadas ou verdadeiras.

`node scripts/audit-admissible-domain.mjs <arquivo.json>` audita a interseção determinística de intervalos fechados, declarados como strings decimais, com aritmética racional exata. Produz `REDUCED`, `UNCHANGED` ou `CONTRADICTORY`; contradição sai com código 2, entrada inválida com código 1. Cada restrição deve registrar ID de evidência, ocorrência, URL, cadeia de independência, grau declarado de verificação, referência formal Lean, status `NOT_RUN` ou `CLAIMED`, e premissa. Repetir um ID ou URL sob grupos de independência diferentes é proibido.

Exemplo **inteiramente sintético**, sem coordenada, órbita nem dado histórico:

```json
{
  "schema": "conde.admissible-domain/v1",
  "kind": "synthetic",
  "parameters": [{"name":"x","unit":"synthetic","initial":{"min":"0","max":"10"}}],
  "restrictions": [{
    "parameter":"x","interval":{"min":"2","max":"8"},
    "trace":{"evidence_id":"SYN1","occurrence":"synthetic fixture",
      "source_uri":"synthetic:test","independence_group":"synthetic-group",
      "verification":"synthetic"},
    "formal":{"lean_ref":"Synthetic.conditional","status":"NOT_RUN"},
    "assumption":"example only"
  }]
}
```

Para uma declaração documental, usar `kind=declared-evidence` com ID `Cnnn`, URI HTTPS, ocorrência e grau de verificação. **O programa não consulta a fonte, não consulta a matriz, não compila Lean, não prova a premissa, não roda solver nem holdout.** Portanto a saída é `DECLARED_NOT_AUDITED`, mesmo quando o autor atribui `directly_inspected`. O campo `independent_chains_declared` é apenas a contagem dos rótulos, não independência científica comprovada. `CLAIMED` não é `PASS`; o checker recusa qualquer tentativa de apresentar `formal.status=PASS` sem execução independente.

Não converter uma interseção de **caixas de parâmetros** em conclusão orbital: relações correlacionadas, geometria não intervalar, unidades distintas, restrições de desigualdades abertas e dinâmicas acopladas não são tratadas. Não existe saída que alegue lugar ou hora de reentrada, impacto em solo ou probabilidade. Mesmo domínio não vazio e menor pode não representar uma trajetória fisicamente viável. O teste só estabelece que as restrições *declaradas*, tomadas como premissas, reduzem ou contradizem os intervalos.

CI: `node --test tests/admissible-domain.test.mjs` cobre 15 contraprovas, inclusive contradição, extensão proibida, precisão decimal, cadeia duplicada e falso status Lean. Para integrar, exigir CI GitHub Actions verde **no SHA final**, revisão independente do Gavião e posterior confronto com dados reais, Lean executado e holdouts antes de alegar um resultado científico.