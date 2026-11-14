---
type: Guide
title: 'C241-L51 · ponte científica de fac-símiles NSA/NRO'
description: 'Dois PDFs retrospectivos custodiados, conflito B/D e latentes inativos para NORAD 528.'
---

# C241-L51: fac-símiles → grafo → hipótese Lean → parâmetro latente

A ponte em `public/data/conde-declassified-2313-scientific-bridge.json` é exportada de `tools/export_declassified_2313_scientific_bridge.py` a partir do manifesto custodiado por 🐢 Tartaruga `research/tle_custody/declassified_facsimiles_C241-L51.json` e da ponte anterior C241-L50, ambos fixados por SHA-256 e revalidados. Não editar manualmente o JSON publicado.

**Obra NSA 1975:** *NSA in Space*, Appendix A, página física **132** (impressa **5** do apêndice), é o registro documental `7153 / 698 BK IV / 2313 / Thor-Agena D / 16 Jan 63`. PDF completo SHA-256 `3d5d7a22608d3eb9ab23f61f46da924708d471917f77ee5f3a68ae8910aeab74`. Liberação posterior em 2017 não equivale a observação de 2017.

**Obra NRO 1994:** *The SIGINT Satellite Story*, física **123**, impressa **90**, identifica 2313/7153 com Thor; dois dias de funcionamento até falha elétrica não são dois dias até cair ou fragmentar. O trecho não nomeia a variante Agena. PDF completo SHA-256 `1bffa3e121073c8a312c9f67393efac09aa0a322e18ce039e592df0454e13c8a`. Na ponte anterior C241-L48, NRO estava somente como texto indexado; a nova custódia permite reconhecer o fac-símile sem reescrever o histórico de acesso.

A NSA (D), a NASA SP-4004 (D para grupo), a Quest (D) e GCAT/Gunter (B) **não são quatro medidas independentes do hardware**. Não é conhecido seu grau de dependência documental. `1963-003` (grupo) não identifica a peça `1963-003B` (NORAD 528). C197#1 é contexto do boletim NASA, não prova da variante nem da massa. Oito parâmetros latentes herdados da ponte anterior mantêm `null`, hipóteses B/D e identidade de peça continuam abertas; Lean documental não compilado e Θ inalterado.

Reproduzir com `python3 tools/export_declassified_2313_scientific_bridge.py --check-site` e `python3 -m unittest discover -s tests -p 'test_declassified_2313_scientific_bridge.py' -v` (também `python3 -O`). O auditor dos PDFs originais é `tools/tle_declassified_facsimiles_c241_l51.py`; o exportador reconcilia seu manifesto, **não baixa os PDFs** nem atesta novamente a inspeção visual. Assim, o hash do manifesto não deve ser confundido com os SHA-256 dos PDFs.

**Teste discriminante:** documentação de integração/engenharia de 2313 que resolva B/D, seguido da associação peça→528 e observação primária SPADATS/SAO com época UTC, estação, referencial e erro. Sem esses elementos, `activation=false`, `THETA_UNCHANGED`, nenhuma probabilidade de queda em Conde.
