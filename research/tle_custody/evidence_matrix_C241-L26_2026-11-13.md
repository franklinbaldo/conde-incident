---
type: Guide
title: "C241-L26: precisão de rastreamento em 1963 e a data de decaimento do 528"
description: "Quatro fac-símiles auditados; capacidade instrumental, registro terminal e controle de não atribuição ao objeto."
---

# C241-L26: o que significa 8 de novembro de 1963?

**Pergunta do proprietário:** a NASA/NORAD rastreava com precisão suficiente para que o dia de decaimento do objeto `1963 3B` (NORAD 528) deva receber peso científico maior do que uma simples extrapolação gráfica? **Resposta documental:** o dia é um registro histórico contemporâneo forte, porém seu método de determinação e erro específico seguem não recuperados. Não há base para transformar precisão nominal de câmera em hora exata de reentrada.

## Quatro fontes com bytes conferidos

| Ocorrência | Fonte contemporânea, página | Observável e status |
|---|---|---|
| C241-L26:DAY_528 | [NASA *Satellite Situation Report*, vol. 3 nº 22, 15/11/1963](https://ntrs.nasa.gov/citations/19640001198), PDF p. 10, p. impressa 8 | Linha de objeto **1963 3B**, coluna **DECAY = 8 NOV 63**. `CONTEMPORANEOUS_CATALOG_DECAY_DAY_NOT_INSTRUMENTAL_FIX`. É dado publicado, não medida cronometrada de impacto. |
| C241-L26:SAO_CAMERA_CAPABILITY | [Relatório presidencial *Aeronautics and Space Activities, 1961*](https://www.nasa.gov/wp-content/uploads/2024/01/presrep1961.pdf), PDF p. 75, p. impressa 73 | As câmeras Baker–Nunn da rede SAO anunciavam capacidade de **4 segundos de arco** de posição angular e **2 milissegundos** de tempo. Não diz que uma câmera fotografou o 528; números são do equipamento, **não** σ de uma órbita ajustada. |
| C241-L26:SPADATS_1963_NETWORK | [NORAD/CONAD, *Historical Summary July–December 1963*](https://nsarchive.gwu.edu/document/29915-document-11-noradconad-historical-summary-july-december-1963-confidential), p. impressas 54–59 | SPADATS reunia Spacetrack da USAF e SPASUR da Marinha; 17 Baker–Nunn nos planos/censo (4 USAF, 1 Canadá, 12 SAO), porém a integração e transferência das câmeras ainda enfrentavam negociação. Cold Lake funcionava sob condições de visibilidade, Prince Albert e Trinidad contribuíam parcialmente, Diyarbakir assumiu operação em 1963. **Nenhum vínculo instrumental específico com 528 na fonte.** |
| C241-L26:COMPARISON_COSMOS94 | [NORAD *Weekly Intelligence Review*, 12/11/1965, nº 46/65](https://www.archives.gov/files/declassification/iscap/pdf/2009-068-doc102.pdf), PDF p. 3, p. impressa 6 | **Outro objeto**, Cosmos 94 / SPADATS 1636. Radar Shemya o detectou na volta 127 e não na 128; análise preliminar Diyarbakir deu suporte a deórbita na volta 128. NORAD inferiu impacto **provável** 15–20 minutos após passagem no equador 05/11/1965 06:28Z. Demonstra *método possível*, não desempenho medido para 528 nem para decaimento natural (Cosmos 94 foi deorbitado intencionalmente). |

Os quatro downloads examinados em 13/11/2026 têm bytes/SHA-256 registrados no [ledger tipado](tracking_precision_1963_C241-L26.json), e o [auditor](../../tools/tle_1963_tracking_precision_audit.py) exige correspondência exata ao revalidar as cópias. Não foram versionados PDFs binários, nem presumida equivalência entre duas variantes de bytes. O caso Cosmos 94 demonstra que, **em outro episódio e dois anos depois**, NORAD podia combinar observações positivas e negativas de radares com cálculo de revoluções e previsão temporal; não mede a precisão da data de 1963 para o 528. Um relato de ausência em uma passagem tampouco é demonstração automática de reentrada: dependem sensores, campo de visão e previsão.

## Grafo cumulativo e uso futuro

- **Variável:** `latent_reentry_calendar_day_528` associada à ocorrência `C241-L26:DAY_528` por `catalog_reporting_day`. Estado `CONNECTED_PENDING_METHOD_AND_ERROR`. A data do boletim, 15/11, é diferente do dia catalogado, 08/11; nenhuma delas é a época de uma observação instrumental individual conhecida. A zona temporal da data catalogada não é expressa na tabela.
- **Variáveis candidatas:** `possible_sensor_accuracy_prior`, `provenance_sensor_candidate_graph` e `historical_detection_method_comparison`. Todas `CONTEXT_ONLY_NOT_ACTIVATED`. A precisão 4 arcsec/2 ms é capacidade publicizada para uma rede, não probabilidade de presença/ausência do 528, erro de altitude, matriz de covariância ou erro da estimativa terminal.
- **Cadeias não independentes:** as publicações NASA com dados NORAD/SAO não equivalem a três sensores; espelhos modernos dos mesmos parâmetros também não são confirmações instrumentais independentes. Para os 527/528/529, identidade/código da estação, latitude/longitude/datum, registro bruto de alcance/ângulo/tempo, época UTC, definição de σ, frame, ajuste orbital e resíduos permanecem **`NOT_RECOVERED`**.
- **Ponte física pendente:** documento prévio de previsão de decaimento com seu intervalo de erro, observações de passagem/ausência datadas, ficha de cálculo SPADATS de 528, arquivos de sensor com código de objeto e relógio, ou metodologia histórica que explique como se determinava `DECAY`. Só então confrontar com dinâmica (atmosfera/área-massa/atitude) e registrar o resíduo de uma previsão independente. Usar a mesma data como ajuste e “validação” seria circular.

**Resultado:** quatro fontes documentais verificadas e quatro novas arestas rastreáveis; zero rastros instrumentais identificados do 528, zero σ específica, zero estreitamento numérico legitimado. A evidência aumenta a importância de testar um modelo contra o **dia catalogado**, mas não autoriza chamar a reentrada de observada com precisão horária ou localização comprovada. A causa e o lugar do caso Conde permanecem indeterminados.

**Reprodução:** `python3 -m unittest discover -s tests -p test_tle_1963_tracking_precision_audit.py -v`; `python3 tools/tle_1963_tracking_precision_audit.py --source-dir <diretório-com-os-quatro-PDFs>`; workflow auditado no HEAD da PR.
