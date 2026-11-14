---
type: Guide
title: 'CGEO-40: terceira rota de custódia para o mapa IOCS 15 (AHEx)'
description: 'Registro físico no Arquivo Histórico do Exército, sem confundir catálogo indexado com fac-símile adquirido.'
---

# CGEO-40 | Mapoteca do AHEx: IOCS 15 (1912)

O [catálogo oficial da Mapoteca do Arquivo Histórico do Exército](https://www.ahex.eb.mil.br/images/DDA/2023/Atendimento_ao_Publico/Catalogo_Mapoteca_Completo.pdf), gerado em **4 de abril de 2023**, traz na página **125/196** a entrada **05.36.334**: módulo **5**, gaveta **36**, mapa **334**, título **Mapa da Bacia do Rio Itapicurú, Estado da Bahia** e ano **1912**. Descreve objeto impresso, colorido, com escala, legenda, convenções, papel comum telado, em bom estado, medindo **87 × 67,5 cm**.

A [ficha anterior do Arquivo Nacional](https://www.gov.br/arquivonacional/pt-br/servicos/copy_of_instrumentos-de-pesquisa/bhering-final-14-fev-13.pdf), **F4.0.MAP.448**, associa título equivalente à publicação IOCS nº **15** (1912), 1:500.000, dimensões catalogadas **64 × 89 cm**. O [Museu da República](https://atom-museurepublica.museus.gov.br/index.php/mapas-2) também arrola a obra na subsérie **BR RJMRAHI EP-IC-MA** (CGEO-39). Esses são **três caminhos de custódia documental**, não três levantamentos autônomos.

## O que foi de fato verificado

A indexação textual da URL institucional expõe a linha **05.36.334**. Na tentativa de aquisição em 14/11/2026, o transporte TLS apresentou certificado expirado e o teste exclusivamente diagnóstico com verificação TLS desabilitada recebeu **HTTP 403**. **Nenhum PDF ou fac-símile AHEx foi adquirido**, nenhum SHA256 pode ser atribuído e nenhum pixel foi inspecionado. O próprio catálogo, não o mapa, é a evidência indireta. O número **05.36.334** é referência do catálogo, não localização espacial.

A diferença de dimensões entre AHEx (87 × 67,5 cm) e Arquivo Nacional (64 × 89 cm) pode decorrer de corte, medição, suporte, montagem, exemplares ou edição; **não prova qualquer dessas explicações**. Sem comparar os exemplares, não se identifica a identidade física ou editorial. A data do catálogo (2023) não é a data de produção de 1912.

## Próximas provas e limites

Obter fac-símile e cota confirmada junto ao AHEx; conferir frente, verso, cartucho, autoria, folha e vestígios de impressão; comparar com o Arquivo Nacional e IBRAM, verificando alterações cartográficas antes de georreferenciar. Esse contato **não foi efetuado** nesta rodada.

Contrato: `research/geo/cgeo40_ahex_iocs15_holdings.json`. Auditor: `python3 -m tools.cgeo40_ahex_iocs15`; controles negativos: `tests/test_cgeo40_ahex_iocs15.py`. O CI executa apenas validações **offline**, não reivindica replay HTTP ou PDF.

A referência não estabelece cobertura de Conde, centro urbano em 1963, datum, incerteza espacial ou posição da alegada queda. Nenhuma restrição orbital é ativada. O [fotoíndice USAF 63-32, issue #558](https://github.com/franklinbaldo/conde-incident/issues/558) continua uma família documental distinta.
