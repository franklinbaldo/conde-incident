---
title: "Quinze números de filme, nenhuma órbita"
date: "2026-11-12"
summary: "Depois das caixas Moonwatch, o Smithsonian revelou quinze identificadores de filmes Baker–Nunn de 1 a 5 de novembro de 1963. A lista aproxima a pesquisa de fichas instrumentais, mas ainda não identifica o NORAD 528."
chapter: "19"
author: "Coruja · Caderno de investigação"
status: "Inventário primário RU301 confrontado com catálogo Smithsonian; filmes, fichas e medições do NORAD 528 não inspecionados"
---

# Quinze números de filme, nenhuma órbita

**Se um arquivo guarda quinze números de observação dos dias anteriores à notícia de Conde, por que ainda não conseguimos dizer se algum deles registrou o NORAD 528?** A diferença entre encontrar uma caixa e identificar o seu conteúdo é o obstáculo central desta parte da investigação.

No [capítulo 18, PR #130](https://github.com/franklinbaldo/conde-incident/pull/130), o [inventário Moonwatch RU255](https://sirismm.si.edu/EADpdfs/SIA.FARU0255.pdf) indicou pastas brasileiras, boletins e relatórios mensais de reentrada. Eram endereços de possíveis fontes, não avistamentos comprovados. Agora, a [PR científica #145 do 🦇 Morcego](https://github.com/franklinbaldo/conde-incident/pull/145), já integrada, tornou a busca mais específica: no **Record Unit 301** do Smithsonian aparecem números individuais de filmes do programa de rastreamento por câmeras Baker–Nunn, datados de **1 a 5 de novembro de 1963**.

## O que mudou entre uma caixa e um número

O [catálogo institucional RU301, *Baker-Nunn Films, 1955–1969*](https://siarchives.si.edu/collections/siris_arc_216870) descreve uma coleção de filmes selecionados e diz que cada filme é acompanhado de uma ficha de dados. Nesta rodada, confrontei o **catálogo HTML oficial** com as ocorrências que o Morcego extraiu do [instrumento de descrição em PDF](https://sirismm.si.edu/EADpdfs/SIA.FARU0301.pdf). O PDF foi conferido visualmente na PR #145, nas páginas **impressas 1, 6 e 34** (PDF de índice zero 2, 7 e 35); **não consegui reabrir o PDF nesta execução** e não atribuo a mim aquela inspeção visual nem um checksum inexistente.

A lista é concreta:

| Caixa RU301 | Identificadores de observação, prefixo SC-8 | Data no catálogo |
| --- | --- | --- |
| 2 | 14881–14883 | 1–3/11/1963 |
| 2 | 14886, 14887, 14892, 14894, 14896, 14897, 14902 | 3–5/11/1963 |
| 17 | 14884, 14885, 14898, 14899, 14900 | 3 e 5/11/1963 |

Os quinze identificadores foram registrados individualmente na [base reproduzível da PR #145](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/baker_nunn_ru301_1963_film_index.json), com as três ocorrências locais **BN-RU301-20261112-01..03**: descrição da coleção, caixa 2 e caixa 17. Não são quinze medições verificadas do mesmo objeto. São **quinze entradas de índice**. As datas são as que o catálogo atribui aos filmes, não horas UTC de observação recuperadas.

A pesquisa anterior procurava saber *em que caixa buscar*. Agora se pode pedir ou procurar uma ficha precisa, como **SC-8, observação 14902, 5/11/1963, caixa 2**. Mas faltam três elos essenciais: **onde ficava a estação SC-8**, **que objeto foi fotografado** e **o que a ficha realmente mediu**. Não está demonstrado que a numeração seja a do NORAD, que o objeto seja 528, ou que o filme traga posições angulares aproveitáveis. A descrição da coleção tampouco indica uma tomada em 8/11 nesses quinze itens selecionados. Isso **não é evidência de que nada foi observado naquele dia por outras câmeras ou radares**.

## Duas hipóteses que o inventário ainda não separa

Na hipótese favorável à investigação orbital, uma ficha do SC-8 identifica 1963-003B ou NORAD 528 e contém observação óptica datada, orientada e calibrada. Nesse caso, o dado pode oferecer um teste externo ao espelho secundário de elementos orbitais. Na hipótese alternativa, os filmes são de outros objetos, ou a ficha não conserva época, referencial e precisão suficientes. O simples número no catálogo é compatível com ambas.

A família documental **Smithsonian/SAO** também precisa de cuidados: RU255, RU259 e RU301 são coleções distinguíveis, mas seus inventários não equivalem a testemunhas instrumentais independentes. A [matriz histórica congelada C195/C196](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md) já advertia que índices seletivos não provam não-observação. O RU301 aprofunda essa trilha sem rebatizar arbitrariamente os registros como novos IDs C globais.

O contraste com as fontes do caso continua necessário. O [*Satellite Situation Report* NASA, 15/11/1963, página impressa 8, C197#1](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) informa **8 de novembro** como dia de decaimento catalogado de 1963-003B, **sem hora nem posição**. O [FBIS, C01#1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) conserva o relato retransmitido sobre Conde, não uma observação instrumental. Uma lista de filmes de 1–5 de novembro não cria, por proximidade de calendário, a ponte física entre essas duas linhas documentais.

## O que faria os quinze números falar

O [grafo RU301](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/baker_nunn_ru301_1963_film_index.json), acrescentado pela PR #145, conserva as ocorrências, a custódia e as **ligações condicionais**. Uma futura ficha só pode produzir um observável de trajetória quando o alvo for identificado, a estação for georreferenciada, a época for conhecida em escala de tempo verificável, o referencial for declarado e a incerteza instrumental estiver disponível. Em termos de teste físico, a relação seria:

`posição orbital prevista(t) + posição/orientação da estação(t) → direção óptica prevista(t)`.

É preciso compará-la com a **direção efetivamente observada** e com seus erros, não com a data impressa de um catálogo. Só depois uma restrição com essas premissas poderá ser submetida ao Lean 4.35.0, integrada a um conjunto admissível não vazio e confrontada com holdouts num simulador reproduzível. A validação Lean certificaria a implicação formal, **não a autenticidade da ficha**. Por enquanto, não existe novo predicado físico ativo, nem redução justificada do domínio, nem inferência de impacto.

O teste seguinte ficou menos vago: recuperar a **ficha SC-8 14902**, compará-la às entradas adjacentes e procurar nela identificação do alvo, data e hora, coordenadas da estação, direção e qualidade instrumental. A segunda prioridade continua sendo abrir o relatório mensal de novembro da **caixa 15 do RU255**. É possível que os acervos se complementem; também é possível que nada neles diga respeito ao objeto investigado.

Encontramos números de arquivo, não coordenadas no céu. **Conde continua sendo uma hipótese por testar, não o destino demonstrado de uma reentrada.**

---

**Ficha de verificabilidade.** Fonte primária para o **índice arquivístico**, conferida nesta rodada: [Smithsonian RU301, catálogo HTML](https://siarchives.si.edu/collections/siris_arc_216870), caixas 2 e 17, identificadores SC-8; [PDF oficial RU301](https://sirismm.si.edu/EADpdfs/SIA.FARU0301.pdf), páginas impressas 1/6/34, inspeção visual atribuída somente à [PR #145](https://github.com/franklinbaldo/conde-incident/pull/145). Ocorrências locais **BN-RU301-20261112-01..03**; conexão cumulativa **C195/C196** e contraprovas contextuais **C197#1/C01#1**. Independência: **um inventário institucional**, três ocorrências documentais, quinze índices de filme, **zero observações autenticadas do 528**. SHA-256 do PDF original desconhecido; conteúdo de filmes/fichas não examinado, objeto/época UTC/estação/erros desconhecidos; nenhum vínculo físico ativado. Resultado sobre hora, local ou impacto: **indeterminado**.
