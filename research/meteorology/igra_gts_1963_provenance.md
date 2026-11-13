---
type: Guide
title: "IGRA 1963: origem GTS versus identificação retrospectiva da estação Recife"
description: "Conecta a genealogia metodológica publicada em 2006 aos perfis C149–C151, sem retroprojetar metadados ou criar restrição física."
---

# GTS de 1963 não é cadastro instrumental de 1963

**Fonte metodológica:** Durre, Vose e Wuertz, *Overview of the Integrated Global Radiosonde Archive*, *Journal of Climate* 19(1), 53–68, **1º de janeiro de 2006**, seções 2a, 2c e 4, [DOI 10.1175/JCLI3594.1](https://doi.org/10.1175/JCLI3594.1). A versão integral indexada foi consultada por busca, mas o binário não foi autenticado nem recebeu SHA-256; `binary_sha256=null`.

O artigo descreve **um núcleo GTS processado no NCDC para 1963–1970**, outro acervo USAF para 1946–1973 e uso de fontes externas, incluindo **WMO Volume A de 2004**, para preencher nomes/países das estações. Também documenta a composição de séries sob múltiplos códigos de estação em certos casos. Trata-se de descrição **do sistema IGRA original**, não de documentação contemporânea de um lançamento individual. Não autoriza atribuir automaticamente ao perfil específico de Recife uma mensagem GTS recuperada, o mesmo sítio de 2014 ou o instrumento utilizado em 1963.

**Fonte institucional de escopo:** [página histórica da WMO sobre Volume A e catálogo de radiossondas](https://old.wmo.int/extranet/pages/prog/www/ois/volume-a/vola-hist-home.htm), HTML integral recuperado em **13/11/2026**, 29.556 bytes, SHA-256 `6c8b5b69b9f38c6c569a10b5a8ecd3572e6c5221e3e0ac2654d5540b38e8c56a`. A própria instituição diferencia o cadastro de estações do catálogo de **modelos de radiossondas, equipamentos de rastreio, estações de solo e correções de radiação**. O exemplar indicado nessa página é de julho de 2014, não de 1963.

**Vínculo material:** o arquivo original NOAA/IGRA de `BRM00082900`, já preservado no projeto com SHA-256 `0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc`, usa o código de origem `ncdc6301` no manifesto existente. Esse rótulo é consistente com a família histórica descrita, mas **sem a mensagem e o decodificador originais não prova o caminho operacional individual nem a localização do lançamento**. C149–C151 permanecem uma mesma família arquivística, não três instrumentos independentes.

**Grafo cumulativo:** métodos IGRA/2006 → código arquivístico NCDC → perfis C149–C151 → identidade operacional e metodologia de GPH de 1963 **PENDING** → covariâncias e transferência Recife→Conde **PENDING** → entrada eventual para o Castor **PENDING**. A evidência C193 é termoesférica de outra época, não uma calibração dos perfis. Estado `CONNECTED_PENDING_CALIBRATION`: nenhum sensor, coordenada histórica, hora real, erro padrão ou restrição geográfica foi inferido.

**Próximo teste falsificável:** recuperar a edição WMO No. 9, Volume A ou o catálogo de radiossondas efetivamente vigente em 1963 e ao menos uma mensagem TEMP/PILOT com a cadeia de decodificação dos níveis. Sem isso, o código do arquivo continua **indício de linhagem**, não prova completa da estação ou do instrumento.

**Reprodução:** `python3 tools/validate_igra_gts_1963_provenance.py` e `python3 -m unittest discover -s tests -p 'test_igra_gts_1963_provenance.py' -v`. O teste confronta a linhagem com o manifesto NOAA existente, impede retrodatação e proíbe conversão indevida de metadados em observação física.
