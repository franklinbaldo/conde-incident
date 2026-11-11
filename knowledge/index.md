# Catalogo OKF do caso Conde

Esta e a fonte de **catalogacao atomica das informacoes** do projeto, nao uma substituicao dos documentos originais ou da matriz cumulativa. Os registros de memorias `team/memory/<animal>/` continuam validos e devem apontar para a `Rodada` respectiva. Cada nova rodada registra **todas** as novidades, verificacoes, refutacoes, resultados negativos, contradicoes, decisoes e perguntas como conceitos tipados, mesmo quando nada foi confirmado.

## Regra de catalogacao por rodada

1. Criar `Rodada` no inicio do trabalho e relacionar nela cada novo conceito criado/alterado. Um resultado inconclusivo tambem deve ser catalogado.
2. Preservar `source_url`, identificador/versao de origem e grau `verification`. So usar `VERIFIED_REPO` para arquivos, metadados ou textos efetivamente lidos; `REPORTED_REPO` para resultados apenas declarados em PR; `HYPOTHESIS` e `NOT_RUN` quando aplicaveis.
3. Manter citacao/extrato, afirmacao, evidencia e dependencia em **registros distintos**. FBIS e sua republicacao nao sao duas testemunhas; NASA e catalogo derivado nao sao dois sensores.
4. `ResultadoNegativo` preserva o **limite da busca**, e ausencia nao observada nunca vira resultado negativo comprovado.
5. Identidades `C001...` sao globais para a matriz cientifica; uma colisao vai para `Conflito`, sem renumeracao automatica. Nao editar/sobrescrever a matriz de outras PRs.
6. Ao encerrar, vincular a memoria OKF da sessao, fontes, SHAs, testes PASS/FAIL/NOT_RUN, limitacoes e proxima duvida. Sinalizar o que mudou desde o capitulo anterior.

## Tipologia inicial

| Tipo | Unidade catalogada | Limite de interpretacao |
|---|---|---|
| Fonte | Objeto documental ou conjunto de dados, com proveniencia e custodia; nao implica autenticacao do conteudo. | Nao converter classificacao em prova independente |
| Extrato | Transcricao ou recorte literal de uma fonte localizada; nao cria observacao independente. | Nao converter classificacao em prova independente |
| Afirmacao | Proposicao atomica verificavel, separada de prova e de inferencia. | Nao converter classificacao em prova independente |
| Evidencia | Relacao explicita de suporte, refutacao ou contexto entre fonte e afirmacao. | Nao converter classificacao em prova independente |
| Dependencia | Relacao genealogica entre relatos, arquivos, calculos ou documentos. | Nao converter classificacao em prova independente |
| Observacao | Fato visto em arquivo, codigo ou execucao, com localizador e limite da observacao. | Nao converter classificacao em prova independente |
| Medicao | Valor numerico e unidade, com origem e incerteza documentadas. | Nao converter classificacao em prova independente |
| Modelo | Modelo computacional ou formal e seus pressupostos, distinto de observacao empirica. | Nao converter classificacao em prova independente |
| Hipotese | Proposicao ainda nao demonstrada com teste capaz de refuta-la. | Nao converter classificacao em prova independente |
| Ensaio | Comando reproduzivel e resultados de teste associados a SHA e run, sem forjar PASS. | Nao converter classificacao em prova independente |
| Conflito | Duas proposicoes ou identificacoes incompatíveis mantidas visiveis ate resolucao. | Nao converter classificacao em prova independente |
| ResultadoNegativo | Busca ou teste sem confirmacao, limitado ao corpus e procedimento realmente consultados. | Nao converter classificacao em prova independente |
| Decisao | Decisao operacional ou epistemica, responsavel e justificativa; nao e evidencia. | Nao converter classificacao em prova independente |
| Capitulo | Unidade editorial com referencias auditaveis e delta desde o anterior. | Nao converter classificacao em prova independente |
| Questao | Lacuna rastreavel, prova faltante e proximo teste falsificavel. | Nao converter classificacao em prova independente |
| Artefato | Codigo, matriz, relatorio, dataset ou commit com identidade versionada. | Nao converter classificacao em prova independente |
| Rodada | Registro totalizante de uma sessao: cada nova informacao deve ter um conceito tipado vinculado. | Nao converter classificacao em prova independente |

As specs sao criadas pela ferramenta **`franklinbaldo/okf-parser` v0.48.2** usando `init --infer-schema --write` e depois enriquecidas com regras de campo obrigatorio, sem apagar o scaffold original do parser. Os SQL sao **declaracoes fisicas iniciais inferidas de exemplos**; nao substituem critica das fontes ou controle de integridade historica. O CI exige `check --require-spec '.okf/specs/{slug}.md' --normative-spec` e gera um JSON Schema para inspeção.

## Inicializacao e verificacao

```bash
uvx --from okf-parser==0.48.2 okf-parser init knowledge --spec-template '.okf/specs/{slug}.md' --infer-schema --write
node scripts/bootstrap-okf-specs.mjs
uvx --from okf-parser==0.48.2 okf-parser check knowledge --require-spec '.okf/specs/{slug}.md' --normative-spec
uvx --from okf-parser==0.48.2 okf-parser schema knowledge --spec-template '.okf/specs/{slug}.md' --format json
node --test tests/okfCatalog.test.mjs
```

## Memorias e matriz legadas

A matriz C001-C238 esta por ora na [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1). Auditar IDs por SHA antes de converter registros em conceitos, em vez de copiar 238 linhas sem proveniencia rastreada. As memórias antigas de agentes nao sao automaticamente promovidas a evidencias; cada entrada precisa de fonte e grau de verificacao.

## Primeira rodada

[Inventario de 11/11/2026](records/rodada-20261111-bootstrap.md)
