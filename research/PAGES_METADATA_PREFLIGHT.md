# GitHub Pages: pré-verificação de metadados (somente leitura)

**Responsável:** 🐘 Elefante. **Issue:** #6. **Estado:** ferramenta operacional de auditoria, **não** comprovação de publicação.

A PR #3 mantém seu fluxo editorial em draft, com dependência de reconciliação das seções Evidências/Caderno da PR #1 e a decisão de SSG Rust da #22. Na `main`, a ausência de um workflow Pages implica que **nenhuma publicação pode ser declarada verificada**. Um build CI bem-sucedido não é um deployment.

Este estágio **independente do gerador de sites** acrescenta `scripts/pages-metadata-preflight.mjs`. É propositalmente menor que a cadeia antiga de PRs #7 → #33 → #46 → #49 → #52 → #55, para permitir sua integração sem introduzir Zola e sem prometer que o conteúdo está publicado. Quando a nova implementação de Pages estiver pronta, reaproveitar este gate de metadados e conservar os testes adversariais de conteúdo da cadeia existente, evitando dois verificadores finais contraditórios.

## Uso (sob demanda; nenhuma escrita)

```sh
GITHUB_TOKEN="${GITHUB_TOKEN}" node scripts/pages-metadata-preflight.mjs <SHA-40-hex-de-main>
node --test scripts/pages-metadata-preflight.test.mjs
```

O token é fornecido por secret de ambiente, nunca versionado. A ferramenta faz somente solicitações HTTP GET à API oficial do GitHub, sem acionar workflows, configurar Pages ou publicar nada.

Para emitir `METADATA_ONLY_SITE_NOT_VERIFIED`, exige conjuntamente:

1. `has_pages=true`, Pages com `build_type=workflow` e URL canônica de projeto;
2. SHA literal da `main` igual ao SHA auditado;
3. **último** run de `Publish Conde site` por `push` na `main`, no SHA exato e `completed/success`;
4. **último** deployment de `github-pages` no SHA exato, com último status `success`;
5. releitura da `main` no final da inspeção, ainda no mesmo SHA.

Qualquer resultado ausente, erro de API, run mais recente falho, publicação antiga, configuração legada ou troca de SHA resulta em `NOT_VERIFIED` (exit code 1). O resultado favorável de metadados **não significa site publicado** e jamais deve aparecer como `PUBLISHED` ou `VERIFIED`: ainda falta provar via HTTPS o HTML final, os capítulos Markdown, as rotas Evidências/Caderno, CSS/JS e a integridade do conteúdo servido. Essa verificação E2E depende da integração editorial e de deployment real posterior.

**Limite científico:** nem deployment real nem CI verde verificam, por si, a autenticidade de relatos de 1963, órbita ou impacto em Conde. O vínculo documental e os testes Lean, físicos e holdout continuam separados.
