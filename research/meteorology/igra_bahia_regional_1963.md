---
type: Guide
title: "Conde/BA: cobertura regional IGRA em novembro de 1963"
description: "Censo de 31 estações NOAA/IGRA por catálogo, quatro arquivos integrais e limites para a inferência meteorológica."
---

# Cobertura regional de ar superior: nenhum segundo perfil próximo demonstrado em 7–9/11/1963

**Pergunta:** entre os arquivos de sondagens NOAA/IGRA espacialmente próximos ao município de Conde, Bahia, quais documentam perfis nos dias 7 a 9 de novembro de 1963? O inventário auditado aponta **apenas Recife** na janela, sem provar que outras estações não tenham operado ou que Recife represente o vento em Conde.

## Como o universo foi definido

A referência cartográfica é o **ponto médio da caixa envolvente** do polígono municipal IBGE **2022** (código 2908606), aproximadamente latitude `-11,8641854` e longitude `-37,6893514`. Não é centróide, localização da cidade, posição histórica em 1963 nem ponto de queda. O manifesto lê a caixa diretamente do dado [`CGEO-01`](../geo/conde_ibge_2022_sirgas2000.json), cuja edição e SHA do ZIP IBGE estão fixados. Distâncias de Haversine em esfera com raio 6.371 km são **aproximações para triagem documental** calculadas a partir das coordenadas atuais do catálogo NOAA; distância mínima ao polígono e deslocamento histórico de estações permanecem desconhecidos.

No [cadastro de estações NOAA/IGRA](https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt) integral (SHA-256 `9515d29b0c61fcfc912028830c37f47e723ba32c14d88fb48cf6d8bf727060ab`), há **31 registros brasileiros** no raio documental de 1.500 km. Apenas quatro fichas abrangem **1963 entre seus anos extremos**. Como primeiro e último ano não provam cobertura mensal, foram baixados integralmente os quatro ZIPs oficiais e enumerados seus cabeçalhos de sondagem, com SHA-256 por captura no [manifesto](igra_bahia_regional_1963.json).

| Estação (código IGRA) | Distância aproximada ao ponto médio | Cabeçalhos de 1963 | Cabeçalhos em 7–9/11/1963 |
|---|---:|---:|---:|
| Recife `BRM00082900` | 522 km | **346** | **3** (um por data nominal) |
| Natal `BRM00082599` | 714 km | 0 | 0 |
| Fernando de Noronha `BRM00082400` | 1.063 km | 0 | 0 |
| Rio/Galeão `BRM00083746` | 1.353 km | **72** | 0 |

Os 72 cabeçalhos Galeão em 1963 distribuem-se entre janeiro e julho (17, 11, 7, 9, 14 e 14 em janeiro, fevereiro, março, abril, junho e julho, respectivamente); **não há nenhum registro de novembro de 1963 nesse ZIP**. O ZIP de Fernando de Noronha não contém cabeçalho de 1963, apesar de seu intervalo agregado no cadastro atravessar esse ano. Salvador, a 157 km na triagem, tem primeiro ano catalogado em 1970 e já foi auditada na [PR #420](https://github.com/franklinbaldo/conde-incident/pull/420), que também confirmou 0 registros de 1963 no seu arquivo.

## Hierarquia epistemológica

- **Observável arquivístico confirmado:** presença ou ausência de cabeçalhos nos **arquivos atuais examinados**, nunca prova de operação histórica ou sua inexistência.
- **Metadado retrospectivo:** nome e coordenadas das estações e anos inicial/final do cadastro consultado em 2026; não autentica a instalação ou programa de 1963.
- **Resultado computacional:** 31 estações no raio aproximado da referência IBGE 2022, quatro candidatas por anos extremos, e só Recife documentada nas três datas nominais. Os perfis Recife provêm de uma família arquivística, não de três sensores independentes.
- **Incertezas não estimadas:** localização dos lançamentos em 1963, hora efetiva de soltura, dependência entre fontes, representatividade espacial/temporal, vento sobre Conde e erro instrumental p/T/GPH/vento.
- **Restrição física:** **nenhuma**. Estado `CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION`; ligações C149–C151 e controle da PR #420. Não transformar 522 km em erro de transporte ou em limite de arrasto/deriva de objetos 527–529.

## Reprodução e cadeia de custódia

```bash
python3 tools/audit_igra_bahia_1963.py --check
python3 -m unittest discover -s tests -p 'test_igra_bahia_1963.py' -v
python3 tools/audit_igra_bahia_1963.py --station-list /caminho/igra2-station-list.txt --zip-dir /caminho/zips --check
```

O comando completo exige, no diretório, os ZIPs originais `BRM00082900`, `BRM00082599`, `BRM00082400`, `BRM00083746` com nomes `*-data.txt.zip`, comparando **bytes, SHA-256, conteúdo ZIP, estação e cabeçalhos**. Esses binários grandes não são incluídos no Git. O `--check` sem fontes confere invariantes do manifesto fixado, mas **não reabre os ZIPs**; não declarar auditoria independente dos binários somente pelo CI. A captura NOAA pode mudar na mesma URL. Se isso ocorrer, guardar as duas versões e investigar alterações antes de substituir qualquer hash. O teste integral foi executado com os quatro ZIPs capturados em 13/11/2026.

**Próximo experimento:** localizar mensagens TEMP/PILOT de 1963, material contemporâneo da WMO ou arquivo de observações da costa da Bahia. Uma cobertura ausente no IGRA não cria dado atmosférico novo nem fecha hipótese de impacto.
