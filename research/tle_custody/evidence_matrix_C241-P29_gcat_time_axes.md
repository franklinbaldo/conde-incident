---
type: Guide
title: "C241-P29: silêncio da carga útil não é desintegração orbital do 527"
description: "Reconciliação por coluna GCAT dos eixos de operação/transmissão e decaimento físico de 527/528/529 com snapshots completos, auditor e testes de mutação."
---

# C241-P29 · Dois relógios no registro 527

**Resultado:** o [psatcat do GCAT](https://planet4589.org/space/gcat/tsv/cat/psatcat.tsv) registra **18 de janeiro de 1963** em `TLast`, `TOp` e `TDate` para `S00527 / 1963-003A`. A [documentação desses campos](https://planet4589.org/space/gcat/web/cat/pcols.html) define respectivamente última atividade conhecida, fim das operações regulares e fim das transmissões/contatos. **Nenhum é a data de queda ou reentrada**.

O [currentcat](https://planet4589.org/space/gcat/tsv/derived/currentcat.tsv) da mesma versão lista `S00527` com `DDate = 1969 Jan 9 1200?` e estado `Reentered attached to A00324 Agena B 2313`. O sufixo `?` torna a hora explicitamente incerta. Os `S00528 / 1963-003B` e `S00529 / 1963-003C` aparecem como componentes com `DDate = 1963 Nov 8` e `1963 Dec 31` **sem horas**. O campo `SDate` de 16 de janeiro de 1963 nas três linhas é fase de separação/início de estado, não data observada por sensor.

A genealogia impressa no `currentcat` também importa: `527` tem pai `A00324`, enquanto os componentes `528` e `529` referem `S00527`. Isto **não** certifica, por si só, a identidade de uma peça de debris, o instante de fragmentação ou uma medição independente. Uma consulta à família GCAT não representa três instrumentos. São distinções necessárias antes de usar o 527 como controle sobrevivente posterior a 8/11/1963, tal como pedido na [issue #396](https://github.com/franklinbaldo/conde-incident/issues/396).

## Custódia e falsificação

O [ledger tipado](gcat_time_axes_527_529_C241-P29.json) preserva o cabeçalho e linhas TSV exatas para `527`, `528`, `529`, além dos SHA-256 e comprimentos dos **dois arquivos completos** recuperados em 14/11/2026 UTC. O [auditor](../../tools/audit_gcat_time_axes_c241_p29.py) refaz a distinção por nomes de colunas e verifica pai, identificadores, datas, estado e ausência de pretensa precisão instrumental. Testes negativos alteram a linha **e recalculam seu hash** para demonstrar que a semântica, e não apenas o digest, é verificada. O comando abaixo aceita opcionalmente o corpus integral local para replay independente por hash e bytes:

```bash
python3 tools/audit_gcat_time_axes_c241_p29.py --check --replay-source-dir /caminho/para/tsvs
python3 -m unittest discover -s tests -p 'test_gcat_time_axes_c241_p29.py' -v
python3 -O -m unittest discover -s tests -p 'test_gcat_time_axes_c241_p29.py' -v
```

**Limite:** este é um catálogo secundário mutável. O conteúdo recortado e seus hashes são evidência de uma captura; o CI padrão reconstrói a interpretação do recorte, **não rebaixa automaticamente** uma atualização posterior do servidor a erro e **não recupera** sensor, estação, época UTC calibrada, frame ou covariância. `Δnovas_custódias = +2`; `Δligações_científicas_ativas = 0`; `ΔΘ = 0`. Nenhuma hora/local de queda do 528 foi inferida. Não adicionar teorema Lean orbital sem observação admissível.
