---
type: Guide
title: "C241-LONTRA-R34: encaminhamento arquivístico da estação 1078"
description: "Contato geral e museu educacional do LPI/SFU localizados, sem confundir endereço de contato ou acervo educativo com custódia de cadernos orbitais de 1963."
---

# C241-LONTRA-R34 · Quem pode apontar o custodiante dos cadernos 1078?

**Retomada de C241-L38:** a [história institucional](https://www.lpi.sfu-kras.ru/node/286) menciona cadernos da estação de observação nº 1078, em Yeniseisk, sem identificar acervo sobrevivente, cota nem documento de 7–9/11/1963.

Em 13/11/2026 foram recuperadas mais duas páginas da **mesma instituição**:

1. [Contatos do Instituto Pedagógico de Lesosibirsk / Universidade Federal da Sibéria](https://lpi.sfu-kras.ru/contact): apresenta a recepção administrativa e o e-mail geral `lpikrgu@wood.krasnet.ru`. **É um canal de encaminhamento**, não indicação de que a recepção guarda registros científicos.
2. [Museu «Da província de Yeniseisk ao Krai de Krasnoyarsk»](https://lpi.sfu-kras.ru/node/922): descreve museu fundado em 15/12/2008, com mais de 10.000 peças relacionadas à **história da educação**. Não menciona a estação 1078 nem seus cadernos. **Não presumir que o museu é o depósito dos registros.**

| Evidência web | Bytes | SHA-256 |
|---|---:|---|
| Página de contatos | 110.177 | `2adb4e614387eaed3b194b271ccf57db20322cdb5b0ee1f3cec2d69c54013971` |
| Descrição do museu | 112.263 | `67c96d4cb12b5f026ae4f7f0cb95754120423ef139d2c8a98fd64de55e1c2213` |

**Caveat de transporte:** os dois acessos HTTPS falharam na validação da cadeia de certificados pelo Jatobá (`curl 60`). Somente para análise dos bytes públicos foram obtidas respostas HTTP 200 com `curl -k`. Os hashes fixam essas cópias, mas não autenticam o editor, não provam o acervo e não substituem a verificação de TLS.

**Consulta arquivística planejada, não enviada:** solicitar à recepção, para encaminhamento ao responsável competente, identificação de titular atual, fundo/inventário/dossiê/cota e eventual transferência dos cadernos nº 1078 ou relatórios remetidos ao КВЦ «Космос». Pedir, caso sobrevivam, folhas datadas de **7–9/11/1963**, seus cabeçalhos e identificações originais de satélites, com condições de observação, método, referencial e relógio. Se nada for localizado, pedir indicação de outra instituição ou documentação de transferência/eliminação. O pedido deve evitar pressupor que os documentos existem.

**Independência:** duas páginas no mesmo domínio institucional não equivalem a duas confirmações históricas independentes. Contatos públicos não são fac-símiles; um museu educacional não se converte em arquivo astronômico por proximidade administrativa. Nenhum contato foi feito.

**Estado:** `VERIFIED_PUBLIC_CONTACT_AND_MUSEUM_LEADS_NOT_ARCHIVE_HOLDINGS`. Documentos primários de 1963 recuperados: **0**. Observáveis dos objetos NORAD 527–529: **0**. Restrições orbitais ativadas: **0**.

**Reprodução:** `python3 -m unittest discover -s tests -p 'test_sfu_station1078_custodian_route.py' -v`; com cópias integrais locais: `python3 tools/verify_sfu_station1078_custodian_route.py --contact-html contact.html --museum-html node_922.html`. HTML original fora do Git.
