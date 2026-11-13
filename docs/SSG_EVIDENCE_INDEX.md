---
type: Guide
title: Índice documental JSON determinístico para SSG
description: Contrato de custódia e geração sem backend para busca opcional no site Conde.
---

# Dados estáticos, sem criar outra matriz

`tools/export_ssg_evidence_index.py` lê somente `public/data/conde-source-citations.json` e `public/data/conde-declared-dependence.json`. A saída é um manifesto e shards JSON de no máximo 12.000 bytes em `public/data/conde-evidence-index/`. Cada shard recebe SHA-256 em manifesto; as duas fontes originais também recebem hash de seus bytes, e o SHA-1 do snapshot imutável da matriz é preservado.

O script **não inventa status nem testemunhos**: exporta `source_status` literalmente, `snapshot_ref`, `row_sha256`, identificador de fonte, família, obra, localizador, citação, relação, limites, genealogia declarada e `archive_path` para página SSG existente. `independent_physical_observation_count` permanece `null`. A falta de aresta de proveniência não significa independência. O campo `post_matrix_ids_not_in_curated_index` declara explicitamente que os registros posteriores ao snapshot ainda não estão nas páginas curadas. `unmapped_matrix_occurrences` impede alegar cobertura completa.

A jornada sem JavaScript continua no arquivo documental gerado por `scripts/ssg-documentary-archive.mjs`; o manifesto é **um índice de leitura por máquina**, destinado a Raposa (integração) e Morcego (auditoria de navegação), e não uma segunda interface. Abelha deve revisar as regras de consistência genealógica antes de ampliar a cobertura.

Reproduzir com `python3 tools/export_ssg_evidence_index.py --check` e `python3 -m unittest discover -s tests -p test_ssg_evidence_index.py`. Para atualizar após mudança canônica: executar o script sem `--check`, revisar os diffs e submeter PR com CI no SHA final. O workflow Pages executa a checagem antes de preservar `public/data/` para publicação; `ssg check/build/audit` e Prek/OKF continuam como gates separados.

## Imutabilidade verificada contra o arquivo matriz (Lagarto)

O mesmo SHA-1 declarado em ambos os feeds não basta para autenticar uma matriz:
uma adulteração coordenada dos feeds pode preservar a igualdade entre eles.
O exportador Python e o auditor Node reabrem a matriz histórica em bytes,
calculam o Git blob SHA-1 a partir do cabeçalho de tamanho e conteúdo original,
e verificam o número de linha, SHA-256 da linha sem terminador e ID Cnnn.
Um digest sintaticamente válido, mas falso, falha mesmo se o feed genealógico
e o shard forem atualizados em conjunto.

Isso verifica a integridade entre três representações versionadas, não a
autenticidade dos fac-símiles externos nem a verdade física do relato. A matriz
histórica é fixa e os acréscimos posteriores continuam explicitamente fora
deste recorte curado. Testes adversariais reproduzem adulteração da matriz,
remapeamento de linha e digest forjado consistente. Rodar Python e Node no SHA
exato do workflow que compila o SSG.

## Ponte verificável JSON → SSG (Lagarto)

`node scripts/verify-ssg-evidence-index.mjs` confere os hashes e tamanhos dos shards, a correspondência literal dos atributos documentais, genealogias, IDs e as rotas individuais `archive_path` com páginas geradas pelo SSG sem JavaScript. Também exige links reversos para fontes, obras e famílias. `node --test tests/ssg-evidence-index-bridge.test.mjs` inclui contraprovas com digest recalculado, rota inexistente e falsa promoção de status. Após `ssg build`, `node scripts/verify-ssg-evidence-index.mjs --built-site` verifica cada HTML da edição real, em vez de supor que o Markdown gerado virou rota publicada. O verificador não identifica sensores independentes, não autentica documentos externos nem valida uma queda.

## Percurso documental auditável (Lagarto, 13/11/2026)

Cada ocorrência apresenta literalmente o código source_status da fonte canônica
(classificação documental, **não** comprovação de impacto), digest row_sha256,
localizador e origem HTTPS. O verificador agora exige no HTML realmente compilado
links clicáveis: índice → ocorrência → documento original e linha imutável da
matriz; ocorrência → família/obra/fonte → ocorrência. Um endereço impresso sem
âncora não satisfaz o gate.

Este percurso usa somente os dois feeds canônicos versionados; não cria
outro catálogo nem observações físicas. Testes adversariais abrangem URL inerte,
status ausente, retorno quebrado e linha imutável sem link. O fixture HTML
sintético valida o auditor; somente o workflow Pages no SHA exato valida o SSG
Rust real. Acessibilidade por teclado e viewport 320 px permanecem para o Morcego.


## Falsos positivos de HTML inerte (Lagarto)

O gate `--built-site` não deve contar texto de scripts, metadados,
`template`, comentários, âncoras fora de `<main>` ou elementos com
`hidden`, `inert`, `aria-hidden`, `display:none` ou `visibility:hidden`
como navegação ou estado documental visível. O auditor examina o HTML
estático produzido, não apenas substrings `href` ou `source_status`.
Há testes adversariais de conteúdo e links falsificados mesmo quando o
manifesto JSON permanece íntegro. Isso **não** substitui auditoria em
navegador para CSS externo, JavaScript, foco/teclado, leitor de tela e
320 px, sob responsabilidade do Morcego e da Raposa.

## Validação independente do grafo no gate Node

O gate de publicação em Node não se limita à igualdade entre JSON genealógico
e shards: valida a forma exata de cada cadeia declarada (somente `edges` e
`upstream_source_id`), de cada aresta (`from`, `to`, `kind`), continuidade,
ausência de ciclo e concordância do identificador terminal. Isso espelha
a validação Python e detecta uma adulteração sincronizada dos dois feeds
mesmo com hashes SHA-256 recalculados. Quatro contraprovas (campo terminal
inventado, ciclo, salto e campo extra em aresta) exercitam esse requisito.
A checagem protege a representação versionada, não afirma que a origem
documental foi autenticada ou que há observação física independente.

## Alegação textual vinculada à matriz congelada

Além de conferir SHA-1 do blob, SHA-256 da linha, posição e ID, os validadores
Python e Node exigem que `claim_text` coincida literalmente com a segunda
coluna de conteúdo (título da alegação) da linha congelada da matriz. Um
editor não pode reescrever simultaneamente o feed de citações e o shard
para anunciar, por exemplo, um impacto confirmado enquanto mantém o hash
real da linha. Os testes negativos exercitam essa adulteração coordenada.

O vínculo não transforma a alegação em fato observado, nem valida o
`source_status` contra documentos externos: esse juízo permanece curatorial,
sujeito à auditoria documental de Abelha e dos demais pesquisadores.

## Cobertura integral da matriz, sem fingir curadoria (Lagarto r36)

O manifesto `public/data/conde-evidence-index-manifest.json` agora expõe
`unmapped_matrix_refs`: cada **ocorrência da matriz congelada ainda fora do
índice curado**, com `occurrence` (incluindo ordinal `#N`) e `matrix_line`.
O exportador enumera diretamente as linhas do **Git blob SHA-1 original**,
reconcilia 241 ocorrências de 238 identificadores C01–C238 (C44, C45 e C46
ocorrem duas vezes), 28 ocorrências já curadas e **213 ainda não indexadas**.
A ordem é a ordem da matriz, nunca a de um contador derivado de feeds JSON.
O auditor Node recalcula esse inventário a partir dos mesmos bytes congelados
independentemente do exportador; ambos rejeitam contagens convenientes ou
omissão de um item, mesmo que os números declarados sejam editados em conjunto.

Esta lista é um **índice de lacunas de curadoria**, não uma lista de
não ocorrências históricas e tampouco inferência de independência. O registro
canônico, seu texto e grau epistemológico permanecem na matriz original.
Para cada `matrix_line`, o leitor pode consultar a URL imutável da linha
com o `matrix_git_blob_sha1` do próprio manifesto. O índice SSG existente
continua navegável sem JavaScript; a Raposa pode oferecer filtragem opcional
dessas lacunas, e Abelha deve revisar a curadoria antes de incorporá-las.
Nenhuma nova fonte nem restrição física é introduzida por esta mudança.
