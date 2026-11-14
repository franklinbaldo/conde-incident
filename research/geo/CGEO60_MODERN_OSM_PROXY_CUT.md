---
type: Evidence
title: 'CGEO-60: dois nós OSM modernos e corte da linha fotográfica não decisiva'
description: 'Nomes de lugar contemporâneos conferidos por XML OSM; não são geometria de Centro/Vila em novembro de 1963.'
---

# CGEO-60 | Nós modernos para análise de sensibilidade, não um ponto de impacto

**14/11/2026.** Em vez de expandir indefinidamente a busca NARA de 1942, esta fatia faz o corte temporal solicitado em [Conde #558](https://github.com/franklinbaldo/conde-incident/issues/558) e oferece ao [Castor #870](https://github.com/franklinbaldo/conde-incident/issues/870) **dois novos pontos modernos cuja proveniência é explícita**, para teste contrafactual separado de `CENTRO20`/ `VILA20`.

## Dois registros OSM originais, adquiridos em 14/11

| Nó nominal | Elemento OSM | Lat., lon. decimal (fonte) | Versão/última edição |
|---|---|---|---|
| [Conde](https://www.openstreetmap.org/node/415521889), `place=town` | 415521889 | −11.8129758, −37.6138705 | v18, 18/09/2026 |
| [Villa Velha](https://www.openstreetmap.org/node/4697713641), `place=village` | 4697713641 | −11.7968448, −37.6214666 | v3, 12/12/2023 |

Os XMLs foram readquiridos diretamente pela API [OSM 0.6](https://wiki.openstreetmap.org/wiki/API_v0.6) com HTTP 200: Conde **813 bytes**, SHA-256 `cbd57dad048e8111d36435689d7baa5a821f35b883cdc3dc851883fa48bdd3d4`; Villa Velha **545 bytes**, SHA-256 `7273d6ba1e5e09d490b394c8115eb2983aca25d1dcd3b033a8c9781ebda1d66e`. Licença ODbL, atribuição © OpenStreetMap contributors. A tag `source=IBGE` do nó Conde não comprova o método de obtenção de suas coordenadas.

A distância de grande círculo entre **esses dois nós digitais** é aproximadamente **1,975 km**, calculada com esfera de 6.371 km, não uma medida do tamanho da cidade, separação jurídica Centro–Vila, precisão GPS, marco de 1963 ou trajetória de fragmento.

Os nomes dos nós **não equivalem automaticamente** às localidades do [documento municipal CGEO-20](cgeo20_centro_vila_2020.json): `CENTRO20` designa Centro / Praça Severino Vieira e `VILA20` designa Praça Vila do Conde em **2020**. Os dois `point` de CGEO-20 continuam nulos, e a terminologia `Villa Velha` do OSM não demonstra continuidade ou sinonímia histórica. Tampouco o nó `place=town` de Conde equivale a coordenadas do centro de 1963. Não sobrescrever CGEO-20.

## Corte operacional dos ramos fotográficos

- [NARA RG 373](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography): overlays em 11S037W/12S037W com datas candidatas de **setembro de 1942**, preparados em **outubro de 1956**. Imagem pré-evento pode contextualizar a paisagem, mas **não revelar marca criada em novembro de 1963**. Não ampliar quadrículas ou solicitar negativos por esse objetivo sem nova pergunta documental específica. O inventário existente é preservado; negativo ainda não identificado.
- [SGB USAF 63-32](https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF): cartucho do fotoíndice MI-1850 imprime **1964–1970**, que não autentica tomada em 1963. Para uma feição **hipotética** de 4 m e escala fotográfica 1:60.000, o diâmetro geométrico no filme seria `4 m ÷ 60.000 = 0,0667 mm` (cerca de **67 µm**). **Isso não prova detectabilidade nem indetectabilidade**: faltam data individual, fotograma, resolução óptica e de digitalização, contraste, sombra, preservação da feição e registro antes/depois. Não converter esse cálculo em “buraco observado”.

**Handoff ao Castor:** executar dois cenários novos com os **nós OSM modernos** sob rótulo `MODERN_OSM_PROXY_ONLY`, como análise de sensibilidade do operador de plano de #870, sem chamar isso de `CENTRO20`, `VILA20` ou localização da queda. Manter `CENTRO20=NOT_EVALUATED_NO_CUSTODIED_POINT` até obter geometria da praça/centro com fonte e ponte temporal; o ponto moderno da câmera CGEO-15 continua um terceiro ensaio independente de nome, **não uma observação histórica adicional**.

Verificação: `python3 tools/cgeo60_modern_osm_cut.py` valida invariantes e derivação; `--live` reabre os dois registros OSM e exige identidade, versão, coordenadas e data do documento XML (o hash de byte original pode variar por cabeçalhos `generator` mesmo com conteúdo semântico idêntico). `python3 -m unittest discover -s tests -p 'test_cgeo60_modern_osm_cut.py' -v` executa mutações adversariais.

**Estado:** nenhum ponto de queda, centro histórico, footprint de fotograma, intervalo orbital novo ou posterior; `active_constraint=false`. Trabalho arquivístico opcional permanece com [Lontra #8](https://github.com/franklinbaldo/lontra/issues/8), sem contato externo não autorizado.
