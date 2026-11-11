# Caderno de reportagem — Coruja

Cada PR editorial acrescenta **um capítulo Markdown** em `stories/YYYY-MM-DD-slug.md` que explica, em narrativa jornalística envolvente mas rigorosa, o que mudou desde o último capítulo publicado.

## Campos necessários

Front matter YAML simples: `title`, `date` (ISO), `summary`, `chapter`, `author`, `status`. A interface ordena pela data. Não alterar capítulos anteriores silenciosamente: correções relevantes usam errata explicada e PR rastreável.

## Leitura e links permanentes no próprio site

O leitor usa hashes para funcionar também no GitHub Pages estático, sem regras de rewrite: `#/stories` abre o índice e `#/stories/YYYY-MM-DD-slug` abre diretamente o capítulo; `#/tab/map` identifica a aba de mapa. Links inválidos ou para capítulos ainda não integrados devem informar que o conteúdo não foi encontrado, sem inventar conteúdo. Links e histórico do navegador devem permanecer navegáveis com teclado.

A ponte de proveniência aponta para um **snapshot identificado da matriz C001–C238 da PR #1**, ainda não integrada, e não afirma que a aba Evidence esteja publicada. Após combinar as PRs #1 e #3, verificar manualmente a presença de ambas as abas e substituir a ponte por navegação à versão integrada, preservando as fontes originais. Build verde não é prova de deployment.

## Contrato editorial

- Abrir com uma cena ou pergunta real, **sem fabricar diálogos, personagens, atmosferas testemunhadas ou detalhes não documentados**.
- Dizer o que motivou a busca, o que se tentou, qual documento foi consultado e **o que de fato mudou** desde a última publicação.
- Cada afirmação material tem link para fonte, evidência da matriz ou PR/cálculo reproduzível; citar páginas, datas e dependências.
- Distinguir **documento diretamente inspecionado**, **citação indireta**, **inferência**, **hipótese** e **resultado negativo**.
- Se a rodada não tiver avanço substantivo, NÃO publicar texto de enchimento. Registrar investigação no log e aguardar um capítulo com descoberta, correção ou refutação significativa.
- Não contar republicações como corroboração; não anunciar local de queda, percentuais ou horário exato de reentrada sem demonstração.
- Uma PR por capítulo, com `stories/` alterado, título literário e resumo técnico na descrição, revisada pelo 🦅 Gavião e integrada pelo 🐘 Elefante com CI verde.
- Publicação significa merge na main e deploy do próprio site, não alteração do blog externo `franklinbaldo.github.io`. Se não houver deploy configurado, registrar bloqueio claramente.
- A versão em inglês pode ser uma tradução futura; original em português.
