---
type: Guide
title: '🦌 Cervo: falsificação condicional do relógio de publicação NASA SSR'
description: 'Contraprova com frações exatas: datas editoriais não devem substituir épocas instrumentais na inferência orbital.'
---

# Teste contrafactual de datas de publicação, C241-L18/L21

Pergunta: é seguro interpretar **30/11, 15/12 e 31/12/1963**, datas das edições compiladas da NASA SSR, como épocas das medições orbitais dos controles 527 e 529 e ajustar uma tendência linear de período nodal? **Não.** As fontes indicam datas editoriais; não temos as épocas de cada medição. O teste a seguir é um diagnóstico de **consistência de um substituto fictício**, não uma simulação do movimento do objeto.

Os valores impressos, da mesma família compiladora NASA/Goddard/NORAD, são 527 (1963-003A): 94,6; 94,6; 94,6 min e 529 (1963-003C): 92,2; 91,6; 89,2 min. Identificadores de custódia C241-L18 (30/11 e 31/12) e C241-L21 (15/12), com SHA-256 herdado do ledger congelado. Não há série equivalente do 528 nessas edições. Fontes de referência: [NASA NTRS 15/12/1963 (19640003479)](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf), e demais PDFs catalogados em `research/tle_custody/`.

## Certificado exato

Sob a hipótese **contrafactual** de que as datas de relatório sejam épocas instrumentais, um modelo afim `P(t) = a + b*t` deve satisfazer, para os três instantes ordenados, `P_meio = (16 P_30nov + 15 P_31dez)/31`, porque os intervalos são de 15 e 16 dias. Supondo **apenas** arredondamento de impressão ao décimo, cada célula impressa admite `±0,05` min; o resíduo da interpolação admite `±0,10` min, independentemente de hipóteses probabilísticas e sem contar a célula central duas vezes.

Para o 529, o valor central do resíduo é **2640/31 centiminutos** (aproximadamente 0,85161 min), e toda a faixa de arredondamento é **[2330/31, 2950/31] centiminutos** (aproximadamente [0,75161; 0,95161] min). Como a faixa não contém zero, nenhuma trajetória **afim no relógio fictício de publicação** atravessa os três intervalos de impressão. Para o 527, o resíduo é zero e o teste não rejeita esse substituto. Compatibilidade não prova que o período físico seja constante.

Esse resultado **não demonstra aceleração orbital** do 529: a premissa que transforma data de impressão em época de medida não é documentada. Os três PDFs não são três sensores independentes; as bandas não são erros instrumentais, intervalos de confiança, nem likelihood. Tampouco permitem transportar a trajetória do 529 para o 528, estimar tempo/local de reentrada ou calcular probabilidade de queda em Conde. A hipótese astronômica, a posterior histórica e a redução geográfica permanecem **NOT_IDENTIFIED / NOT_RUN**, com `active_physical_constraint=false`.

## Reproduzir e falsificar

```bash
python3 tools/ssr_report_date_proxy_falsifier.py --check
python3 -m unittest discover -s tests -p 'test_ssr_report_date_proxy_falsifier.py' -v
```

O programa usa `reports()` do comparador já integrado, validando SHA dos PDFs, crosswalks e pertinência das linhas. O JSON congelado contém frações exatas, nunca estimativas em `float`; os testes incluem datas trocadas, fonte adulterada, 528 artificial, erro de arredondamento e o controle compatível do 527. A próxima observação discriminante real continua sendo **época original associada ao observável, referencial, instrumento, erro/covariância e linhagem documental**. Até essa fonte existir, este certificado só veta a interpretação ingênua do relatório como sensor.
