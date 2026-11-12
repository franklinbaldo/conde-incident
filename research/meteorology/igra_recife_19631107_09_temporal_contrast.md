---
type: Guide
title: "C149–C151: contraste entre três sondagens nominais de Recife, novembro de 1963"
description: "Auditoria NOAA IGRA em 7, 8 e 9 de novembro; diferença meteorológica observada sem transformar proxies em vento de Conde."
---

# Recife: o vento mudou de um perfil nominal para outro

**Pergunta verificável:** o perfil de Recife em 08/11/1963 (C151) pode ser tratado como vetor invariável ao longo dos dias adjacentes? **Não.** Ao comparar os **registros originais de 7, 8 e 9/11/1963** da mesma estação, encontramos diferenças vetoriais em cinco níveis isobáricos comuns. Trata-se de **contraste entre datas nominais de Recife**, não de distribuição de erro, vento em Conde ou trajetória de fragmento.

## Custódia dos três perfis

A fonte é **um único pacote NOAA/NCEI IGRA 2.2**: [BRM00082900-data.txt.zip](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), 7.834.492 bytes, SHA-256 0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc. A leitura local conferiu o SHA do arquivo inteiro, extraiu bytes exatos e preservou os excertos em base64 reversível, sem criar observações sintéticas.

| Data nominal UTC | Níveis originais | Níveis com vento completo | SHA-256 do trecho bruto |
| --- | ---: | ---: | --- |
| 07/11/1963 12h | 29 | 15 | d77a3bc79935199cc5606a21a464f2836edc1191105ea44a03e58a3fce8375c6 |
| 08/11/1963 12h | 26 | 15 | 577224172e19552f5ce87081897479255596dc44debacc674dfd9d9ec418207e |
| 09/11/1963 12h | 26 | 15 | 73e963250891689bf39baf5c29963dd3e42ed13180cf72355237cf98a70d00b2 |

Todos têm **RELTIME=9999** (horário efetivo de lançamento **não informado**) e P_SRC=ncdc6301. A posição -8,0500°, -34,9167° e elevação catalogada 7 m pertencem à **ficha atual de Recife**; mudanças históricas de estação não foram verificadas. O [formato da NOAA IGRA](https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt) define pressão Pa (convertida a hPa), altura **geopotencial** acima do nível do mar, direção meteorológica **de onde vem** e velocidade em décimos de m/s. A resolução de 0,1 m/s não é erro instrumental medido.

## Contrastes observados na mesma estação

A tabela traz a magnitude da diferença entre o vetor u/v do dia indicado e o de 8/11, em **pressão constante**, usando u = -V sen(θ), v = -V cos(θ). Não é diferença em altura geométrica constante e não fornece derivada temporal física entre lançamentos de hora desconhecida.

| Pressão | 07/11 menos 08/11 | 09/11 menos 08/11 |
| --- | ---: | ---: |
| 850 hPa | 2,626 m/s | 5,884 m/s |
| 700 hPa | 3,061 m/s | 4,288 m/s |
| 500 hPa | 3,224 m/s | 6,793 m/s |
| 300 hPa | 5,376 m/s | 5,376 m/s |
| 250 hPa | 8,932 m/s | 7,512 m/s |

Os vetores u/v originais, pressões, alturas geopotenciais e flags estão no [JSON reproduzível](igra_recife_19631107_09_temporal_contrast.json). Esses resultados rejeitam apenas a hipótese simplificadora de **persistência exata na mesma estação entre datas nominais**. **Não** são intervalos estatísticos calibrados, erros instrumentais, correções de vento Recife–Conde, nem informação independente de época da reentrada. Três sondagens da mesma estação são **três ocasiões instrumentais, uma única família de custódia**, com níveis internamente correlacionados.

## Ligações científicas e limites

- **C149–C151**: três datas de Recife auditadas, acrescentando contraste entre dias ao perfil já verificado de 08/11; não há segunda fonte para C151.
- **C144–C146**: mapas DHN de pressão de superfície são outra modalidade documental, sem validar vento vertical na região de Conde.
- **C17–C23**: Ap/Kp planetários e F10.7 podem alimentar modelo condicional de **densidade termoesférica**, não a transferência automática de vento de Recife.
- **C193**: Explorer XVII mediu condições termoesféricas em abril–junho/1963; esses valores não são ventos troposféricos de novembro e não calibram o presente contraste.
- **Conexão para o Castor**: registrar diferença observada **dentro de Recife** como diagnóstico da inadequação de persistência temporal perfeita. Uma eventual deriva de balão/fragmento exige posição e hora reais, perfil de subida/descida, campos regionais de vento, modelo de transporte e erros **calibrados**, ausentes. Status físico OBSERVATION_ONLY_PENDING_SPATIOTEMPORAL_TRANSFER.

As sondagens NOAA são independentes da cadeia jornalística Rádio Tupi–FBIS, porém eventuais republicações UADB/NCAR oriundas dos mesmos dados NCDC **não** contam como novos instrumentos. Aqui não existe observação de Conde, horário ou localização da queda, densidade atmosférica local ou trajetória NORAD 528.

## Reprodução e falsificação

Executar:

    python3 tools/audit_igra_recife_window.py --check
    python3 -m unittest discover -s tests -p test_audit_igra_recife_winds.py -v

O workflow **IGRA Recife C151 wind audit** já executa esse arquivo de testes no HEAD, incluindo quatro controles novos de adulteração de dia/estação/fonte, hora de lançamento inventada, truncamento e vento incompleto. Toda a validação é offline com bytes fixados por SHA-256.

**Conclusão negativa:** o intervalo observado de magnitudes de diferenças (2,626–8,932 m/s nos níveis selecionados) não é um limite defensável de erro para Conde, não restringe domínios do Castor e não permite geolocalizar queda.
