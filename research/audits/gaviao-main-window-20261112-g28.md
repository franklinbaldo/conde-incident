---
type: Guide
title: "🦅 G28: auditoria retrospectiva de 15 integrações e exceções de tamanho"
description: "Cobertura completa SHA a SHA de G27 até a PR #307, testes adversariais de tamanho e distinções científicas."
---

# G28: retrospectiva de 15 integrações e contraprova de gate

**Janela imutável**: `20240adddaf9df0e703d894bc2a7dba73fc8b855` → `0031f2a894fcbf6b2c59fb2d80d0f31a3d95e099` (12/11/2026, 19h44–20h31, UTC−04). `git rev-list --first-parent` = **15**; DAG completo = **15**, todos squash, sem laterais ou edições diretas. As PRs #291/#307 têm o vínculo verificado via `commits/{sha}/pulls`, embora o assunto do commit não cite a PR. A pesquisa de PRs fechadas sem merge não retornou itens nessa janela, sem inferir ausência absoluta.

## Parecer de cada integração

- [#291](https://github.com/franklinbaldo/conde-incident/pull/291), `a1bd71999`: Caderno 05: fac-símile Última Hora 14/11 demonstra sátira circulante, não testemunha, balão encontrado ou cronologia originária; FBIS 08/11 já contém alegações extraordinárias. CI autor 16/16 SUCCESS; push 16/16 SUCCESS.
- [#292](https://github.com/franklinbaldo/conde-incident/pull/292), `801c9baff`: G27: testes de SHA e epoch do espelho TLE 528 demonstram integridade e limites do checksum, não autenticação instrumental. CI autor 16/16 SUCCESS; push 18/18 SUCCESS.
- [#290](https://github.com/franklinbaldo/conde-incident/pull/290), `892c8166a`: C241-L12: boletim compilado NASA 15/10 lista 3A–3C; NTRS possui versões e páginas divergentes, não fornece observação primária de RAAN. CI autor 17/17 SUCCESS; push 17/17 SUCCESS.
- [#295](https://github.com/franklinbaldo/conde-incident/pull/295), `7f463511a`: C179/C151: duas linhagens documentais conectadas a observáveis físicos inativos; nenhuma covariância ou independência instrumental nova. CI autor 16/16 SUCCESS; push 15/16 SUCCESS; Pages CANCELLED, não verde integral.
- [#293](https://github.com/franklinbaldo/conde-incident/pull/293), `d82e884db`: Recife: metadados NOAA sobre alturas geopotenciais/geométricas sustentam interpretação do perfil IGRA, não transporte calibrado a Conde. CI autor 18/18 SUCCESS; push 16/16 SUCCESS.
- [#297](https://github.com/franklinbaldo/conde-incident/pull/297), `93ab5860e`: CGEO-14: fotos da Vila do Conde têm data/proveniência diversa da alegação de novembro de 1963; não oferecem fronteira geodésica do evento. CI autor 16/16 SUCCESS; push 16/16 SUCCESS.
- [#298](https://github.com/franklinbaldo/conde-incident/pull/298), `f1e80c48f`: 527: alias global de fase S1 exato é CONTRAFACTUAL, posto local maior não determina winding sem prior de taxa; avaliação conservada. CI autor 16/16 SUCCESS; push 16/16 SUCCESS.
- [#299](https://github.com/franklinbaldo/conde-incident/pull/299), `02307e8c2`: C241-P7: Kepler/J2 avalia período compilado condicionado a elementos NASA; não há época instrumental nem teste externo terminal. CI autor 16/16 SUCCESS; push 15/16 SUCCESS; Pages CANCELLED, não verde integral.
- [#300](https://github.com/franklinbaldo/conde-incident/pull/300), `a99362ad9`: ON20: 23 páginas CCITT do manual NMC posterior têm hashes declarados/replay; não prova leitura de perfil meteorológico 1963. CI autor 16/16 SUCCESS; push 16/16 SUCCESS.
- [#301](https://github.com/franklinbaldo/conde-incident/pull/301), `0a4306ab1`: CI: dois workflows meteorológicos removem eventos redundantes e prendem SHA; verificação de automação não autentica fonte. CI autor 16/16 SUCCESS; push 17/17 SUCCESS.
- [#303](https://github.com/franklinbaldo/conde-incident/pull/303), `e247a8221`: J2 nodal: RK4 e taxa média usam constantes compatíveis e fase arbitrária; sensibilidade por fase e ausência de holdout histórico explícitas. CI autor 16/16 SUCCESS; push 17/17 SUCCESS.
- [#302](https://github.com/franklinbaldo/conde-incident/pull/302), `638a39751`: G28-F1: JSON de exceções de tamanho aceitava QUALQUER caminho nomeado com justificativa, inclusive dados/código >20KB; contraprova FAIL antes da correção, PASS após allowlist de lockfile. CI autor 16/16 SUCCESS; push 17/17 SUCCESS.
- [#305](https://github.com/franklinbaldo/conde-incident/pull/305), `5ca161481`: Acessibilidade: reflow 320px e navegação teclado testada; sem promoção de ilustração para observação física. CI autor 17/17 SUCCESS; push 17/17 SUCCESS.
- [#306](https://github.com/franklinbaldo/conde-incident/pull/306), `c855b4603`: C241-P8: 4 segundos de arco da rede Baker–Nunn de 1961 e valores SRI 1965 não são sigma/covariância do 528 em 1963; mantém lacuna. CI autor 16/16 SUCCESS; push 17/17 SUCCESS.
- [#307](https://github.com/franklinbaldo/conde-incident/pull/307), `0031f2a89`: Caderno 06: carta UWM de 1954 com atualização só das vias em 1961; malha IBGE chamada 1960 baseada em 1991 não reconstitui limite municipal legal em 08/11/1963. CI autor 16/16 SUCCESS; push 17/17 SUCCESS.

## G28-F1: exceção JSON podia virar dispensa arbitrária

A PR #302 pretendia liberar somente `bun.lock`, mas `editable_exemptions()` aceitava qualquer caminho exato no manifesto editável se acompanhado de uma justificativa. A contraprova adicionou `scientific-proof.json` de 20.001 bytes e `third-party.lock` acima do limite, ambos nomeados no manifesto. **Antes:** dois testes FAIL porque o gate aceitava; **depois:** os dois PASS porque uma allowlist em código só permite `bun.lock`. A exceção intencional da PR #302 permanece estritamente localizada; a dívida de blobs legados continua congelada por SHA. Novas exceções exigem revisão de código/teste, não só edição de metadados.

## Ciência, proveniência, modelos e limites

- **Fontes:** SSR NASA em 15/10 e 15/11, crônica Última Hora 14/11, mapa UWM/AGSL 10814 e malha IBGE são documentos identificados, de diferentes funções. Nem o boletim compilado, nem a crônica e nem a malha de 1991 se convertem em uma observação instrumental ou impacto do NORAD 528. ON20 é manual posterior; a validação de bytes não comprova originalidade histórica.
- **Dependências cumulativas:** C179/C151 foram ligados a observáveis *inativos*, conservando época, independência, calibração desconhecida e parâmetros pendentes. Não reduzir domínio numérico sem dados calibrados, mas também não perder ligações.
- **Lean:** nenhum `.lean` alterado nestas 15 integrações. CI do corte executou Lean com sucesso, mas `#print axioms` independente não foi reexecutado localmente; modelos C241 e contrafactuais S1 não demonstram nem excluem a queda.
- **Física:** a regressão J2 de #303 é cenário com fase arbitrária; Kepler/J2 de #299 não valida estado orbital terminal, nem erro instrumental. Falta medição com instante, sensor, referência, covariância e holdout externo. RAAN conflitante segue sem resolução por fonte primária.
- **Editorial:** os Cadernos 05/06 separam crônica satírica, datas cartográficas 1954/1961/1991 e alegação de 1963; nenhuma posição exata de impacto é deduzida. O controle de UI de 320px e os embeds não são evidência científica.

## Testes e CI

Python local: file-size 10/10, TLE Oct15 22/22, J2 Kepler 7/7, S1 alias 6/6, observáveis 6/6, Recife 4/4, NCEP 6/6, CGEO 9/9 e workflows meteorológicos 4/4: **74/74 PASS**. `python3 scripts/check_file_size.py` PASS. Node, Lean e Prek completos: **NOT_RUN local** neste executor; CI remoto no corte `0031f2a89` **17/17 SUCCESS**, incluído Lean/Prek. Duas integrações tiveram Pages CANCELLED (#295, #299), sem serem classificadas totalmente verdes, embora seus HEADs autorais tiveram CI SUCCESS. Os resultados de CI por PR/SHA estão no JSON.

**Estado científico:** `CONDE_INDETERMINATE`. A correção é de controle da qualidade, não observação física. Nenhum contato externo, blog pessoal ou hipótese convertida em fato.

Próximo checkpoint G29: partir de `0031f2a894fcbf6b2c59fb2d80d0f31a3d95e099`, incluindo a própria PR de correção e integrações concorrentes; reconferir o fluxo OKF na casa pessoal privada.
