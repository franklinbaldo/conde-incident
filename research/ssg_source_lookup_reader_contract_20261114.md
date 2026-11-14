---
type: Guide
title: '🦎 SSG: leitura verificada do índice reverso de fontes'
description: 'Contrato de leitura HTTPS de dados documentais endereçados por digest e detecção de snapshots mistos, sem promoção epistemológica.'
---

# Leitura verificável do índice reverso do Conde

O exportador `tools/export_ssg_source_lookup.py` publica `data/conde-source-lookup-manifest.json` e um shard nomeado por SHA-256. O leitor `scripts/ssg-source-lookup-loader.mjs` entrega à interface o índice **somente depois** de verificar os bytes. Essa camada não substitui as fontes primárias nem a auditoria independente `scripts/verify-ssg-source-lookup.mjs` em CI.

1. Buscar o manifesto mutável com `cache: no-store`, exigir versão v1, dependências SHA-256 e `source_index.path` estritamente dentro de `public/data/conde-source-lookup/part-<sha256>.json`, tamanho de 1 a 20.000 bytes.
2. Buscar o manifesto da matriz de evidências também com `cache: no-store`. Confrontar SHA-256 dos **bytes integrais** com `inputs_sha256['public/data/conde-evidence-index-manifest.json']`; assim um ponteiro de geração A não é silenciosamente composto com a matriz de geração B.
3. Buscar shard de nome imutável (`cache: force-cache`), exigir tamanho e SHA-256 de seus bytes, versão v1, igualdade dos identificadores de matriz, dos digests das fontes canônicas e contagem exata de referências/ocorrências.
4. Diante de falha de rede, schema, mixed snapshot, SHA, byte count, origem insegura ou estado epistemológico proibido, lançar `SourceLookupIntegrityError` com código identificável. **Nunca** cair em um shard em cache não verificado, exibir contagens falsas ou inferir independência a partir de ausência de aresta.

Uso pelo frontend, quando a Raposa integrar a jornada: `loadCondeSourceLookup({baseUrl: 'https://franklinbaldo.github.io/conde-incident/'})`. O consumidor deve mostrar indisponibilidade e opção de atualizar, sem misturar o dado comprometido com a apresentação. O teste usa `fetcher` e `hashBytes` injetados; no navegador de produção, SHA-256 depende de WebCrypto (`crypto.subtle`). A função não emite alegações históricas nem acessa servidor de aplicação.

## Fronteiras e custo

O cache pode ficar com o **shard antigo**, pois o nome inclui seu digest. Uma página com manifesto antigo em cache e matriz nova **falha fechada** em vez de combinar gerações; não faz retry nem escolhe automaticamente outra fonte. A leitura fecha a consistência com o manifesto da matriz, **não** autentica o servidor HTTPS contra comprometimento, nem comprova que a fonte original era verdadeira: um atacante que altere a autoridade de publicação e recalcule todos os digests ainda exige verificação independente no CI. A bibliografia editorial possui 15 fontes, 9 famílias, 29 vínculos curados, 28 ocorrências com ficha, 213 lacunas; não são 15 medições independentes. O item pós-matriz permanece sem linha nem observação física certificada. Meteorologia não foi reaberta.

O único acréscimo gerado em execução é código estático; não altera bytes dos JSONs, entradas, IDs ou SHA históricos. Verificação determinística: `python3 tools/export_ssg_source_lookup.py --check`, `node scripts/verify-ssg-source-lookup.mjs`, `node --test tests/ssg-source-lookup-loader.test.mjs`. O workflow `ssg-evidence-index.yml` passa a exigir essas operações no SHA exato da PR.
