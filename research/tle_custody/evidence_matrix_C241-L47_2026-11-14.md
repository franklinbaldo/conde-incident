---
type: Guide
title: 'C241-L47: cronometria fotográfica soviética em fonte NASA de novembro de 1963'
description: 'Três fascículos NASA digitalizados pela UAH e um resumo contemporâneo de equipamento óptico, sem promover valores genéricos a erro orbital do NORAD 528.'
---

# C241-L47: atrasos de obturador não são erro orbital

**Fonte preservada:** [*Space Intelligence Notes*, vol. 4, nº 11, novembro de 1963](https://digitalprojects.uah.edu/items/show/3372), Space Systems Information Branch, NASA Marshall Space Flight Center. A digitalização da University of Alabama in Huntsville contém **28 folhas**, **10.004.789 bytes** e SHA-256 `f953ffe533a7f6e0a3430c6381903be57dd98521523622e4b6e90c7830080318`. A **página impressa 24, índice PDF zero 23**, foi conferida diretamente por renderização da imagem digitalizada, não por OCR. Os fascículos [outubro](https://digitalprojects.uah.edu/items/show/3371) e [dezembro](https://digitalprojects.uah.edu/items/show/3373) também tiveram seus PDFs recuperados, hashes e páginas conferidos (manifesto `uah_soviet_camera_timing_C241-L47.json`). Os três são scans **sem camada textual extraível por `pypdf`**: nenhum resultado de busca textual negativa pode provar ausência de referência a um alvo no restante das páginas.

**Observação documental:** a seção *Tracking* da página 24 resume uma investigação de equipamento de fotografia de satélites artificiais, incluindo a fotocâmera **NAFA-3S/25-S**, cronógrafo 21-P, adaptador 1P-M e outros instrumentos. Os valores impressos são: atraso de **abertura 0,0022 ± 0,0002 s**, atraso de **fechamento 0,0002 ± 0,0002 s**; atraso do início do registro do cronógrafo a **210 V: 0,0268 s**, a **230 V: 0,0254 s**. O texto informa dependência da tensão e correção da hora de observação. Os sinais ± são transcrição editorial, **não** identificação verificada de desvio-padrão, distribuição de erros ou qualidade orbital. Não atribuir esses instrumentos ao NORAD 528.

**Genealogia, sem triplicar independência:** o digest da NASA cita *Dept. of Defense Intelligence Info.*, relatório nº **1521678463**, de **19/06/1963**, que por sua vez cita *Astronomicheskiy Zhurnal*, Moscou, nº 5, **maio de 1963**. Os dois elos anteriores ainda **não foram recuperados**. É um resumo contemporâneo de tecnologia soviética, não a folha de observação do 528, nem uma segunda medição independente de NORAD/SAO. Não há época instrumental do 528, estação, identidade de sensor, RA/Dec, resíduos, referencial, covariância ou reentrada geográfica. `THETA_UNCHANGED`; nenhuma restrição física ou Lean ativada.

**Reprodução:** `python3 -m unittest discover -s tests -p test_tle_uah_soviet_camera_timing.py -v`; `python3 tools/tle_uah_soviet_camera_timing_audit.py --verify-remote` com `pypdf==6.1.3` para hashes, páginas e ausência de camada textual. PDF não foi incorporado ao Git. O contrato registra transcrição e testes adversariais, não substitui leitura de fac-símile.

**Teste seguinte:** recuperar o artigo russo e/ou o relatório 1521678463 e, separadamente, uma observação instrumental de **1963-003B/NORAD 528** datada e identificada. Só nesse segundo caso haverá base para avaliar correções de tempo e calibrar erros relevantes à trajetória, com 527/529 como controles.
