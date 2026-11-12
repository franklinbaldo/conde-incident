# 🐝 Custódia e grafo documental do caso Conde, fatia C01–C238

A fonte de verdade desta exportação é a **matriz cumulativa congelada** em
[`research/evidence_matrix_C001-C238_2026-11-11.md`](../evidence_matrix_C001-C238_2026-11-11.md),
Git blob SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7`. **O grafo não acrescenta
medição de reentrada, hora, local ou testemunha.**

O [registro curado de proveniência](lineages.json) descreve 14 fontes/documentos
de sete famílias, suas dependências documentais explícitas, 24 citações
para 24 ocorrências e três conexões com contratos de modelo. O compilador
[Python sem dependências externas](../../tools/provenance_graph.py) retém
**todas as 241 ocorrências** da matriz (238 rótulos e C44/C45/C46 duplicados);
as **217 não mapeadas ficam marcadas como não mapeadas**, sem inferência por
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
