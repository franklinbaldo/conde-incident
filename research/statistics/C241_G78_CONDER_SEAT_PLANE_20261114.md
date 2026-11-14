---
type: Experiment
title: "G78: sede CONDER versus nó OSM moderno nos cruzamentos de plano do 528"
description: "Sensibilidade geográfica condicional de duas fontes digitais contemporâneas; não recupera posição nem horário de 1963."
experiment_id: C241-G78-CONDER-OSM
verification_status: CONDITIONAL_MODERN_ONLY_NO_HISTORICAL_SITE
---

# G78 | Duas representações contemporâneas de Conde não são uma posição de 1963

O ponto da sede registrado pela CONDER/BA (CGEO-61, em EPSG:4326) difere em cerca de **751,892 metros** do nó OSM de Conde (CGEO-60). As duas camadas CONDER consultadas repetem o mesmo registro, portanto não são medições independentes. Nenhum dos dois pontos é um geocódigo autenticado da localidade descrita em 1963. Fontes: [CGEO-61](../geo/CGEO61_CONDER_SEDE_PROXY.md) e [G76](C241_G76_OSM_FBis_SENSITIVITY_20261114.md).

Reapliquei o operador físico já publicado em G76 e G77, usando os mesmos dois ramos orbitais secundários do NORAD 528, com semieixo constante e secante de decaimento, e a mesma raiz do **plano orbital** na noite de 8/11/1963. A única variável modificada foi a latitude/longitude moderna, de OSM para CONDER. Com ambas as hipóteses, a raiz calculada na coordenada da CONDER ocorre **1,628 segundo antes** da raiz calculada no nó OSM. São tempos de cruzamento geométrico de plano, não tempos em que o satélite esteve sobre Conde.

O [resultado JSON custodiado](c241_conder_seat_plane_g78.json) inclui SHA-256 de todos os insumos e o deslocamento relativo à câmera de referência. [Script](../../tools/c241_conder_seat_plane_g78.py) e [testes](../../tests/test_c241_conder_seat_plane_g78.py) validam os contratos CGEO-60/61, repetem a raiz da câmera, exigem a inexistência de fase e de ponte histórica, e verificam independentemente a nova raiz por bissecção. A aproximação EPSG:4326 versus EPSG:4674/WGS84 não tem certificado de transformação com erro: os milissegundos impressos são resolução numérica, jamais exatidão documental.

Reproduzir em executor autorizado: executar "python3 tools/c241_conder_seat_plane_g78.py --repo . --output research/statistics/c241_conder_seat_plane_g78.json --check" e os testes Python em modo normal e sob -O. Mutações que inventam identidade Centro-1963 ou trocam uma coordenada oficial devem falhar. Todos os Markdown seguem o contrato OKF e o projeto preserva o gate 20 KB.

**Limite científico:** o ponto CONDER não prova Centro, Vila ou queda em novembro de 1963. A fase orbital do 528, observações instrumentais, posição histórica, erros de época, convenções temporais do FBIS e probabilidade de impacto continuam ausentes. Portanto active_constraint=false, posterior=false, impact_probability=null. O resultado não reduz o domínio histórico de Conde.
