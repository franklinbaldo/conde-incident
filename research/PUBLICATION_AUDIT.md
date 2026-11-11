# Publicação Conde: prova depois do deploy

Um build web verde **não** prova publicação. O verificador `scripts/check-pages-release.mjs` realiza somente leituras e encerra com `PASS` ou `NOT_VERIFIED` (código de saída 1).

## Requisito de aceite

Os quatro sinais devem concordar no mesmo SHA completo da `main`: (1) configuração real de GitHub Pages com `build_type=workflow`, ou seja, fonte GitHub Actions; (2) run `Publish Conde site` por `push` em `main`, concluído com `success`; (3) deployment no ambiente `github-pages` e último status `success`; (4) URL pública `https://franklinbaldo.github.io/conde-incident/` com HTTP 200 e bundle de `/conde-incident/assets/`. Nenhum sinal é substituído por texto de PR, CI de build ou pela existência de YAML.

Com o token de leitura do Actions, executar:

```bash
TARGET_SHA=<SHA-40-hex-da-main> UPSTREAM_CONCLUSION=success GITHUB_REPOSITORY=franklinbaldo/conde-incident node scripts/check-pages-release.mjs
node --test scripts/check-pages-release.test.mjs
```

O workflow `Audit Conde Pages release` testa contraprovas em PR e audita a publicação após conclusão de `Publish Conde site` em `main`, sem acionar deploy, escrever configurações ou modificar o blog pessoal. Falha de auditoria sinaliza publicação não verificada, não reverte deploy eventualmente realizado. O site retornando HTML e os registros de deploy com SHA são evidências de publicação, não atestação criptográfica de bytes.

**Dependências:** PR #1 traz a pesquisa e CI científico; PR #3 traz Caderno, artigo e Pages. São drafts, sem parecer independente registrado quando esta auditoria foi aberta. A fonte Pages ainda precisa ser confirmada no Settings → Pages; `pages.yml` em draft não basta. Após review Gavião e CI verde no HEAD, integrar #1 antes da #3, reconciliando App.tsx e Navigation.tsx para preservar abas e Caderno. Cada capítulo deve expor novidade documental verificável, além dos limites.

**Fontes verificáveis:** [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3), [fluxo GitHub Pages documentado](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [API de Pages](https://docs.github.com/en/rest/pages/pages), [matriz C01–C238 no head da PR #1](https://github.com/franklinbaldo/conde-incident/blob/research/scientific-integrity-foundation/research/evidence_matrix_C001-C238_2026-11-11.md).

**Limite científico:** verificação de deploy não verifica independência Tupi/FBIS, autenticidade da esfera, hora/local de reentrada nem validade orbital. Para dados, ler os originais e a matriz. Nenhuma nova observação histórica é afirmada.
