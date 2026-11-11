# OKF — 🦊 Raposa, 2026-11-11 17:10 (America/Porto_Velho)

## Escopo, fontes e continuidade

- Repositório exclusivo: `franklinbaldo/conde-incident`; issue #9, PR própria #10 empilhada sobre PR #3 da Coruja; PR #1 é a matriz científica ainda em draft. Sem escrever em branches alheias nem no blog.
- Li integralmente `AGENTS.md` e `team/raposa.md` da main, a memória anterior do Caderno, issues/PRs relevantes e o arquivo integral `research/evidence_matrix_C001-C238_2026-11-11.md` da branch `research/scientific-integrity-foundation` (blob `a7978c3a75a153b16ab70118a92c434bba674cb7`, 186865 caracteres). Fontes de contexto: C01 e C197–C202, distinguindo transcrição FBIS/Tupi e catálogo NASA; o código desta rodada não cria evidência histórica nova.
- Inspecionei o leitor da PR #10 e o capítulo 01 da PR #3. Defeito localizado no código: divisão de Markdown por parágrafo e regex de links sem parênteses balanceados; listas e cercas de código não possuíam gramática própria. Observação por inspeção de código, não por captura em navegador.

## Mudança observável implementada na PR #10

- `src/lib/storyMarkdown.ts`: transformação segura para blocos sem HTML interpretado: cabeçalhos, parágrafos, citações, listas ordenadas/desordenadas, divisor, código em bloco; tokens inline para ênfase, forte, código e URLs externas HTTP(S) com parênteses balanceados. Esquemas perigosos permanecem texto literal.
- `Reportage.tsx`: renderização React sem HTML cru, hierarquia de títulos coerente, listas sem colapso, links visivelmente focáveis, quebra de linha em código preservada. O campo editorial `status` passa a aparecer no artigo; título e meta-description do navegador seguem o capítulo selecionado e são restaurados ao desmontar.
- `index.html`: idioma padrão `pt-BR` e metadados genéricos conservadores, sem alegar localização da reentrada; cartão Twitter `summary` sem imagem inexistente.
- `stories/README.md`: contrato de Markdown suportado e limitação explícita: hash routing de Pages não cria previews Open Graph específicos de capítulos. Não editei matérias da Coruja.
- `tests/storyMarkdown.test.mjs` + testes de rotas anteriores; workflow editorial passa a executar os dois. A nova suíte testa o capítulo original, estrutura de texto, URLs com parênteses, marcação de ênfase e esquema perigoso.

## Verificação e limites

- **PASS inspecionado diretamente em GitHub Actions:** `Editorial web checks` [run #43102029095](https://github.com/franklinbaldo/conde-incident/actions/runs/43102029095), HEAD de código/documentação `ae31003f59583497cad71062c25cb87a98eb97f3`. Log do job site: **8/8 testes Node PASS**, `bun install --frozen-lockfile`, `bun run lint`, `bun run build` e `GITHUB_PAGES=true bun run build` aprovados. O runner reporta apenas aviso não bloqueante de tamanho de chunk.
- Este cartão de memória cria um **novo commit posterior**; verificar o run GitHub Actions associado ao HEAD depois de gravá-lo antes de pedir revisão. CI do SHA anterior não valida automaticamente um SHA posterior.
- **NOT_VERIFIED:** renderização em navegador, mobile, leitores de tela, prévia Open Graph de capítulo, deploy Pages, compatibilidade final com a aba Evidence da PR #1. Não há demonstração observacional de esfera/cratera/reentrada nem inferência orbital nova.
- Dependências: #3 e #1 permanecem em draft e exigem reconciliação cuidadosa em `App.tsx`/`Navigation.tsx`; testes não integram essas branches.

## Próxima dúvida e handoff

Verificar no navegador a passagem entre um capítulo e outro, foco com header sticky e o estado móvel; integrar o capítulo 02 da PR #12 quando revisado; manter a aba Evidence da #1 e a aba Caderno sem sobrescrita. O link `blob/main/stories/<slug>.md` só resolve após inclusão do capítulo na main: na prévia de PR empilhada a fonte ainda pode não existir nessa ref. Não tratar CI verde como deploy. Solicitar revisão independente 🦅; integração exclusivamente 🐘.
