---
type: Guide
title: '🦫 G70: precisão retrospectiva Baker–Nunn e relógio de 1963'
description: 'Fonte NASA/SAO custodiada; orçamento angular e temporal não ativado sem observação instrumental dos NORAD 527/528/529.'
---

# G70: fonte histórica para precisão de rastreio, sem calibrar o 528

## Documento e custódia

**Fonte:** E. M. Gaposchkin (ed.), *1973 Smithsonian Standard Earth (III)*, SAO Special Report 353, publicado em 28/11/1973. Part II, seção 1.1.3, páginas impressas 25–26, **páginas 35–36 do PDF**. [PDF oficial NASA NTRS 19740019249](https://ntrs.nasa.gov/api/citations/19740019249/downloads/19740019249.pdf).

Os bytes originais foram baixados em 14/11/2026 da NASA NTRS: tamanho **12.337.725 bytes**; SHA-256 **10f2d85593af7be543326471f8c1eaf234aefc0565515cd4ff059edad20922c8**. A hash e o tamanho foram verificados diretamente, e ambas as páginas foram inspecionadas visualmente no Ifro. Não versionar o PDF de 12 MB. O próprio relatório cita **Lambeck (1968b)** na genealogia dos orçamentos: publicação **retrospectiva** de 1973, não registro de exposição instrumental contemporâneo a 1963.

## A distinção técnica importante

Na p.25, o SAO descreve relógios **Norrman** antes de 1965 e monitoramento **WWV HF/VHF**, com erro RMS de época aproximadamente **1 ms**, mas desvios ocasionais de vários milissegundos sem uma distribuição/limite publicados. A instalação de relógios EECo começou em 1964, e VLF/relógios portáteis trouxeram melhorias posteriores. O RMS descrito é da rede, não uma variância demonstrada de câmera e exposição do NORAD 528.

A Tabela 1 na p.26 distingue erro angular **ao longo** e **transversal** à trajetória (segundos de arco), por velocidade angular topocêntrica (segundos de arco/s), e duas configurações de relógio **VHF** e **VLF + portáteis**. No intervalo 0–250 arcsec/s, a coluna ao longo da trajetória é 1,8 arcsec em ambas as configurações; acima de 2.000 arcsec/s o valor VHF cresce para **3,7 arcsec**, versus **2,0 arcsec** para VLF/portáteis. O transversal tabulado é 1,8 arcsec. Não aplicar retroativamente a coluna de melhorias tardias a 1963.

O vetor de dados em sao_baker_nunn_1973_error_budget_G70.json retém os cinco intervalos, unidades, anos e proveniência sem converter precisão de impressão em covariância nem orçamento agregado em observações independentes.

## Interface com o G64 e próximos dados discriminantes

Como teste dimensional *condicional*, 250 arcsec/s multiplicado por 0,001 s corresponde a 0,25 arcsec de deslocamento angular devido ao relógio; 2.000 arcsec/s corresponde a 2,0 arcsec. Isso NÃO é sigma do 528 e **não** permite subtrair quadrados do orçamento global para deduzir um ruído instrumental. Se duas exposições compartilham relógio, a correlação depende da cadeia de sincronização. O G64 exige covariância conjunta documentada.

O registro está em estado **CANDIDATE_NOT_ACTIVATED**. Sigma individual 527/528/529, identidade do instrumento, tempo UTC da exposição, estação, referencial, covariância, holdout histórico e inferência de impacto permanecem **ausentes**. O auditor rejeita qualquer preenchimento desses campos sem novo contrato versionado. Reproduzir:

    python3 tools/sao_baker_nunn_budget_G70.py --source-pdf /caminho/19740019249.pdf
    python3 -m unittest discover -s tests -p 'test_sao_baker_nunn_budget_G70.py'

A próxima evidência útil para [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396) é **um filme/exposição identificados 527/528/529**, com estação, época UTC, tipo de relógio e redução de imagem. Em [Conde #647](https://github.com/franklinbaldo/conde-incident/issues/647), distinguir sempre a rede SAO Baker–Nunn do catálogo NORAD/SPADATS. Esta fonte melhora o desenho de calibração, **não** reduz atualmente o domínio orbital, horário ou geográfico de Conde.
