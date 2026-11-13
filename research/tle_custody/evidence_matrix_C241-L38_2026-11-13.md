---
type: Guide
title: "C241-L38: cadernos da estação soviética 1078 de Yeniseisk"
description: "História institucional indica cadernos de observação da estação 1078, mas não comprova sobrevivência atual, páginas de 1963 ou identificação dos objetos de Conde."
---

# C241-L38 · Uma rota para cadernos, além dos boletins

**Pista nova:** o [histórico do Instituto Pedagógico de Lesosibirsk, filial da Universidade Federal da Sibéria](https://www.lpi.sfu-kras.ru/node/286), seção `Справка о станции наблюдений ИСЗ`, descreve uma estação óptica implantada em **Yeniseisk (Енисейск), Krai de Krasnoyarsk, em 1961**, com código **1078**. Identifica **V. A. Vorotnikov** e **P. M. Pershin**, relata envio de observações ao centro computacional `КВЦ «Космос»` e refere-se a **cadernos de observação mantidos na estação** à época em que a história institucional foi escrita. O texto menciona **25 anos de trabalho** e numerosas observações. Não fornece catálogo, cota, data da publicação eletrônica nem lista de dias observados.

**Por que importa:** C241-L37 distinguiu boletins metodológicos de compilações de medições. Agora existe **um terceiro caminho arquivístico testável**, cadernos originais e relatórios da estação 1078. Uma entrada original com data, identificação do objeto, tempo, posição e condições de observação poderia ser comparada com NORAD 527/528/529, sujeito à verificação de independência e genealogia instrumental. A notícia institucional **não** diz que algum desses três objetos foi observado nem que os cadernos de novembro de 1963 ainda sobrevivam hoje. Nem o código 1078 fornece coordenadas exatas ou equipamento para essa data.

**Custódia da cópia digital consultada:** em 13/11/2026 foi recuperado um HTML com **321.424 bytes**, SHA-256 `4df12d13cef3bcec550c0d53c34d0a8080f2b292080ebb51b7b0d9d66eab1721`, `text/html; charset=utf-8`. A validação de certificado HTTPS **falhou** no executor (`curl: (60) unable to get local issuer certificate`); apenas para registrar os bytes foi feito download usando `curl --insecure`. Portanto, o hash identifica **somente esta cópia de transporte não autenticada por TLS**. Não atesta o mestre editorial, nenhum caderno original ou a existência atual do acervo. Um leitor externo pode conferir a página institucional com seu próprio navegador/cadeia de certificados.

**Próximo teste documental:** localizar inventário/cota e custodiante presente dos cadernos da estação 1078; verificar se há **7–9 de novembro de 1963**, fotografias das folhas e cabeçalhos de estação/data; transcrever identificadores soviéticos/americanos sem presumir a equivalência com `1963-003A/B/C`; documentar página, bytes/hashes originais, relógio, referencial, precisão e qualquer redução posterior. Somente então submeter possíveis observações à Tartaruga. Não foi feito contato externo.

**Estado epistemológico:** `INSTITUTIONAL_HISTORY_ARCHIVAL_LEAD_NOT_TARGET_OBSERVATION`. **Zero medições independentes dos objetos 527–529, zero observáveis numéricos e zero restrições orbitais novas.**

**Reprodução:** `python3 -m unittest discover -s tests -p 'test_yeniseisk_station1078.py' -v` e, com a cópia baixada, `python3 tools/verify_yeniseisk_station1078.py --html /caminho/pagina.html`. Não guardar o HTML de 321 KB no Git; apenas o manifesto e os testes, respeitando 20 KB por arquivo.
