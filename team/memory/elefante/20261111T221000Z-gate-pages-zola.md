---
type: AgentMemory
title: "Gate Pages adaptado ao Zola e laboratório React"
description: "O gate legado exigia Vite na raiz; agora comprova caminhos Zola, histórias, CSS e laboratório, sem alegar deploy."
agent: elefante
timestamp: "2026-11-11T22:10:00Z"
tags: [conde, pages, zola, auditoria, integracao]
---

# Retomada

**Achado verificado no código:** a [PR #7](https://github.com/franklinbaldo/conde-incident/pull/7) exigia `<div id="root">` e bundle `/conde-incident/assets/*.js` na página inicial; isso conflita com a migração já implementada na [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3), cujo Zola 0.22.1 gera a raiz e o Caderno, enquanto Vite fica em `/conde-incident/lab/`. Conferidos `templates/base.html`, `templates/index.html`, `templates/section.html`, `scripts/check-site.mjs` no HEAD `c84cce85` da #3. A revisão independente do Gavião em #3 é favorável à fatia, mas ressalva reconciliação com #1 e ausência de deployment.

**Mudança desta rodada na #7:** `scripts/check-pages-release.mjs` agora confere homepage Zola com links de histórias/laboratório/CSS, listagem com capítulo datado, laboratório React isolado e CSS público; a suíte inclui contraprovas para cada erro de URL/conteúdo. `research/PUBLICATION_AUDIT.md` explica o contrato. SHA antes desta memória: `00889431231709f9ef304af0c5dfa1c8bcb4504c`. CI do SHA final deve ser lido no GitHub Actions; teste ainda não comprovado por esta nota.

**Fonte e grau:** código de PRs consultado diretamente; documentação histórica C01–C238 lida a partir do HEAD da #1, sem atribuir nova observação ao FBIS, NASA ou satélites. O C197 permanece com divergência de localizador indicada pelo Gavião. Tentativas de obter configuração Pages e deploy pelas APIs disponíveis retornaram acesso não permitido ou URL inacessível, portanto status da publicação **NOT_VERIFIED**, sem alegar 404 confirmado. Nenhum contato externo, publicação ou merge.

**Próxima pergunta:** o Gavião valida a #7 no novo SHA? A #1 será corrigida e revisada globalmente para permitir conciliar com #3? Depois do merge, conferir `build_type=workflow`, run push/main, deployment exato e as quatro superfícies HTTPS, sem usar CI de build como prova de publicação.
