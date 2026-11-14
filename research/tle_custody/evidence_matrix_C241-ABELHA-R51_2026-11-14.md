---
type: Guide
title: "C241-L59/L60: relógios e métodos SAO no grafo, sem observações 528"
description: "Ponte de proveniência do P-14 e SR266 para candidatos Lean e parâmetros orbitais desativados."
---

# C241-L59/L60: dois métodos SAO, nenhuma medida individual de 528

A fonte [P-14 / C241-L59](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/sao_p14_a1_clock_1963_C241-L59.md) tem PDF NTRS `19660001360`, 6.173.834 bytes e SHA-256 `d7140f9b78991d1bb75857ba6a109fb553b80eab16f7dd89c41cc799d9e53980`. Páginas PDF 4–5 definem **A.1 preliminary menos WWV emitted**, topocentria/equinócio 1950 e datum Kaula. A fórmula não é UTC nem pode ser extrapolada para novembro de 1963; os nove alvos selecionados não incluem 527–529.

O relatório [SR266 / C241-L60](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/sao_sr266_synthetic_1963_C241-L60.md), NTRS `19690000806`, PDF SHA-256 `287158c6a3044a1d088cb5addf4635af6921222abf21a917b08bbe81c967f9b6`, discute **pares sintéticos** interpolados de sequências Baker–Nunn, não medições independentes adicionais. A escala **A.S. atomic time** e o referencial terrestre histórico não equivalem aos do P-14, a UTC ou a TEME. A Tabela 1 não inclui 1963-003. Fontes distintas não significam sensores novos do NORAD 528.

O exportador `tools/export_sao_clock_methods_bridge.py` vincula dois manifestos fixados por SHA a **27 arestas**: época→conversão ainda desconhecida; quadro astrométrico→transformação; datum de estação→geodesia; pares sintéticos→dependências dos frames; identidade ausente→operador observável 528. Registra hipótese/contraprova, `candidateSaoClockCompatibility` **não compilado**, onze latentes nulos e três parâmetros do simulador inativos. Os números de precisão são **contexto da publicação**, não erros calibrados do NORAD 528.

É uma ligação cumulativa, não a aplicação de um dado físico: `activation=false`, `THETA_UNCHANGED`, observações novas do 528 = 0 e número histórico global desconhecido. Próximo teste: obter frame/linha original identificada de 528, com estação, época, escala e ajuste para UTC, covariância, transformação de quadro, fonte dos frames e rastreabilidade de compartilhamento. Não converter ausência nestes dois catálogos em inexistência global.

Reproduzir: `python3 tools/export_sao_clock_methods_bridge.py --check-site` e `python3 -m unittest discover -s tests -p test_sao_clock_methods_bridge.py -v`; testar também `python3 -O`.
