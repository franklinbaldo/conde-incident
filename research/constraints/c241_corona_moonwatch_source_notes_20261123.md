---
type: Guide
title: CORONA e Moonwatch como fontes para o caso Conde
description: Suplemento documental sobre a cápsula do NORAD 637, os registros observacionais Moonwatch e um controle de reentrada de 1964.
---

# CORONA e Moonwatch como fontes para o caso Conde

Suplemento à [matriz histórica](../evidence_matrix_C001-C238_2026-11-11.md), blob `a7978c3a75a153b16ab70118a92c434bba674cb7`. A leitura dirigida, em 23/11/2026, fornece localizadores, uma divergência de data e um candidato a controle. Nas passagens consultadas, não foi localizada observação de 1–9/11/1963 atribuída ao 528 ou ao 637, nem hora independente do relato de Conde ([#871](https://github.com/franklinbaldo/conde-incident/issues/871)). A leitura dos livros não cobre as fichas originais.

## NORAD 637 e a cápsula de filme

Jonathan McDowell, Apêndice B de *Eye in the Sky*, linha 70, pp. impressas 238–239 (PDF 254–255), vincula a missão `9058A` ao **KH-5 ARGON**, câmera A-11, **Agena D 1169**, operação **1561 PELICAN PETE**, designação `1963-35` e lançamento em 29/08/1963 às 20:31 GMT. O identificador da peça `1963-035A / NORAD 637` vem do cruzamento catalográfico já registrado em C92. O quadro dá **1.201 kg após a inserção orbital**, conforme a nota d da p. 246, e registra **recuperação aérea da cápsula em 01/09/1963 GMT**, conforme a nota g. A massa refere-se à configuração inicial em órbita e já aparece no [registro de física terminal](oglobo_cutoff_and_crater_physics.json).

O [GCAT, entrada A00386](https://planet4589.org/space/gcat/data/cat/auxcat.html), também compilado por McDowell, registra para a **SRV 604** separação em `1963 Sep 1 2250?` e término em `1963 Sep 2 2330`. A [tabela 2 do relatório USGS depositado no NTRS](https://ntrs.nasa.gov/api/citations/19990009049/downloads/19990009049.pdf) lista o intervalo fotográfico da missão como 29/08–01/09. O fim da aquisição de imagens não resolve a data da recuperação. As duas cronologias publicadas colocam a cápsula fora do conjunto orbital antes de novembro. A divergência diária fica aberta até consulta ao registro de recuperação da SRV 604, com evento, hora e convenção explícitos.

## Moonwatch e o que procurar no Smithsonian

McCray, *Keep Watching the Skies!*, pp. 195 e 197–198, descreve o rastreio de objetos perdidos e de reentradas e os testes da **Operation 2050** (maio de 1960). Os melhores observadores obtinham resíduos angulares de cerca de **5 minutos de arco**, com desempenho variável por equipe e instrumento. A previsão de referência usava dados Baker–Nunn e radar. O residual mede a diferença entre observação e previsão, incluindo os erros dos dois lados. A fonte da nota 28 é Gustav A. Bakos, *A Comparative Study of Accuracy of Satellite Observations*, *Bulletin for Visual Observers of Satellites*, n.º 12, junho de 1961, pp. 1–5. O artigo original ainda precisa ser localizado para recuperar amostra, estatística, equipamento e referência de ajuste.

Na p. 210 e nota 58, McCray remete a um rascunho de julho de 1963 do *Moonwatch Manual*. A numeração citada no livro é caixa 40, MW/SI. O [guia atual RU255](https://sirismm.si.edu/EADpdfs/SIA.FARU0255.pdf), série 4, p. 28, localiza um rascunho de 1963 na **caixa 14**. A equivalência entre os exemplares precisa de folha de rosto ou inspeção do conteúdo. As instruções de 1962–63 figuram na caixa 15, p. 29, e as fichas de coordenadas das estações na caixa 16, p. 30.

Na p. 228, McCray data o início informal da rede de pilotos de Herbert Roth em 1963 e a associação formal com Moonwatch em 1965. O guia RU255, série 8, pp. 37–44, acrescenta que os primeiros relatos provavelmente vieram sobretudo da United Air Lines. Para a [#1093](https://github.com/franklinbaldo/conde-incident/issues/1093), examinar primeiro o relatório mensal de novembro de 1963 e as pastas de equipes brasileiras (caixas 15 e 10). A caixa 21 é uma rota complementar, condicionada à data, rota, hora e origem do relato. Os localizadores de equipe e de relato já constam do [grafo RU255](moonwatch_ru255_1963_archival_graph.json) e do [censo Moonwatch/WSRN](../archive/moonwatch_wsrn_1963_source_census_LONTRA_R84.json).

## Controle proposto para a reentrada de 1964

A nota 6 do Apêndice B, p. 246 de *Eye in the Sky*, associa o voo 78 à reentrada venezuelana de 26/05/1964. A linha 78 identifica a missão **CORONA 1005**. O [histórico desclassificado do NRO, p. 152](https://www.nro.gov/Portals/135/documents/foia/docs/HOSR/SC-2017-00006a.pdf), descreve previsão inicial no Pacífico e revisão para a Venezuela. O [histórico desclassificado da CIA, p. 8-3](https://www.cia.gov/readingroom/docs/CIA-RDP89B00980R000500070001-2.pdf), relata cinco objetos luminosos observados em Maracaibo, detecções de radar posteriores e a cápsula recuperada perto de La Fría. São reconstruções institucionais retrospectivas, com possível dependência dos mesmos registros operacionais.

Para a [#647](https://github.com/franklinbaldo/conde-incident/issues/647), a missão é candidata a controle de cronologia e geografia. Recuperar a emissão, o alvo e a região de cada previsão, o relatório original do avistamento com relógio e a identificação das detecções de radar. O lugar da recuperação da cápsula é um observável distinto do lugar da fragmentação. O fuso da hora narrativa, a incerteza das previsões e a correspondência entre os ecos e os objetos avistados permanecem desconhecidos. A transferência de erro quantitativo para 1963 dependeria de justificar a comparabilidade de sensores, horizonte de previsão e configuração física.

## Ocorrências e vínculos com a matriz

| Ocorrência documental | Vínculo | Dado e conexão | Estado |
| --- | --- | --- | --- |
| Apêndice B, linha 70 e notas d/g | C92–C95 | `massa_637_pos_insercao_kg = 1201`; `massa_637_novembro_kg = null`. A recuperação da SRV condiciona a composição em novembro. A precisão da massa e o instante de pesagem não são informados. | Configuração inicial documentada em fonte secundária. Massa terminal pendente. |
| Apêndice B, linha 70 × GCAT A00386 | C95 | `data_recuperacao_srv_604` tem duas leituras de dia. A ausência da cápsula em novembro é compatível com ambas. Os dois registros têm o mesmo compilador e a linhagem de cada data ainda precisa de apuração. | Divergência preservada. Hora operacional desconhecida. |
| McCray, pp. 197–198 e nota 28 | C195–C196; #647 | `residuo_angular_moonwatch` depende tanto da observação quanto da previsão de referência. Valor narrado de cerca de 5′ para os melhores; `sigma_angular_528_637 = null`. | `CONNECTED_PENDING_CALIBRATION`. |
| McCray, p. 210 e nota 58, p. 228; RU255 | C195–C196; #1093 | Manual e fichas podem ligar uma observação a estação, tempo e procedimento; um relatório de piloto exige identificação de hora, local e origem. | `SOURCE_CATALOG_ONLY` para as pastas. Observações dos alvos ainda sem confirmação. |
| Voo 78 / missão 1005, históricos NRO e CIA | #647 | A comparação exige previsão emitida antes do evento e observável posterior com definição compatível. `erro_tempo_1005 = null`; `erro_local_1005 = null`. | `CONNECTED_PENDING_CALIBRATION`. |

Nenhuma dessas ocorrências fornece hora, direção ou vetor orbital novo para 528 ou 637 em 1–9/11/1963.

## Cópias consultadas

- Dwayne A. Day, John M. Logsdon e Brian Latell (orgs.), *Eye in the Sky: The Story of the Corona Spy Satellites*, Smithsonian Institution Press, 1998, ISBN 9781560987734. SHA-256 do PDF consultado `931b5aa1594742e3f2050c6bdb101d740d6a66706cf2523f6fa34ad4fdbfc38f`. Linha 70 conferida no fac-símile renderizado; notas do apêndice conferidas na camada textual.
- W. Patrick McCray, *Keep Watching the Skies! The Story of Operation Moonwatch and the Dawn of the Space Age*, Princeton University Press, 2008, ISBN 9780691128542. SHA-256 do PDF consultado `3c75077f605e419f79252a1d8fb0b09a1b6fe8c38adf02dcce88a10e40bc92f9`. Passagens e notas conferidas na camada textual, com inspeção visual das pp. 197 e 228.
