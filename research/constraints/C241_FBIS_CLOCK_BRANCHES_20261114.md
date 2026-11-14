---
type: Experiment
title: "C241-P48: os dois relógios possíveis do cabeçalho Tupi/FBIS"
description: "Pré-registro da calibração independente de horas FBIS; horário de verão da Guanabara e limite superior condicional do relato, sem hora de queda"
experiment_id: C241-P48
verification_status: UNRESOLVED_ZERO_INDEPENDENT_1963_ANCHORS
---

# O relógio impresso '2330' não é a hora da suposta queda

**Issue responsável:** [Conde #886](https://github.com/franklinbaldo/conde-incident/issues/886), prioridade 94. Esta é uma entrega **parcial** dessa issue, não seu encerramento. O requisito de pelo menos dez despachos FBIS de 1963 ancorados em registros horários externos permanece **0/10**; nenhuma documentação de 1972 vale como âncora de transmissão de 1963.

## Fonte e premissas

O fac-símile do boletim FBIS atribuído à Rádio Tupi de 8/11/1963 imprime o cabeçalho 'RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 2330 8 NOV 63 W' e o rodapé '9 NOV 111A RWS/GY'. Uma cópia digital de 126.624 bytes possui SHA-256 '63654bcd90c0515f30e31ed511a12a05f170ff4470e3d8a6f40fca12012a1adb'. Fonte: [fac-símile EOP-UAP-D001](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), C01 e [CGEO-18](../geo/cgeo18_fbis_city_center_phrase.md). É **um relato de rádio traduzido**; não existe nele uma medição de reentrada ou de hora da ocorrência. 'W', '111A' e 'RWS/GY' **não estão decodificados** nesta auditoria. Não ler '111A' como '11:10', nem inferir que o rodapé necessariamente representa hora de arquivamento.

O [Decreto federal nº 52.700, de 18/10/1963, art. 1º](https://www2.camara.leg.br/legin/fed/decret/1960-1969/decreto-52700-18-outubro-1963-393059-publicacaooriginal-1-pe.html) estabeleceu, entre 23/10/1963 e 29/02/1964, **60 minutos de hora especial na Guanabara**, entre outras unidades; Bahia **não** está incluída. Assim, em 8/11 a Guanabara tem hora civil **UTC−2**, e a Bahia **UTC−3**. Isto corrige a conversão ingênua que equipara a hora civil do Rio à da Bahia nessa data. A lei não informa qual relógio o FBIS empregava nos cabeçalhos.

## Três ramos, preservados sem preferência

| Hipótese para '2330 8 NOV 63' | Transmissão condicional em UTC | Hora civil na Bahia | Limite superior do evento relatado |
| --- | --- | --- | --- |
| 'GMT', como hipótese de padronização FBIS | 08/11 23h30Z | 08/11 20h30 | até 08/11 23h30Z, **somente se** o evento precedeu aquela transmissão |
| 'RIO_LOCAL', como hipótese de relógio civil da Guanabara | 09/11 01h30Z | 08/11 22h30 | até 09/11 01h30Z, **sob a mesma condição** |
| 'OTHER_UNVERIFIED', se o campo significar outro relógio ou procedimento | 'null' | 'null' | 'null' |

O suposto evento poderia ter ocorrido muito antes do programa e o boletim poderia ter processado o programa mais tarde. O horário do programa é no máximo **limite superior condicional do relato**, nunca tempo de impacto ou medição da órbita. A história institucional [CIA FBIS, maio de 1972, Part III](https://www.govinfo.gov/content/pkg/GOVPUB-PREX3-PURL-gpo254964/pdf/GOVPUB-PREX3-PURL-gpo254964.pdf) confirma a existência do Wire Service e sua operação, mas **não** fornece nestas passagens uma regra verificada para '2330' ou '111A'.

## Cruzamento nominal de plano: uma implicação condicional falsificável

A [tabela experimental #892](../statistics/C241_CONDITIONAL_PLANE_WINDOWS_20261114.md) dá, para **uma câmera proxy moderna de 2022**, uma raiz nominal do plano NORAD 528 em **08/11 20h44 da Bahia** (23h44Z). Portanto:

- Sob 'GMT', a raiz nominal estaria **14 minutos depois** da hora impressa interpretada como transmissão.
- Sob 'RIO_LOCAL', estaria **106 minutos antes** da transmissão interpretada.
- Com fuso do cabeçalho desconhecido, a comparação permanece 'UNRESOLVED'.

Essas diferenças são *ordens temporais calculadas*, não probabilidades nem exclusões: a raiz usa uma posição de câmera moderna que **não foi demonstrada como local de Conde em 1963**; tampouco é uma observação da fase real do 528. A incerteza da extrapolação orbital de 12 dias e do relógio não foi calibrada para transformar os 14 minutos em um corte físico. No segundo ramo, uma coincidência antes da transmissão tampouco demonstra queda ou que a esfera fosse um satélite. O limite NASA de decaimento de dia inteiro não fixa hora/local.

## Critério pré-registrado para substituir 'UNRESOLVED'

Antes de contar resultados, exigir **dez ou mais itens FBIS distintos de novembro de 1963**, cada qual com URL, página e SHA do FBIS, mais URL, página, SHA e cadeia independente de uma **fonte contemporânea que determine a hora efetiva da mesma transmissão**. Correspondência do tópico geral ou repetição da mesma linhagem não conta. Para os dez primeiros itens verificáveis, confrontar 'GMT' e 'RIO_LOCAL' contra hora externa em UTC, com margem operacional pré-fixada de **até cinco minutos**, apenas nas emissoras e datas em que o UTC−2 da Guanabara se aplica. Só escolher um ramo quando **todos** os dez ou mais itens o sustentarem e nenhum contradisser; caso contrário retornar 'UNRESOLVED'. Esta margem **não** é sigma instrumental.

O manifesto [fbis_1963_clock_anchors.json](fbis_1963_clock_anchors.json) está vazio e não possui exemplos sintéticos disfarçados de observações. [Gerador e auditor](../../tools/fbis_1963_clock_branches.py) exporta [JSON derivado](fbis_1963_clock_branches.json) e compara bytes com '--check'. Os testes incluem controles sintéticos negativos que **não são inseridos** no manifesto histórico.

**Saída para Castor (#870):** consumir os três ramos e o indicador 'orbit_exclusion_licensed=false', nunca selecionar fuso por conveniência para ajustar a simulação. **Para Lontra (#871):** preservar cabeçalho e rodapé literais enquanto a fonte comparável ainda não for encontrada. **Estado:** 'THETA_UNCHANGED'; nenhuma prova Lean nova é legitimada por estas premissas.
