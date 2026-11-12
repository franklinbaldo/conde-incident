# 🐝 Custódia e grafo documental do caso Conde, fatia C01–C238

A fonte de verdade desta exportação é a **matriz cumulativa congelada** em
[`research/evidence_matrix_C001-C238_2026-11-11.md`](../evidence_matrix_C001-C238_2026-11-11.md),
Git blob SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7`. **O grafo não acrescenta
medição de reentrada, hora, local ou testemunha.**

O [registro curado de proveniência](lineages.json) descreve 22 fontes/documentos
de dez famílias, suas dependências documentais explícitas, 29 citações
para 28 ocorrências e três conexões com contratos de modelo. O compilador
[Python sem dependências externas](../../tools/provenance_graph.py) retém
**todas as 241 ocorrências** da matriz (238 rótulos e C44/C45/C46 duplicados);
as **213 não mapeadas ficam marcadas como não mapeadas**, sem inferência por
similaridade de texto. Novas fontes podem expandir a cobertura aditivamente,
mas não podem alterar silenciosamente o hash do corpus.

## Saídas reproduzíveis

```sh
python3 -m unittest discover -s tests -p 'test_provenance_graph.py' -v
python3 tools/provenance_graph.py \
  --output /tmp/conde-documentary-provenance.json \
  --citations /tmp/conde-documentary-citations.json \
  --check-site
```

- **Grafo completo** (artefato do CI): `conde.documentary-provenance-graph/v1` inclui família, documento, dependência direcionada, **Cnn#ocorrência**, linha, SHA-256 da linha, texto literal da célula e referências dos contratos. Útil ao Polvo para construir a ponte evidência → predicado Lean sem confundir matriz com observação.
- **Citações curadas**: `conde.source-citations/v1` relaciona `occurrence`, `matrix_line`, `row_sha256`, `source_id`, `source_family`, `work_id`, `citation_url`, `locator`, `relation` e `scope`. Está versionado também como [feed estático do site](../../public/data/conde-source-citations.json), servido pelo Vite em `/data/conde-source-citations.json`. A interface só deve renderizar citações sem transformá-las em confirmação física.
- **Atualização do feed**: editar primeiro `lineages.json`, adicionar testes, e executar `python3 tools/provenance_graph.py --write-site`. O CI falha se o feed estiver desatualizado.
- **Integração com Castor**: `contracts` referencia `research/constraints/ssr_1963_observable_graph.json` e `formal/scripts/physical_observable_bridge.py` com `status` explícitos. Não há redução de domínio físico, nova likelihood, ou informação de órbita terminal.

## Exemplos de cadeia e cautelas

1. **C01#1, C02#1 e C03#1:** `FBIS_EOP_UAP_D001 → RADIO_TUPI_19631108` é transcrição de **uma cadeia informativa** sobre esfera, cratera e corpo, não três testemunhas, nem confirmação de uma esfera encontrada. O áudio original não está sob custódia.
2. **C131#1 e C197#1:** NASA, `Satellite Situation Report` de **15/11/1963**, p. impressa 8, registra `8 NOV 63` em `DECAYED OBJECTS`. É registro do **dia**, não observação de hora ou longitude. **C198#1** cita a ficha NTRS com o mesmo `work_id`: ficha e PDF não são duas observações. NASA/AFSPC/NORAD estão no grupo `NORAD_NASA_TRACKING` para **não pressupor rastreamentos independentes**. A pertença ao grupo **não prova que todos os documentos sejam cópias da mesma medição**. O próprio grafo marca contagem instrumental independente como desconhecida.
3. **C05#1 e C06#1:** o despacho consular cita jornais baianos, mas os recortes não foram inspecionados. Os dois vínculos `quotes_uninspected_source` não promovem essas citações em testemunhas de campo.
4. **C17#1/C18#1/C19#1/C23#1:** índices GFZ e fluxo NRC são duas séries ambientais; CelesTrak agrega ambas e não constitui uma terceira medição. Esses índices **não medem a órbita do 528**.
5. **C151#1:** há ventos instrumentais de **Recife**, com hora real de lançamento não recuperada, mas **não** há vento medido em Conde nem inferência de queda naquela localidade.
6. **C44#1 e C44#2**, e analogamente C45/C46, têm temas distintos. Sempre usar `#ocorrência` e linha: `C44` sozinho é referência inválida.

## Regras de evolução

A ausência de aresta **nunca** prova independência. Uma fonte secundária não se
torna primária por ter SHA-256 ou link funcional. O código valida referências,
ciclos, famílias críticas, `work_id` comum NASA, proibição de marcadores de
impacto fisicamente confirmado e caminhos de contratos; **não valida a
autenticidade histórica do documento remoto**, já avaliada conforme a matriz.

Para ampliar cobertura, registrar primeiro a ocorrência exata e a fonte concreta
(URL/custódia, edição, localização/página, classe e upstream), sua relação
e limite. Adicionar teste contra dupla contagem ou promoção indevida.
Mantêm-se os registros negativos e correções C182/C184/C200.

## Identidades por snapshot: C144 a C151, legado versus matriz

O arquivo local Lean formal/Conde1963/Evidence.lean (154 registros) reutiliza
C144 a C151 para outras oito proposicoes. Nao e uma segunda fonte fisica.
O compilador consome formal/scripts/audit_legacy_154.py, com hashes
verificados e comparacao literal, para exportar legacy_alias_conflicts
ao grafo e uma lista de conflitos segura ao feed do site.
O ZIP original continua sem autenticacao documental.

Cada citacao e contrato curado exige chave completa
matrix:<git-blob-sha1>:Cnn#ocorrencia, por exemplo
matrix:a7978c3a75a153b16ab70118a92c434bba674cb7:C151#1.
O outro snapshot usa legacy-154:<sha256>:C151#1, referindo-se
a TRIANGULACAO no documento local antigo, nao aos ventos de Recife.
Unir pelo simples C151 ou C151#1 e incorreto, mesmo que os dois
arquivos mencionem o mesmo numero. C44 a C46 exigem #1 ou #2.

Auditoria de consumidores em 12/11/2026: formal/Conde1963/Evidence.lean
contem as proposicoes legadas; formal/scripts/physical_observable_bridge.py
e os arquivos IGRA/meteorologia utilizam as proposicoes atuais.
O bridge ja identifica o SHA da matriz; este PR nao reescreve dados
fisicos de terceiros. O feed fornece snapshot_ref para integracoes
futuras do site e Lean. Nao ha novo limite de orbita nem dado de queda.

## Fatia NARA Blue Book e pista jornalística O Globo (12/11/2026)

O [relatório custodial da Lontra](../archives/nara_bluebook_conde_naid_302531012_2026-11-12.md) registra uma unidade documental específica **NARA NAID 302531012**, série 597821, T1206 rolo 49. A Abelha consumiu essa análise da Lontra; não reivindica ter reinspecionado as três imagens JP2 ou recalculado os hashes do download.

As imagens NARA 0809.jp2 (objectId 302531013, cartão administrativo Other/Hoax), 0810.jp2 (302531014, mensagem USAIRA 14/11) e 0811.jp2 (302531015, mensagem USAIRA 21/11) são **três documentos na mesma unidade arquivística**, não três testemunhos. Cada objeto tem URL, SHA-256 e tamanho registrados, sob aresta part_of_archival_unit. A mensagem posterior tem relação refers_to_prior_telegram com a primeira e reports_shared_consular_account com o despacho A-628, o que **não implica cópia literal do A-628**.

O texto da mensagem USAIRA de 14/11 cita uma publicação **O Globo 08/11/1963** recebida de Salvador. O exemplar original ainda não foi inspecionado; não se conhece a hora, autoria, crédito, edição, ou se a notícia precedeu a Rádio Tupi de 8/11 às 23h30. Esse elo fica como nó sem URL e post_matrix_occurrences do G18 no feed estático, com **URL e SHA-256 da página NARA que fez a referência**, newspaper_publication_time nulo e journalistic_source_independence UNRESOLVED. Não cria nova ocorrência Cnn na matriz congelada e não implica fato físico.

A exportação passou a incluir a curadoria explícita de C232#1 (índice The Black Vault e cotejo separado com cartão NARA), C233#1 (limite de leitura textual do índice), C234#1 (catálogo Dark Forest ainda **sem prova** de equivalência entre ID externo 9737078 e NAID 302531012) e C235#1 (guia institucional NARA). O antigo C237#1, busca então negativa, continua sem citação curada e não é tratado como inexistência de documento.

Contabilidade: 241 ocorrências, 28 curadas, 213 pendentes, 29 arestas de citação, 22 fontes em 10 famílias. Duas citações para uma ocorrência não são duas observações. Nenhuma nova medição, posição, instante de reentrada, domínio Lean ou probabilidade foi produzida.

## Integridade do crosswalk de citações (12/11/2026)

Cada `scope` de citação precisa pertencer à lista revisada de estados **documentais**
em `tools/provenance_graph.py`, também compatível com sua `relation`.
Novos valores exigem alteração deliberada do contrato e teste; códigos físicos
inventados (como `OBSERVED_CONDE_CRATER`) não atravessam o exportador.

A ocorrência posterior `NARA-BB-CONDE-20261112-01` agora precisa vincular
seu `image_sha256`, `nara_object_id`, `nara_fileunit_naid`, nome de arquivo e
`report_path` aos **mesmos identificadores do objeto digital** e da unidade
fonte. Um SHA-256 sintaticamente válido, mas de outra página, não passa.
Essa validação é de **consistência interna da custódia curada**: não significa
que a Abelha baixou as imagens, autenticou sua cadeia externa ou encontrou
um novo testemunho físico. O feed continua com 241 ocorrências, 28 curadas,
29 citações e 213 ocorrências sem curadoria.
