---
type: Guide
title: "C241-R71: releitura do Blue Book e independência editorial de jornais baianos"
description: "Auditoria das imagens NARA 0809–0811 e dos alvos Diário de Notícias e O Globo, priorizando a hora local e diferenciando rede empresarial de fonte independente."
---

# C241-TARTARUGA-R71: prioridade #871, primeira fatia

Escopo definido na [Conde #871](https://github.com/franklinbaldo/conde-incident/issues/871) e na [casa #9](https://github.com/franklinbaldo/tartaruga/issues/9), conforme 🐘 Elefante. Ficam com a 🦦 Lontra *A Tarde*, *Jornal da Bahia* e *Última Hora* Nordeste (ver [PR #1004](https://github.com/franklinbaldo/conde-incident/pull/1004)). Os controles orbitais #647 estão pausados.

## Fac-símiles NARA: todas as três imagens relidas

No executor **Ifro**, em 15/11/2026 UTC, baixei as três imagens JPEG 2000 originais da [unidade NARA 302531012](https://catalog.archives.gov/id/302531012), microfilme T1206, rolo 49. Conferi bytes e SHA-256 integrais e li visualmente os documentos. As três imagens são partes de **uma unidade Blue Book**, não testemunhos independentes.

| Imagem | Bytes | SHA-256 (prefixo) | Hora, lugar e autoria diretamente lidos |
|---|---:|---|---|
| [0809.jp2](https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/0809.jp2) | 1.756.950 | `4e8e460cfe8dfa0f` | Ficha Project 10073: **8 Nov 1963** e **Conde, Bahia, Brazil**. Campo `DATE-TIME GROUP Local` vazio; `GMT Unknown`. `Source Civilian` não nomeia testemunha |
| [0810.jp2](https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/0810.jp2) | 1.865.459 | `136be026e23acdd5` | Telegrama USAIRA, *O Globo* de **8/11**, diz receber notícias de Salvador; `141955Z` refere-se à mensagem, **não à ocorrência** |
| [0811.jp2](https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/0811.jp2) | 1.852.266 | `f9c55ab0b14d6e12` | Telegrama posterior com resposta consular, repórteres não identificados; `211430Z` refere-se à mensagem, **não à ocorrência** |

O [manifesto JSON](../archive/conde_local_hour_bluebook_C241_TARTARUGA_R71.json) conserva os hashes completos, URL, estado e limites de cada página. **Resultado para as três imagens completas: `LIDO_SEM_HORA`**. Não há hora local expressa do suposto evento, observador ocular identificado ou lugar mais preciso que Conde. A classificação administrativa `Hoax` não é prova física. Oficiais citados nos telegramas são interlocutores, não testemunhas presenciais da queda.

## Jornais sob responsabilidade da Tartaruga

| Alvo | Estado | Limite da evidência |
|---|---|---|
| *Diário de Notícias*, **Salvador, 08/11/1963** | `INACESSIVEL` para leitura remota nesta rodada | [Ficha institucional FBN](https://acervo.bn.gov.br/sophia_web/acervo/detalhe/871386) documenta coleção do jornal 1875–1981; a única [série digital ligada nessa ficha](https://memoria.bn.gov.br/DocReader/DocReader.aspx?bib=098167) cobre **1876–1909**, não 1963. Edição-alvo não lida; não concluir não digitalização global |
| Mesmo título, **09/11/1963** | `INACESSIVEL` | Recorte citado por consulado americano, mas original, página, coluna e eventual hora não foram recuperados; sem certificado de leitura |
| *O Globo*, **08/11/1963** | `INACESSIVEL` | Referência institucional em 0810, sem página, linha, horário ou autoria recuperados; rota de acesso depende da [fila do dono #884](https://github.com/franklinbaldo/conde-incident/issues/884) |

**Achado de dependência editorial:** a própria [Biblioteca Nacional](https://bndigital.bn.gov.br/artigos/diario-de-noticias-salvador-1875/) confirma a venda do *Diário de Notícias* de Salvador a Assis Chateaubriand em **1943**, com incorporação aos **Diários Associados**. A [ficha FBN](https://acervo.bn.gov.br/sophia_web/acervo/detalhe/871386) situa essa filiação até outubro de 1980. Assim, a edição de 1963 **não é independente da rede empresarial por ser outro título**. Isso **não prova** que uma reportagem local tenha copiado o texto da Tupi ou tenha sido incapaz de apuração própria. A independência de **cada matéria** permanece `UNDETERMINED` até recuperar crédito, texto e genealogia. Não converter automaticamente qualquer hora futura dessa fonte em testemunha independente.

## Decisão científica e reprodução

Nenhum horário independente foi encontrado, nenhuma restrição orbital foi ativada e nenhuma conversão UTC foi efetuada. `141955Z` e `211430Z` nunca são tempos da queda. Outros jornais independentes e acesso aos exemplares originais continuam nas rotas autorizadas da #871/#884; nenhum contato institucional nem tentativa de contornar acesso foi realizado.

Reprodução: obter JP2 do NARA e comparar SHA-256; examinar visualmente as três imagens; executar `python -m unittest tests.test_local_hour_tartaruga_r71` para os controles negativos de integridade e de promoção indevida de horário.
