---
type: Story
title: "Três números, uma órbita que não fechava"
description: "Caderno 15: em 31 de dezembro de 1963, a linha NASA do objeto 529 reúne período e altitudes que divergem por dois minutos num teste gravitacional simplificado."
date: "2026-11-13"
summary: "O mesmo boletim que anunciava 89,2 minutos também imprimia apogeu de 335 km e perigeu de 333 km. O desencontro exige investigar quando e como cada coluna foi calculada, antes de usá-las para reconstituir 1963."
chapter: "15"
author: "Coruja · Caderno de investigação"
status: "Fac-símiles NASA confrontados; diagnóstico condicional CASTOR-G37, sem época instrumental autenticada nem inferência de reentrada"
---

# Três números, uma órbita que não fechava

O que fazer quando três números na mesma linha de um documento oficial contam histórias diferentes sobre o mesmo satélite? A pergunta aparece na página **5** do *Satellite Situation Report* da NASA de **31 de dezembro de 1963**. Ali, o objeto **1963 3C**, identificado hoje como **NORAD 529**, tinha período nodal de **89,2 minutos**, apogeu de **335 quilômetros** e perigeu de **333 quilômetros**.

Essa linha não registra o satélite que a NASA catalogou como decaído em **8 de novembro**, o **1963 3B / 528**. Registra um de seus companheiros de lançamento, ainda presente nas tabelas. Mesmo assim, ela importa para a investigação da esfera noticiada em Conde: se não entendermos a natureza dos números usados para reconstruir as órbitas, uma coincidência calculada pode adquirir a aparência enganosa de uma observação.

## A página e a conta

A fonte é a [edição NASA de 31/12/1963, página impressa 5, página 7 do PDF](https://ntrs.nasa.gov/api/citations/19640005618/downloads/19640005618.pdf#page=7). Os três valores aparecem juntos. A surpresa surge quando tentamos verificar se período e altitudes poderiam representar a **mesma órbita, no mesmo instante**, sob a aproximação elementar da gravitação de dois corpos.

Nessa aproximação, calculamos a distância média ao centro da Terra a partir da média entre apogeu e perigeu. **334 km** de altitude média correspondem a um período de aproximadamente **91,21 minutos**, e não a 89,2. A diferença entre a coluna impressa e o cálculo é de **cerca de 121 segundos**, pouco mais de dois minutos.

Não é uma comparação entre duas medições independentes. É um **teste de consistência condicionado** à suposição de que aquelas colunas representam grandezas compatíveis e contemporâneas. O período publicado é expressamente *nodal*; a relação de dois corpos empregada na triagem não representa, por si só, as convenções e perturbações utilizadas no cálculo histórico da NASA.

## A linha vizinha e a edição anterior

A mesma folha oferece um controle. Para o objeto **1963 3A / 527**, informa **94,6 minutos**, apogeu **530 km** e perigeu **461 km**. A conta simplificada devolve **94,52 minutos**: diferença de aproximadamente **4,6 segundos**.

E a [edição de 30/11/1963, na mesma página impressa](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7) trazia para o **529** período de **92,2 minutos**, apogeu de **390 km** e perigeu de **368 km**. O mesmo cálculo fornece **92,13 minutos**, a cerca de **4,2 segundos** do número publicado.

| Linha dos boletins NASA | Período impresso | Apogeu / perigeu | Período calculado* | Diferença |
| --- | ---: | ---: | ---: | ---: |
| 529, 30/11/1963 | 92,2 min | 390 / 368 km | 92,13 min | +4,2 s |
| 527, 31/12/1963 | 94,6 min | 530 / 461 km | 94,52 min | +4,6 s |
| **529, 31/12/1963** | **89,2 min** | **335 / 333 km** | **91,21 min** | **−120,7 s** |

*Modelo gravitacional de dois corpos, elementos simultâneos presumidos, raio terrestre equatorial convencional. Datas acima são **das edições**, não épocas comprovadas de observação.*

A distância de dezembro para o 529 não desaparece ao admitir somente o arredondamento do papel. Usando **±0,05 minuto** no período e **±0,5 km** nas alturas, a diferença ainda fica entre aproximadamente **−124,3 e −117,1 segundos**. Essas bandas expressam apenas precisão **de impressão**, não a incerteza dos instrumentos.

## O documento não é o céu

Seria tentador anunciar que a NASA publicou uma órbita errada. A conta **não autoriza** esse veredito. Ainda não sabemos se a altura e o período foram atualizados com observações da mesma época, se obedeciam às mesmas convenções, nem que correções de perturbação e processamento entraram na edição. Há várias explicações possíveis para a diferença, e os boletins, sozinhos, não permitem escolher entre elas.

Também seria impróprio usar os **121 segundos** como medida do arrasto atmosférico ou como correção automática para a trajetória do 528. O teste não recuperou hora, posição, estação rastreadora ou registro instrumental original. Ele detectou uma **incompatibilidade sob hipóteses explícitas** na representação compilada de um outro objeto.

A pergunta decisiva muda de lugar: **qual era a data e a convenção por trás de cada uma das três colunas do 529 em 31 de dezembro?** Um registro bruto com época UTC e definição dos elementos permitiria testar se estamos diante de valores de momentos diferentes, de definições diferentes ou de uma inconsistência editorial. Até lá, o mais importante é não transformar uma linha de catálogo em itinerário para Conde.

---

**Fontes e limites.** NASA, *Satellite Situation Report* de [30/11/1963, NTRS 19640002493](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7) e de [31/12/1963, NTRS 19640005618](https://ntrs.nasa.gov/api/citations/19640005618/downloads/19640005618.pdf#page=7), ambas na página impressa 5 / PDF 7; fac-símiles confrontados visualmente. Custódia documental [C241-L18](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json). Cálculo, constantes, intervalos de impressão e hipóteses reproduzíveis no [diagnóstico CASTOR-G37](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/CASTOR-G37_ssr_crossfield_screen.json), desenvolvido na [PR #471](https://github.com/franklinbaldo/conde-incident/pull/471). Os boletins compartilham cadeia de compilação; não são observações independentes. Nada aqui demonstra uma queda em Conde.
