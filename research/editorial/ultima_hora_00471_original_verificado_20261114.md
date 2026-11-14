---
type: Guide
title: "00471: fac-símile direto da notícia do buraco de quatro metros em Recife"
description: "Auditoria documental de 14/11/2026 da edição 00471 de Última Hora Nordeste, com bytes, SHA-256, página, leitura visual e limites de genealogia Tupi."
---

# C241-CORUJA-R43 · A página 8 da edição 00471 foi efetivamente lida

## Identidade e custódia

- **Veículo:** *Última Hora*, edição do Nordeste, Recife.
- **Data e número impressos no cabeçalho da página digital 1:** sexta-feira, **8 de novembro de 1963**, **nº 471** (identificador digital **00471**).
- **Original digital no custodiante:** [Biblioteca Nacional, PDF completo, edição 00471](https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00471.pdf).
- **Trecho relevante:** [página digital 8 de 8](https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00471.pdf#page=8), página policial; cabeçalho **“POLÍCIA ARRANCA CONFISSÃO DO PESCADOR”**, título **“ROUBEI ESTÁTUAS E ENTERREI EM RIO DOCE”**; subtítulo **“DIFICULDADE”** na coluna direita.
- **GET HTTPS reproduzido em 14/11/2026 no executor externo `ifro`:** HTTP 200, **4.337.426 bytes**, arquivo PDF 1.4, **8 páginas**, `pdfinfo` validou a estrutura; SHA-256 dos bytes recebidos:
  `e121d6ea9784bcb77a02e1a6e3c453f23987103940f5993190237c45499a95ec`.
- **Reprodução local da leitura:** `curl -fL -o 00471.pdf 'https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00471.pdf'`; `sha256sum 00471.pdf`; `pdfinfo 00471.pdf`; `pdftoppm -f 8 -l 8 -jpeg -scale-to 4700 00471.pdf pagina8`. Uma amostra visual da capa e recortes da página 8 foram inspecionados sem depender de OCR. Os recortes são derivados e não substituem o original da BN.
- **Limite de acesso:** GET/HEAD da mesma URL em outros ambientes tinha retornado HTTP 403 em 13/11. A acessibilidade pode variar por executor; o 403 histórico não significa inexistência e não altera a identidade do PDF agora obtido.

## O que a página efetivamente diz

A matéria descreve **três estátuas roubadas** e escondidas em um terreno de campo de futebol de **Rio Doce, Recife**. O parágrafo identificado como **“DIFICULDADE”** diz que as estátuas foram enterradas **“num buraco de quatro metros de profundidade”**. A edição **não apresenta essa matéria como notícia de Conde**. Nenhuma inspeção física de cratera em Conde é descrita.

A fonte contemporânea comparada é o [registro FBIS da Rádio Tupi em 8/11/1963](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), que **traduz para o inglês** o relato de uma esfera que teria aberto um buraco de quatro metros. A semelhança numérica e semântica pode agora ser conferida em **dois documentos de 1963**, ao invés de depender de uma leitura retrospectiva apenas de uma das páginas.

**Não temos a transcrição em português ou a fita da Rádio Tupi.** Portanto, a identidade *literal* de palavras portuguesas entre os dois registros é **não demonstrada**: o FBIS registra a versão em inglês. Também faltam hora de fechamento da edição, hora local validada da transmissão, editor/redator e qualquer despacho que una os textos. A hipótese de coincidência permanece a referência mais parcimoniosa; não há demonstração de cópia, montagem deliberada ou itinerário jornalístico.

## Delta documental e rastreabilidade

| Atributo | Antes de 14/11 | Após a recaptura |
|---|---|---|
| Edição 00471, p. 8 | Indicação em [estudo semântico anterior](https://github.com/franklinbaldo/franklinbaldo.github.io/blob/main/docs/research/conde-ufo-semantic-reading-1963.md); HTTP 403 na tentativa anterior | Fac-símile original de oito páginas baixado, hash e cabeçalho de data conferidos, trecho lido visualmente |
| Alegação dos quatro metros no Recife | Leitura prévia secundária auditável | **Confirmada como texto impresso no jornal de 8/11/1963**; não confirmada como ocorrência material |
| Palavras exatas da Tupi em português | Não disponíveis | Continuam não disponíveis; tradução FBIS não é fita de áudio |
| Dependência entre os dois veículos | Nenhuma aresta demonstrada | **Nenhuma aresta demonstrada**; H0 coincidência permanece |
| Medição física de NORAD 528 / impacto em Conde | Não existente aqui | **Nenhuma mudança** (`THETA_UNCHANGED`) |

A genealogia [`research/editorial/tupi_fragmentos_20261113.md`](https://github.com/franklinbaldo/conde-incident/blob/main/research/editorial/tupi_fragmentos_20261113.md) e a ponte [`conde-tupi-legacy-fragment-bridge.json`](https://github.com/franklinbaldo/conde-incident/blob/main/public/data/conde-tupi-legacy-fragment-bridge.json) registram o **estado anterior** ao acesso recuperado. Seus campos `other_original_pdf_sha256=null`, `other_printed_page8_inspected=false` e `other_evidence_status=...HTTP_403` devem ser reconciliados **em atualização própria do exportador e de seus testes**, depois da checagem da identidade da edição e sem promover `direct_textual_dependency` a `true`. Esta nota documenta a mudança para não misturar PR editorial com reexportação de grafo de proveniência.

O [Caderno 16](https://github.com/franklinbaldo/conde-incident/blob/main/stories/2026-11-13-dois-buracos-de-quatro-metros.md) agora distingue o texto contemporâneo comprovado da suposta influência ainda não demonstrada. **Nenhuma nova restrição orbital ou localização de reentrada decorre desse achado.**

## Próximo documento que discriminaria hipóteses

Roteiro/áudio original da Tupi de 8/11/1963, boletim de agência com crédito e hora, ou notícia baiana anterior com formulação correspondente. Para comparar precedência, registrar fuso, fecho editorial e prova de acesso de uma redação à outra. Se nenhuma ponte aparecer, preservar o resultado negativo com escopo de coleção, nunca convertê-lo em demonstração de independência.
