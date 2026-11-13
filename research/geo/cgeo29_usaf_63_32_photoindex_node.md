---
type: Guide
title: 'CGEO-29: nó MI-1850 no leitor oficial de fotoíndices USAF'
description: 'Custódia verificável de um nó de árvore, separada da aquisição do fotoíndice e da data de captura'
---

# CGEO-29: alternativa oficial para procurar o fotoíndice de Esplanada

**Pergunta:** há uma ocorrência individualizada para a folha MI-1850, Esplanada BA/SE, entre os fotoíndices digitalizados do SGB? E a ocorrência pode ser confundida com a campanha PETROBRAS 53 D nominalmente de 1961?

Em **13/11/2026**, adquiri uma resposta HTTP 200 do leitor oficial da coleção [Fotoíndices USAF](https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF). O HTML integral tinha **585.747 bytes**, SHA256 `02bc816f4c213f854dc3af119a3c840c3eb745fe3c2e9607a7d53ebe2c97d58b`. No componente `div#T1`, foram encontrados **1.809 rótulos de árvore**; na posição zero-based 679, aparece literalmente:

> 1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI

O nó está custodiado no [excerto HTML original](evidence/cgeo29_usaf_1850_node.html), com SHA256 `001787e5b6b26dd457a464b64740cb4de4f680956eba3ee0d20313db03206652`. A página do leitor declara o título *Fotoindices da USAF - Lote 32A - DocReader Web*. O nó individualiza **uma entrada de índice de fotos dos EUA (USAF)** para a **mesma folha cartográfica MI-1850** do catálogo PETROBRAS 53 D (CGEO-26). O CIM aparece com ponto na fonte `SC.24-Z-C-VI`, contra `SC-24-Z-C-VI` no catálogo anterior; isso é uma normalização gráfica de referência à folha, **não prova de mesmo voo, fotograma, cobertura ou data**.

**Nova conexão:** CGEO-27 confirmou quatro coleções oficiais; CGEO-28 demonstrou que preencher o campo de texto não confirma uma pesquisa. Agora temos um *nó específico de navegação* no ramo `FotoUSAF`, não apenas uma página de formulário ou uma transcrição em site de terceiros. O nó oferece outra rota documental, distinta da PETROBRAS, para procurar um fotoíndice que possivelmente permita testar cobertura urbana. Não é um segundo testemunho do incidente de 1963.

**Limites de aquisição:** o HTML foi obtido e verificado, mas o nó não foi selecionado no leitor, a imagem do fotoíndice não foi baixada, nenhum fotograma ou negativo foi adquirido, nenhuma legenda de faixa/voo foi inspecionada e **não foi verificada data de exposição**. `63-32` é o código impresso do projeto e não pode ser convertido em dia/ano da imagem sem metadado original. Não se sabe sequer se a imagem cartográfica representa a posição do Centro de Conde. Um rótulo em árvore também não comprova posse atual de original físico.

**Reprodução independente:** `python3 tools/cgeo29_usaf_photoindex_locator.py` confere contrato, excerto, folha e arestas cumulativas sem internet. Com os bytes reais adquiridos em separado, `python3 tools/cgeo29_usaf_photoindex_locator.py --source-html /caminho/FotoUSAF_root.html` faz replay do HTML integral, conferindo SHA256, contagem de nós, índice exato e unicidade. O teste integral foi executado nesta rodada com os bytes realmente baixados; o CI isolado só pode validar o excerto armazenado, não a captura HTTP ausente da árvore Git.

**Próximo teste falsificável:** navegar ao nó `1850 Projeto USAF 63-32`, obter a imagem original do fotoíndice, registrar SHA256, escala, legenda, direitos de reprodução, IDs de faixa/fotograma, data de voo e footprint. Só com isso poderemos procurar marcos de 1958 e confrontar o Centro de Conde em 1963. `historical_center_geometry=null`, `event_position_1963=null` e `can_constrain_orbital_reentry=false` permanecem.
