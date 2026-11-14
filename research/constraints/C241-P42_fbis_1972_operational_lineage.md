---
type: Guide
title: 'C241-P42: CIA FBIS 1972, três vínculos e uma fonte'
description: 'Vínculos de proveniência C212–C214 sem atribuir a retranscrição Tupi ao bureau do Panamá.'
---

# C241-P42 · O histórico de operações FBIS não identifica um receptor Tupi

A [história institucional CIA FBIS de maio de 1972](https://www.govinfo.gov/content/pkg/GOVPUB-PREX3-PURL-gpo254964/pdf/GOVPUB-PREX3-PURL-gpo254964.pdf), documento CIA-RDP05-01429R000100010001-0, foi reinspecionada visualmente nos índices PDF 55, 70 e 6 (páginas impressas 54, 69 e 5). O documento é **fonte primária retrospectiva sobre funcionamento institucional**, mas não observação instrumental da esfera ou da transmissão de Conde.

- **C212#1, p. 54:** a organização relata dificuldade para cobrir o Brasil; suas estações costeiras monitoravam imprensa brasileira, porém pouco rádio falado.
- **C213#1, p. 69:** o bureau do Panamá acompanhava transmissões de 17 países em novembro de 1963, sem enumerá-los. Isso **não identifica o Brasil ou a Rádio Tupi** entre as emissoras monitoradas.
- **C214#1, p. 5:** em 1964 havia seleção editorial entre material enviado e material publicado no *Daily Report*. A porcentagem de 1964 **não pode ser aplicada como probabilidade** de presença/ausência de uma notícia brasileira em novembro de 1963.

Os três registros são **três ocorrências do snapshot histórico congelado, mas apenas uma obra de proveniência**. O exportador tools/export_fbis_operational_lineage.py --check-site confere o hash de cada linha congelada, localizador, identidade da fonte e estados não ativados; tests/test_fbis_operational_lineage.py tenta falsificar contagem de fontes, páginas, atribuição de estação, data de observação e ativação da trajetória. O PDF foi verificado por imagens, **mas a recuperação de bytes brutos desta rodada falhou com HTTP 522**; por isso seu SHA-256 permanece nulo, sem inventar um digest.

O contador de cobertura das **duas fontes qualificadas anteriores** continua 30 de 241; o novo terceiro feed soma **mais três vínculos documentais distintos (33 ao total ampliado)**, não três sensores. Nenhuma nova observação de 528 ou 1963 é derivada, nenhum parâmetro do simulador é preenchido e **ΔΘ = 0**. Para atribuir o circuito da notícia, ainda são necessários escala/lista de países do Panamá em 1963, registro de recepção, estação, horário, fita/áudio original Tupi e vínculo demonstrável com a retranscrição FBIS.
