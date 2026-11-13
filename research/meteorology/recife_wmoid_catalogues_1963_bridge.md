---
type: Guide
title: "C149–C151: distinguir WMO 82899 e 82900 sem inventar estação de 1963"
description: "Auditoria cruzada de duas fichas retrospectivas independentes como publicações, com hashes e veto à retroprojeção instrumental ou geográfica."
---

# Dois identificadores modernos de Recife não autenticam a estação de 1963

**Pergunta testável:** é seguro fundir as fichas WMO **82899** e **82900** encontradas no histórico tardio da NOAA `BRM00082900` (C149–C151)? Não: duas instituições publicam denominações diferentes para os dois códigos, mas isso **não** identifica qual local, instrumento ou procedimento era usado nos lançamentos históricos de 7–9/11/1963.

## Fontes e ocorrências (recuperadas em 13/11/2026 UTC)

1. [CEDA/UK Met Office, lista de estações radiossonda na América do Sul](https://artefacts.ceda.ac.uk/badc_datadocs/radiosglobe/southamerica.html): linha `82900 Recife/Curado 8.03S 34.55W 7m`. HTML completo recuperado: **6.302 bytes**, SHA-256 `dc8354d3f2d012838e26c6f80b68849fa784ad917732e816ab86fc54ffa03a29`. **Data de vigência da ficha não identificada**; latitude/longitude são da lista retrospectiva, não georreferenciamento validado para 1963. A elevação de 7 m é metadado catalogado, não altitude certificada de lançamento naquele ano.
2. [CPRM/Serviço Geológico do Brasil, *Atlas pluviométrico do Brasil*, Recife, 2014](https://rigeo.sgb.gov.br/items/1f0cc1e9-5f8b-4c8b-b816-a88a2665b854): o título catalográfico associa **82899** à **estação pluviográfica Aeroporto de Recife**. HTML completo: **464.477 bytes**, SHA-256 `8a310e76a75b74267c74e934742585e9363f930b2278d3a2df45db86d419ae6a`. O documento é de **2014** e versa sobre pluviometria, não radiossonda em 1963.

Os excertos originais preservados em [TXT](recife_wmoid_catalogue_excerpts.txt) possuem SHA-256 próprio e alimentam o [manifesto JSON](recife_wmoid_catalogues_1963_bridge.json). O script [audit_recife_wmoid_catalogues.py](../../tools/audit_recife_wmoid_catalogues.py) confere offline a integridade, a distinção de códigos e o bloqueio de inferências indevidas; `--download` relê as duas páginas e mostra se o HTML integral mudou, mantendo a comparação dos excertos. Hash de página HTML não é assinatura institucional e pode mudar legitimamente.

## Independência e variável conectada

São **dois catálogos de proveniência editorial distinta**, mas sem demonstração de independência dos registros históricos de origem. Em particular, a ficha pluviográfica não fornece um segundo valor de vento, p/T ou GPH de 1963. Um nome de estação da CEDA não comprova que a radiossonda ou a coordenada IGRA de 1963 coincidam com aquela ficha. O catálogo NOAA de 1982–1992 e os produtos atuais não devem ser lidos como atas contemporâneas da operação meteorológica em 1963.

`CEDA:82900` e `CPRM:82899` → `C149–C151` → `identidade WMO 1963 [PENDING]` → `custódia do sensor/GPH/σ [PENDING]` → `erro de transferência Recife→Conde [PENDING]` → `deriva/arrasto do Castor [NÃO AVALIÁVEL]`. As arestas estão no JSON e não impõem um valor físico. A observação original é NOAA/IGRA com hora nominal, hora real desconhecida. **Nenhuma medição foi produzida em Conde**; não há localização de queda, valor de densidade, erro instrumental ou encurtamento de domínio. A comparação não transforma metadados de superfície em dados termoesféricos (C17–C23/C193).

## Reprodução

```bash
python3 tools/audit_recife_wmoid_catalogues.py --check
python3 tools/audit_recife_wmoid_catalogues.py --check --download
python3 -m unittest discover -s tests -p 'test_recife_wmoid_catalogues.py' -v
```

O próximo documento decisivo é **a edição de 1963 do WMO No. 9, Volume A ou equivalente de estações de altitude**, contendo época e identificação operacional, acompanhada de ficha de instrumentação do mesmo período. Até ser localizada, duas labels retrospectivas apenas explicitam uma ambiguidade e não autorizam tomar a posição de Recife/Curado como dado instrumental coevo.
