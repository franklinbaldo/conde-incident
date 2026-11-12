---
type: Guide
title: "C151: perfil de vento de Recife 08/11/1963, procedência e transformação u/v"
description: "Auditoria reprodutível NOAA IGRA 2.2, sem inventar vento de Conde, lançamento ou densidade."
---

# C151: vento em altitude em Recife, não em Conde

**Resultado instrumental (NOAA/NCEI IGRA 2.2):** a sondagem **nominal** de **8/11/1963 12 UTC**, estação **BRM00082900 (Recife)**, tem 26 níveis registrados, dos quais **15 apresentam vento completo** (direção e velocidade); os outros **11 têm vento ausente** no arquivo. A faixa com vento documentado estende-se do nível de superfície **1016 hPa, 10 m geopotenciais sobre o nível do mar**, ao de **20 hPa, 26.693 m**. Não se trata de 15 lançamentos independentes. Os níveis são coobservados em **uma única sondagem**.

## Custódia e independência

- **Fonte primária arquivística acessada em 12/11/2026:** [NOAA IGRA2 período integral, Recife BRM00082900](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), **7.834.492 bytes**, SHA-256 0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc. O ZIP foi baixado integralmente, passou no teste interno de integridade e contém BRM00082900-data.txt; dele foi copiado **literalmente** o cabeçalho e 26 registros de nível de 08/11, totalizando **1.450 bytes**, SHA-256 577224172e19552f5ce87081897479255596dc44debacc674dfd9d9ec418207e. Trecho auditável em igra_recife_19631108_raw.txt.b64 (base64 dos bytes originais, reversível e sem normalização de espaços), não arquivo sintético.
- **Dicionário de campos NOAA:** [IGRA 2.2 formato dos dados](https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt), SHA-256 dfd7b4d2dd18a255477455a7caefd12cb21c30549a1e70cbc3a51db9f41c1dfe. PRESS em Pa; GPH em metros geopotenciais ASL; WSPD em décimos de m/s; WDIR em graus **de onde vem**; -9999 = dado ausente, **não zero**.
- **Estação/posição no catálogo NOAA:** [lista IGRA de estações](https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt), SHA-256 5a277ba4036544cb79d07e3f503f7ca1aaa2d81a304dbea5f79ac24808d2dc34: Recife **-8,0500°, -34,9167°, 7 m** (elevação catalogada). O cabeçalho da própria sondagem repete latitude/longitude; porém, conforme o manual IGRA, para estações fixas a posição do cabeçalho reutiliza o inventário e **não reconstrói mudanças históricas da posição**. Não foi validada a posição exata do instrumento em 1963.
- P_SRC=ncdc6301 no cabeçalho designa **NCDC U.S. Rawindsonde Data (DSI-6301)**, uma linha upstream do compilador IGRA. Não contar outra cópia UADB/NCAR como testemunha independente sem confrontar origem e registros. A estação instrumental é independente da cadeia de relatos Tupi–FBIS, mas os níveis não são amostras independentes.
- **Temporalidade não resolvida:** HOUR=12 é *hora nominal*; RELTIME=9999 indica horário real do lançamento **ausente**. Não foi constatada hora exata, altitude temporal de cada nível, nem intervalo de erro observacional. Os incrementos de 0,1 m/s na codificação não são uma estimativa de incerteza instrumental.

## Dados úteis para uma futura comparação de deriva

| Pressão | Altura geopotencial ASL | Vento informado (de onde vem) | u leste (m/s) | v norte (m/s) |
|---|---:|---:|---:|---:|
| 850 hPa | 1.560 m | 100° / 4,0 m/s | -3,939 | +0,695 |
| 700 hPa | 3.197 m | 236° / 4,0 m/s | +3,316 | +2,237 |
| 500 hPa | 5.917 m | 159° / 6,0 m/s | -2,150 | +5,601 |
| 300 hPa | 9.745 m | 129° / 15,0 m/s | -11,657 | +9,440 |
| 250 hPa | 11.007 m | 102° / 17,0 m/s | -16,629 | +3,534 |

O vetor meteorológico **de onde vem** é convertido ao vetor de transporte **para onde vai** pela fórmula u = -velocidade × sen(θ), v = -velocidade × cos(θ). Os sinais negativos de u indicam componente para **oeste**, não para leste. As direções variam bastante com a altitude, invalidando a aplicação mecânica de um único vetor de vento.

**Conexão cumulativa à matriz:** C149/C150/C151 (um arquivo, uma sondagem com 15 níveis); C144–C146 (cartas CHM de pressão superficial, outro tipo de fonte e altura); C17–C23 (índices geomagnéticos globais e F10.7, fenômeno diferente); C193 (densidades Explorer XVII de abril–junho de 1963, **não coetâneas**). O JSON anexo guarda as arestas e observáveis tipados. Ligação **observação → variável**: componentes u/v em Recife em cada nível e data nominal; ligação **variável → transporte** fica CONNECTED_PENDING_SPATIOTEMPORAL_TRANSFER: precisa de cenário físico, trajetória/altitude, tempo real e erro de transferência regional. **Não foi estimada densidade, arrasto orbital, deslocamento de balão até Conde nem local do NORAD 528.** Estes dados não impõem uma restrição física até que a ponte espacial-temporal seja cientificamente validada.

## Reprodução sem rede

Executar python3 tools/audit_igra_recife_winds.py --check para comparar o JSON ao trecho original fixado; executar python3 -m unittest discover -s tests -p test_audit_igra_recife_winds.py para testar 26/15 níveis, altitudes, unidades, vetores, proveniência e falsificações de horário/estação/origem. O reprocessamento do **ZIP integral** pode repetir extração e confirmar hashes publicados; o CI não baixa arquivos externos, preservando reprodutibilidade.
