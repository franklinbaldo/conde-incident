---
type: Guide
title: '🦅 G58: rejeitar alegações orbitais introduzidas em texto livre de C241-L47'
description: Retrospectiva de três integrações e contraprova de custódia das notas NASA/UAH de 1963.
---

# G58: integridade das notas interpretativas C241-L47

**Janela congelada:** `4f01d61fdb88c0842a90a4a26f6514bf9420c98f` (exclusivo) até `deb7e8562107f9f7b5dfe5998f5fe1237659056e` (inclusivo). Três integrações first-parent, três commits no DAG: #736 (narrativa Baja), #725 (timing de câmeras soviéticas; foco) e #743 (Lean MCMC circular). Checks históricos individuais não inspecionados: **NOT_CHECKED**.

## G58-F1: palavras de ressalva não impedem afirmações adicionais falsas

O auditor `tools/tle_uah_soviet_camera_timing_audit.py` da integração #725 verifica campos físicos e hashes de PDFs. Porém, `interpretation`, `visual_check`, `source_lineage` e `next_test` eram textos livres, sujeitos apenas às substrings `not a tracking record`, `No OCR`, `May 1963` e `not retrieved` (ou nem isso). Quatro mutações sintéticas preservaram os requisitos e **foram aceitas**, embora passassem a afirmar observação instrumental do NORAD 528, impacto em Conde, verificação dos originais russo/DoD não recuperados ou confirmação de reentrada.

**RED:** adicionamos quatro testes de falsificação: quatro falhas de 21 testes, produzidas por `ValueError` não lançada. Não existe evidência de que a adulteração tenha ocorrido no registro real.

**GREEN:** cálculo determinístico SHA-256 da representação JSON canônica dos quatro campos de prosa do snapshot atualmente revisado. Alterações futuras exigem conferência explícita da fonte e atualização intencional do pin, em vez de uma redação enganosa manter palavras de ressalva. O teste original e 20 negativos/positivos passam em Python normal e `python3 -O` (21/21 em cada modo). `git diff --check` passa; nenhuma fonte primária, número impresso nem parâmetro de órbita foi modificado.

**Limites:** o SHA protege apenas **o texto atualmente revisto** e não confirma a veracidade histórica da transcrição visual. A fonte é um digest contemporâneo de equipamento, não um registro de rastreamento do 528. O resultado não confirma instante nem local de reentrada. CI do HEAD autoral e replay de fontes reais devem ser validados antes do merge.

Referências: [#725](https://github.com/franklinbaldo/conde-incident/pull/725), [#743](https://github.com/franklinbaldo/conde-incident/pull/743), [#736](https://github.com/franklinbaldo/conde-incident/pull/736), [G57 #742](https://github.com/franklinbaldo/conde-incident/pull/742).
