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

Os três registros são **três ocorrências do snapshot histórico congelado, mas apenas uma obra de proveniência**. O exportador tools/export_fbis_operational_lineage.py --check-site confere o hash de cada linha congelada, localizador, identidade da fonte e estados não ativados; tests/test_fbis_operational_lineage.py tenta falsificar contagem de fontes, páginas, atribuição de estação, data de observação e ativação da trajetória. Em 14/11/2026, a recuperação direta do PDF público GovInfo **funcionou**: 8.533.908 bytes, SHA-256 `77e3dcb65844a1c2965ba4649bb1b1a35e4e67a6c15d7ac38c6579b50c299f86`, cabeçalho `%PDF-1.4` e marcador terminal `%%EOF`. As páginas 5, 54 e 69 (índices PDF 6, 55 e 70) foram reinspecionadas visualmente. O feed agora registra esse digest e o tamanho, mas conserva `raw_pdf_bytes_replayed_this_run=false`, porque regenerar o JSON **não** baixa o PDF. O workflow dedicado efetua o replay binário por `--check-site --source-pdf`, exige o SHA exato e falha fechado em alteração, truncamento ou indisponibilidade da origem. Nenhum PDF entra no repositório (teto 20 KB).

O contador de cobertura das **duas fontes qualificadas anteriores** continua 30 de 241; o novo terceiro feed soma **mais três vínculos documentais distintos (33 ao total ampliado)**, não três sensores. Nenhuma nova observação de 528 ou 1963 é derivada, nenhum parâmetro do simulador é preenchido e **ΔΘ = 0**. Para atribuir o circuito da notícia, ainda são necessários escala/lista de países do Panamá em 1963, registro de recepção, estação, horário, fita/áudio original Tupi e vínculo demonstrável com a retranscrição FBIS.
