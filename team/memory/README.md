---
type: Guide
title: Memória operacional OKF do time Conde
description: Continuidade de contexto por agente, com referência histórica ao IES sem importar fatos de outro projeto.
---

# Memórias do time Conde

Este time reutiliza o **método**, não os fatos, de memória operacional usado em [franklinbaldo/ies](https://github.com/franklinbaldo/ies/tree/main/team/memories). Os oito agentes (elefante, raposa, coruja, tartaruga, gaviao, polvo, castor e texugo) já atuaram no IES. Suas [fichas antigas](https://github.com/franklinbaldo/ies/tree/main/team) e suas [memórias históricas](https://github.com/franklinbaldo/ies/tree/main/team/memories) continuam consultáveis **quando relevantes** para método, decisões e experiência do agente. Não duplicar o acervo, nem supor que uma decisão técnica do IES vale no Conde. A identidade funcional aqui é definida pela ficha local `team/<agente>.md`, não pela antiga.

## Início de cada rodada

1. Ler integralmente `AGENTS.md` e a própria `team/<agente>.md` da `main` do Conde.
2. Ler as memórias fixadas (`memorias_fixadas`, se houver) e até cinco memórias **mais recentes** de `team/memory/<agente>/`, em ordem decrescente do timestamp; não reler duplicadas.
3. Consultar issues, PRs, código e matriz cumulativa **atuais** antes de tomar decisões. Memórias não substituem esses registros.
4. Buscar memórias antigas do IES apenas se houver uma dúvida concreta de continuidade operacional, citando URL exata. Não copiar nem transpor sem verificação uma alegação factual, científica ou técnica.
5. Reter a distinção entre evidência de 1963, inferência quantitativa, hipótese e reflexão pessoal.

## Encerramento de cada rodada

Criar **uma** memória curta e durável em `team/memory/<agente>/YYYYMMDDTHHMMSSZ-assunto.md`. Não criar arquivos vazios para inicializar pastas. A memória inclui:
- o que mudou, com issue/PR, commit SHA e fonte exata;
- o que foi efetivamente verificado (testes, CI, autenticidade documental) e o que ficou `NOT_RUN` ou inconclusivo;
- tentativas negativas e limites da conclusão, inclusive dependência de fontes;
- próxima dúvida e ponto de retomada.

Frontmatter OKF:

```yaml
---
type: AgentMemory
title: "Título pesquisável"
description: "Resumo breve do que lembrar"
agent: elefante
timestamp: "2026-11-11T19:00:00Z"
tags: [conde, integracao]
---
```

A hora acima é **exemplo**, não um fato registrado. O campo `agent` corresponde ao diretório. Se não houve mudança, registrar o bloqueio e a pergunta real, sem inventar sucesso. Notas de conversa, preferências e inspiração podem ser lembradas, mas são explicitamente separadas de evidências científicas.

## Fixação e pesquisa

Opcionalmente, cada ficha pode trazer `memorias_fixadas` no frontmatter como lista de caminhos locais; não é preciso criar essa lista quando vazia. Preferir links permanentes a SHA/PR, títulos pesquisáveis e busca sob demanda. Consultar [o guia do IES](https://github.com/franklinbaldo/ies/blob/main/team/memories/README.md) como antecedente metodológico, sem depender da disponibilidade desse repositório para operar o Conde.

## Isolamento

Memórias novas ficam somente no Conde. Não alterar memórias do IES nem o blog pessoal. Não promover informação herdada a evidência independente de satélite, queda ou testemunho. Respeitar ownership, revisões, PRs e os gates de `AGENTS.md`. Em especial, comentário de outro agente não é revisão independente. A memória operacional não integra PR automaticamente.
