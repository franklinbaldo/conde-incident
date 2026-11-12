# Publicação Conde: prova depois do deploy

Um build web verde **não** prova publicação. O verificador `scripts/check-pages-release.mjs` realiza somente leituras e encerra com `PASS` ou `NOT_VERIFIED` (código de saída 1).

## Requisito de aceite

Os quatro sinais devem concordar no mesmo SHA completo da `main`: (1) configuração real de GitHub Pages com `build_type=workflow`, ou seja, fonte GitHub Actions; (2) run `Publish Conde site` por `push` em `main`, concluído com `success`; (3) deployment no ambiente `github-pages` e último status `success`; (4) URL pública `https://franklinbaldo.github.io/conde-incident/` com HTTP 200, página inicial **Zola** com caminhos `/conde-incident/stories/`, `/conde-incident/lab/` e `/conde-incident/css/site.css`, listagem Zola com link de capítulo datado **efetivamente acessível por HTTPS**, HTML de artigo completo e ligação ao Markdown-fonte, folha de estilo do Zola disponível e laboratório React/Vite em `/conde-incident/lab/` com bundle em `/conde-incident/lab/assets/`. Nenhum sinal é substituído por texto de PR, CI de build ou pela existência de YAML.

Com o token de leitura do Actions, executar:

```bash
TARGET_SHA=<SHA-40-hex-da-main> UPSTREAM_CONCLUSION=success GITHUB_REPOSITORY=franklinbaldo/conde-incident node scripts/check-pages-release.mjs
node --test scripts/check-pages-release.test.mjs
```

O workflow `Audit Conde Pages release` testa contraprovas em PR e audita a publicação após conclusão de `Publish Conde site` em `main`, sem acionar deploy, escrever configurações ou modificar o blog pessoal. Falha de auditoria sinaliza publicação não verificada, não reverte deploy eventualmente realizado. O site Zola, a listagem de histórias, CSS e o laboratório React retornando HTML/asset, junto aos registros de deploy com SHA, são evidências de publicação, **não atestação criptográfica dos bytes**. Não se pode deduzir o SHA do código apenas olhando a página HTTPS: a concordância depende dos registros oficiais de deploy. Esta auditoria não garante frescor por hash do conteúdo.

**Dependências:** PR #1 traz a pesquisa e CI científico; PR #3 traz Caderno, artigo e Pages. A #3 foi convertida para Zola e recebeu parecer independente LGTM técnico-editorial no HEAD `c84cce85` (Gavião, 11/11/2026), mas não é prova de deploy; a #1 ainda exige revisão global e correção de C197. Ambas devem ser reconciliadas antes da publicação. A fonte Pages ainda precisa ser confirmada no Settings → Pages; `pages.yml` em draft não basta. Após review Gavião e CI verde no HEAD, integrar #1 antes da #3, reconciliando App.tsx e Navigation.tsx para preservar abas e Caderno. Cada capítulo deve expor novidade documental verificável, além dos limites.

**Fontes verificáveis:** [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3), [fluxo GitHub Pages documentado](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [API de Pages](https://docs.github.com/en/rest/pages/pages), [matriz C01–C238 no head da PR #1](https://github.com/franklinbaldo/conde-incident/blob/research/scientific-integrity-foundation/research/evidence_matrix_C001-C238_2026-11-11.md).

**Limite científico:** verificação de deploy não verifica independência Tupi/FBIS, autenticidade da esfera, hora/local de reentrada nem validade orbital. Para dados, ler os originais e a matriz. Nenhuma nova observação histórica é afirmada.

## Migração de contrato, 11/11/2026

A versão inicial desta PR procurava `<div id="root">` e bundle Vite **na raiz**. Isso era um falso negativo após a decisão de usar Zola. O contrato atualizado exige páginas Zola na raiz e nas histórias, CSS estático e bundle React somente em `/lab/`. Testes de contraprova rejeitam HTML React na raiz, páginas/paths errados e capítulos ausentes. A auditoria permanece somente leitura e **não deve ser tratada como gate de publicação concluída** enquanto #1/#3 não forem integradas e a API Pages/deployment e site real não forem conferidos no HEAD exato.

## Contraprova de capítulo, 11/11/2026

A verificação anterior inspecionava apenas uma URL com data na **listagem**, que poderia apontar para 404 ou texto não publicado. Agora o auditor extrai um `href` canônico de capítulo (mesma origem e base `/conde-incident/`), faz GET do artigo e exige HTTP 200, `<article class="full-story">`, corpo `story-body` e referência ao Markdown-fonte. Há testes negativos de 404, fallback genérico, ausência da fonte, troca de path e origem externa, mais teste positivo para `story.permalink` absoluto do Zola. Isso demonstra apenas **existência da superfície publicada**, não autenticidade de fontes históricas nem integridade criptográfica dos bytes.

## Auditoria integral da coleção editorial (fatia empilhada após #7)

O gate deve seguir **todas** as URLs dos cartões da listagem Zola, e não apenas o primeiro capítulo. Cada cartão precisa ter permalink datado e único sob o domínio e base canônicos. Para cada URL, a auditoria faz GET, confere HTTP 200, corpo `full-story`/`story-body` e a ligação específica para `stories/<slug>.md` no repositório. Uma segunda reportagem 404, uma fonte de Markdown trocada, uma ligação para outro domínio ou um cartão duplicado fazem o resultado ficar `NOT_VERIFIED`. Para impedir uma varredura de rede ilimitada, uma listagem com mais de 100 cartões exige revisão explícita do limite. O teste utiliza HTML sintético para demonstrar falhas de detecção; **não** certifica a procedência histórica de cada reportagem, nem que sua narrativa contém notícia nova. O controle editorial da Coruja e a revisão factual independente do Gavião continuam obrigatórios.


## Contraprova de inventário no commit publicado (12/11/2026)

**Nova condição de publicação:** o auditor consulta somente leitura o endpoint
`GET /repos/franklinbaldo/conde-incident/git/trees/<SHA>/recursive=1`
(formato de consulta efetivo: `?recursive=1`). O GitHub fornece a árvore
do **commit de 40 caracteres** que venceu os gates de run e deployment.
O conjunto de `stories/YYYY-MM-DD-slug.md` precisa coincidir
**exatamente** com os cartões de `/conde-incident/stories/` (não basta
a existência de um capítulo). Árvore truncada, fontes não convencionais,
duplicatas, capítulos ausentes/ocultos e links extras resultam em
`NOT_VERIFIED`. O verificador continua a buscar cada artigo em HTTPS.

O próprio artigo precisa apontar para
`https://github.com/franklinbaldo/conde-incident/blob/<SHA>/stories/<slug>.md`,
e não `blob/main`: a fonte do artigo publicado fica identificável
**mesmo depois que main avançar**. Requer atualização do template da
Coruja na PR #3, ainda **não implementada**; um teste sintético verde
não representa deploy. A exceção explícita é `stories/README.md`, documentação editorial já
presente na PR #3, que não representa capítulo publicável. Se houver outro
Markdown intencionalmente não publicável, ele deve estar fora de `stories/`
ou o contrato deve ser explicitamente revisto com avaliação independente,
nunca ignorado silenciosamente.

**Mudança editorial superveniente:** a PR #22 registra decisão do
proprietário por SSG Rust em lugar de Zola. Este auditor é independente
do executável gerador: exige a estrutura HTML pública estável
`masthead`, `journal`, `story-card`, `full-story`, `story-body`,
stylesheet em `/css/site.css` e laboratório em `/lab/`.
A Coruja precisa preservar ou adaptar esse contrato no HTML SSG
real antes da integração. Referências anteriores a Zola neste
documento descrevem a revisão histórica, não autorização para
publicar a versão Zola revogada.

**Proveniência e independência:** o inventário é metadado primário
do controle de versões lido via GitHub no SHA de `main`; não é
evidência da reentrada de 1963 nem independente do código que produz
o site. As páginas em HTTPS demonstram disponibilização no momento
da auditoria, não autenticidade histórica ou checksum de artefato
buildado. Testes usam somente árvore/HTML artificiais adversariais.
Fonte da política: [AGENTS.md](../AGENTS.md),
[PR #22](https://github.com/franklinbaldo/conde-incident/pull/22)
e [API Git Trees](https://docs.github.com/en/rest/git/trees).

## Contraprova de atualização da publicação (12/11/2026)

O auditor também exige que `GET /repos/{owner}/{repo}/branches/main`
retorne **o mesmo SHA de 40 caracteres** sob auditoria e que o
**deployment mais recente** em `github-pages` (consulta com
`environment=github-pages&per_page=1`) pertença ao mesmo SHA.
Mesmo havendo um deployment antigo verde nesse commit, o mais recente
precisa estar com **último status `success`**, e o run mais recente
de `Publish Conde site` nesse SHA precisa ter `completed/success`.
Um run anterior verde não mascara um run posterior com falha, um
deployment posterior pendente, ou a avanço de `main` sem deploy.

**Independência e incerteza:** as leituras são metadados oficiais do
próprio GitHub (não atestação independente do binário publicado).
A regra conservadora pode declarar `NOT_VERIFIED` durante uma
atualização legítima enquanto `main` avançou e Pages ainda não
concluiu seu próximo deploy. Isso é preferível a declarar publicado
o conteúdo do SHA errado. A árvore de fontes, os artigos HTTP e o
laboratório continuam sujeitos às verificações anteriores; o gate não
confere hashes de bytes HTML nem detecta toda troca maliciosa de
conteúdo sem alteração nos metadados. Não utiliza dados astronômicos
e não afirma reentrada/impacto.

**Documentação da API de controle:**
[Branches](https://docs.github.com/en/rest/branches/branches#get-a-branch),
[Deployments](https://docs.github.com/en/rest/deployments/deployments#list-deployments),
[Deployment statuses](https://docs.github.com/en/rest/deployments/statuses#list-deployment-statuses)
e [Workflow runs](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow).
Teste reproduzível:
`node --test scripts/check-pages-release.test.mjs`.
A fonte Pages via GitHub Actions e o deploy real **seguem NOT_VERIFIED**
até consultas e respostas de produção no `main` integrado.
