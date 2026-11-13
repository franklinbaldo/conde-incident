---
type: Guide
title: "C241-L43: caixas Smithsonian para procurar observações ópticas SAO de 1963"
description: "Localizadores EAD originais, verificação de custódia e limite entre achado arquivístico e dado orbital dos objetos 527/528/529."
---

# C241-L43: uma rota arquivística verificável para observações primárias

**Nova fonte (metadados de acervo, não TLE):** o inventário [Smithsonian Institution Archives, Records 1957–1966, SIA.FARU0171](https://sova.si.edu/components/sia.faru0171), publicado em [EAD XML](https://sirismm.si.edu/EADs/SIA.FARU0171-ead.xml), identifica quatro unidades concretas diretamente relevantes à recuperação das observações SAO: [optical tracking reports, 1960–1963, caixa 22](https://sova.si.edu/record/sia.faru0171/refIDd1e2142); [STP monthly reports, 1961–1965, caixa 22](https://sova.si.edu/record/sia.faru0171/refIDd1e2187); [STP correspondence, 1962–1963, caixa 23](https://sova.si.edu/record/sia.faru0171/refIDd1e2240); [STP clocks, precision timing system, 1961–1965, caixa 24](https://sova.si.edu/record/sia.faru0171/refIDd1e2360). São descrições de dossiês, não suas imagens digitalizadas. Não é possível afirmar que algum deles contenha observações dos objetos 527/528/529 sem consulta aos documentos internos.

A cópia EAD consultada em 13/11/2026 tinha **90.490 bytes** e SHA-256 `15b9c1a3e513690b0d66eec177a2b6897c373fbfe96cd8925e722765e6229f02`. O JSON [C241-L43](sao_archival_tracking_leads_C241-L43.json) fixa URLs de nível de arquivo, identificadores, caixas, perguntas e limites. `tools/tle_sao_archive_leads_c241_l43.py` reabre a EAD e rejeita alterações de bytes, título, caixa e refID. O SHA identifica o *finding aid*, não os relatórios guardados no acervo.

**Ponte cumulativa:** `inventário SAO → localização de dossiê → obtenção de documento original → vinculação explícita 1963-003A/B/C a 527/528/529 → estação e época UTC → frame, calibração e erro → restrição orbital candidata`. O primeiro elo está documentado; os demais são pendentes. Nenhum relatório primário dessas caixas foi recuperado nesta ocorrência. Não há nova medição independente, nenhum σ, hora ou latitude/longitude de reentrada, nenhuma redução de Θ e nenhuma inferência física sobre o corpo relatado em Conde.

**Próxima aquisição necessária:** pesquisar no acervo os relatórios ópticos correspondentes a outubro–novembro de 1963 e identificar, dentro deles, 1963-003A/B/C ou equivalências documentadas. Relatórios de relógios podem informar método de cronometragem da rede, mas não substituem calibração específica de cada observação. Não foi enviado contato aos arquivistas; eventual solicitação externa depende de autorização explícita.

**Reprodução:** `python3 -m unittest discover -s tests -p test_tle_sao_archive_leads_c241_l43.py -v`; `python3 tools/tle_sao_archive_leads_c241_l43.py --live`. Fonte de pesquisa original: issue #396. Esta é uma nova rota de custódia, não uma alegação de sucesso na obtenção de TLEs.
