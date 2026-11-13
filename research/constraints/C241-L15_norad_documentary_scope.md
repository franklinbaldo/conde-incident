---
type: Guide
title: 'C241-L15: relatórios NORAD sobre 687/688/943 não medem o objeto 528'
description: 'Compilação tipada de contexto documental MOR em Lean, protegendo identidade, cronologia e proveniência sem ativar restrições orbitais.'
---

# C241-L15: escopo dos relatórios NORAD contemporâneos

**Objetivo verificável.** Integrar no Lean as cinco ocorrências do [crosswalk documental de Abelha](../../public/data/conde-norad-context.json), entregue pela [PR #225](https://github.com/franklinbaldo/conde-incident/pull/225), sem criar ligação entre IDs `MOR-NOR-*`, ocorrências `Cnn#n`, nem afirmar que tais documentos mediram o NORAD 528. É contexto de proveniência e contraexemplo de atribuição indevida, não uma restrição física de trajetória.

**Evidências e interpretação.** O memorando NASA/NORAD de 16/01/1961 registra política de intercâmbio de dados, não identificação do instrumento que mediu o 528. Relatórios NORAD de 12 e 14/11/1963 citam Sputnik 46 e os objetos **687/688**, não 528. Dois documentos catalogados na coleção com data de **30/11/1963** exibem em seus próprios originais a data **30/11/1964**, sendo um referente ao **943**. A fonte de observação do 528 permanece desconhecida. Hash individual dos PDFs originais é `null` neste crosswalk; o SHA-256 existente autentica a **auditoria documental derivada** do Morcego, não os PDFs.

**Linhas conectadas.** `MOR-NOR-20261112-01` a `-05` preservam namespace independente. C197#1 e C198#1 são **referências contextuais** presas ao snapshot de matriz `a7978c3a75a153b16ab70118a92c434bba674cb7`, linhas 905/906; não são provas de instrumentação ou medidas independentes do mesmo evento. A cadeia tipada consumível está em `formal/Conde1963/NoradContext.lean`, gerada por `formal/scripts/compile_norad_context.py` a partir do export auditado, não editada à mão.

**Teste adversarial.** `python3 -m unittest discover -s formal/tests -p 'test_norad_context.py' -v` rejeita novo `528` na lista de IDs, promoção de campo `physical_528_constraint`, mistura `MOR`/`Cnn`, SHA inventado, data 1963 promovida indevidamente e referência de matriz sem snapshot. A compilação Lean roda no CI; nenhuma prova de posição, horário ou queda foi criada.

**Consequência científica.** O grafo ganha antiatribuição explícita. `NORAD_528_TRACKING_SENSOR`, `RAW_TRACKING_VECTOR`, `FRAME_1963` e `COVARIANCE_528` continuam sem fonte primária e **não** recebem limite inferido. Domínio de simulação Θ: inalterado; nenhuma variável física eliminada. Para uma restrição orbital efetiva, exigir documento primário com ID 528, época UTC, instrumento, frame, unidades e modelo de incerteza.
