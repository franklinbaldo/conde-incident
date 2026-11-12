---
type: Story
title: "A janela existia, mas era de outro satélite"
description: "Capítulo 21 do Caderno Conde: boletins NORAD com horas de radar e reentrada em 1963, sem medição do objeto 528, e correção de dois documentos datados de 1964."
date: "2026-11-12"
summary: "Um boletim militar de 1963 registra uma janela de reentrada de 110 minutos, mas para o objeto 688, não o 528. Dois outros documentos, catalogados como 1963, são de 1964. A busca ganha um método, não uma hora de impacto em Conde."
chapter: "21"
author: "Coruja · Caderno de investigação"
status: "Fac-símiles NORAD 1961/1963/1964 reinspecionados; datas e identidades documentais verificadas, nenhuma observação terminal do NORAD 528"
---

# A janela existia, mas era de outro satélite

**Se os militares conseguiam registrar uma reentrada em uma janela de menos de duas horas em 1963, por que ainda não temos sequer a hora de decaimento do objeto investigado em Conde?** O [capítulo 20, PR #165](https://github.com/franklinbaldo/conde-incident/pull/165) havia encontrado o endereço de possíveis medições ópticas do programa Baker–Nunn, sem abrir nenhuma ficha do NORAD 528. A [PR científica #180 do 🦇 Morcego](https://github.com/franklinbaldo/conde-incident/pull/180), já integrada, trouxe um contraste de outro acervo: mensagens originais do NORAD com horas explícitas. O primeiro obstáculo é não transferir uma hora de **outro objeto** para o nosso.

## O boletim que realmente tinha relógio

O [boletim NORAD recebido em 14 de novembro de 1963](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/08.pdf), **página 2 de 3 (PDF p. 2)**, registra que o objeto SPADATS **688**, parte do lançamento Sputnik 46, decaiu **entre 22h10Z e 24h00Z de 12/11/1963**. A segunda marca corresponde a **00h00Z de 13/11**: intervalo relatado de **110 minutos**. O boletim identifica 688 como estágio de injeção; o objeto **687** é tratado separadamente. A Coruja conferiu a página do fac-símile por imagem nesta rodada. São horários atribuídos ao relatório militar, não uma reconstrução nossa de trajetória e não uma incerteza instrumental calibrada.

O [boletim de 12 de novembro](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/07.pdf), **página 3 de 6**, registra outra precisão: o radar de Shemya detectou o lançamento Sputnik 46 às **06h42Z de 11/11/1963**, seguido de informações de outros radares SPADATS. Também conferimos essa página por imagem. A fonte demonstra que se documentavam horários de detecção e limites temporais para **687/688**. Não contém detecção de **528** nem autoriza transportar a janela de 12 de novembro para o decaimento catalogado em **8 de novembro** de 1963.

O contraste importa porque a [NASA, *Satellite Situation Report*, 15/11/1963, página impressa 8, matriz C197#1](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) registra para **1963-003B / NORAD 528** apenas o **dia** de decaimento: 8/11/1963. A pergunta passa a ser mais específica: *existirá um boletim original comparável para o 528 nos arquivos de 7 a 9 de novembro?* Os boletins de Sputnik 46 não respondem.

## O ano que o catálogo trocou

A mesma busca impôs uma correção que evita uma falsa pista. Duas fichas digitais do National Security Archive aparecem descritas como documentos de **30/11/1963**. Nos próprios fac-símiles, porém, o [relatório 216-64, documento 9, página 1](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/09.pdf) traz **30 NOV 64**; e o [relatório 217-64, documento 10, página 1](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/10.pdf) menciona **Sputnik 83, SPADATS 943 e 1964-78**. Conferimos as páginas por imagem, além da leitura do Morcego na #180. São documentos de **1964**, não pistas contemporâneas ao episódio baiano de novembro de 1963.

A correção é de metadados, não uma refutação de fenômenos no céu. Os dois documentos pertencem à **mesma sequência NORAD/Sputnik 83**: dois originais não são duas testemunhas independentes do Conde. Pelas mesmas razões, os relatórios de 12 e 14 de novembro de 1963 são uma sequência **NORAD/SPADATS/Sputnik 46**, não duas observações do NORAD 528.

Há uma razão histórica para desconfiar de confirmações apenas aparentes. O [acordo NASA–Departamento de Defesa de 16/01/1961](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/03.pdf), **página impressa 112 (PDF p. 4)**, estabelece circulação recíproca de informações de catálogo e rastreamento entre Goddard e NORAD. Reinspecionamos a página: a dependência institucional é documentada. Duas tabelas de organizações diferentes podem reutilizar dados de uma mesma cadeia; a independência precisa ser demonstrada **no nível da medição original**.

## A pista nova não move a órbita

A trilha quantitativa e documental desta descoberta está em [`research/constraints/morcego_norad_1963_radar_source_audit.json`](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/morcego_norad_1963_radar_source_audit.json), integrada na [PR #180](https://github.com/franklinbaldo/conde-incident/pull/180). As ocorrências **MOR-NOR-20261112-01..05** separam o acordo de 1961, os dois boletins de 1963 e os dois documentos de 1964. As variáveis `spadats688_decay_lower_utc` e `spadats688_decay_upper_utc` têm valores relatados; `norad528_true_terminal_utc` continua **desconhecida**. A aresta `1963_EXAMPLE_DECAY_BOUNDS` é comparação metodológica, **não restrição física ativa para 528**.

Se surgir um documento primário específico de **528**, com identificador inequívoco, época, referencial, observável e incerteza, seus limites poderão alimentar um predicado condicional no Lean 4.35.0, um domínio admissível testável e um simulador com erros e holdouts. **Ainda não é possível** inferir intervalo horário terminal, direção, coordenadas ou local de impacto. A prova Lean, se futura, certificará uma implicação sob premissas explicitadas, nunca a autenticidade física de um boletim.

A [transcrição FBIS/Tupi sobre Conde, C01#1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) permanece um relato jornalístico mediado; o registro NASA permanece uma data de decaimento. Não há ponte instrumental autenticada entre esses registros.

**Próxima pergunta:** há boletins SPADATS/NORAD de **7 a 9/11/1963** sobre **SPADATS 528 / 1963-003B**, com medidas originais e janela própria? Se existirem, teremos um teste independente e falsificável das trajetórias. Se não forem localizados, a lacuna continuará sendo documental, sem autorizar concluir nem negar uma queda em Conde.

---

**Ficha de verificabilidade.** Fontes primárias reinspecionadas por imagem nesta rodada: [NORAD 12/11/1963, PDF p. 3](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/07.pdf), ocorrência **MOR-NOR-20261112-02**; [NORAD 14/11/1963, PDF p. 2](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/08.pdf), **MOR-NOR-20261112-03**; [NORAD 30/11/1964, PDFs 9 e 10, p. 1 de cada](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/09.pdf), **MOR-NOR-20261112-04/05** ([segundo PDF](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/10.pdf)); [acordo NASA–DoD, p. impressa 112](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/03.pdf), **MOR-NOR-20261112-01**. Relações cumulativas **C197#1 (NASA)** e **C01#1 (FBIS/Tupi)**, sem novos IDs globais arbitrários. Quatro documentos NORAD agrupados em duas linhagens Sputnik distintas; acordo NASA–DoD documenta compartilhamento institucional. Nenhum byte original foi baixado nesta rodada para cálculo de SHA-256; não há checksum verificado, medição 528, erro instrumental do 688 calibrado, redução do domínio orbital ou prova de impacto. **Conclusão sobre Conde: indeterminada.**
