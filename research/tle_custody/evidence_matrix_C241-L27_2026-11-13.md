---
type: Guide
title: "C241-L27: sequência documental NASA 1963 e precisão de impressão"
description: "Normalização de nove edições NASA para 527/528/529 com controles de custódia e quatro grandezas tipadas, sem converter resolução impressa em σ instrumental."
---

# C241-L27: precisão editorial não é precisão orbital

**Escopo:** integrar e auditar de maneira automática as séries já recuperadas de boletins *Satellite Situation Report* de NASA/Goddard em 1963, sem baixar novas linhas TLE, sem atribuir instrumentos ou inventar eventos. Fontes já auditadas nas ocorrências C241-L12, L16, L17, L18, L19, L21, L22 e C241-L11, com suporte cruzado C241-L10. O registro [JSON](nasa_ssr_editions_precision_C241-L27.json) fixa para cada edição o NTRS, a data publicada, o número, o índice PDF, a página impressa, o SHA-256 previamente verificado e a posição no ledger de origem. O script lê os documentos já existentes em `main`, não edita nem substitui as fontes.

| Publicação NASA | NTRS | Nº do volume 3 | Linhas de 527/528/529 |
|---|---|---:|---|
| 30/04/1963 | 19630012128 | 9 | 527, 528, 529 |
| 30/06/1963 | 19630012130 | 13 | 527, 528, 529 |
| 31/07/1963 | 19630012290 | 15 | 527, 528, 529 |
| 15/08/1963 | 19630012289 | 16 | 527, 528, 529 |
| 15/10/1963 | 19640000428 | 20 | 527, 528, 529 |
| 15/11/1963 | 19640001198 | 22 | 527, 529 |
| 30/11/1963 | 19640002493 | 23 | 527, 529 |
| 15/12/1963 | 19640003479 | 24 | 527, 529 |
| 31/12/1963 | 19640005618 | 25 | 527, 529 |

O resultado computacional é uma sequência de **nove edições distintas, 23 linhas documentais**: 527 em nove, 528 em cinco, 529 em nove. São fotografias compiladas de publicações, **não** 23 medições de radar nem nove redes independentes. As três identidades NORAD provêm de *crosswalk* catalográfico secundário, não estão impressas assim nas tabelas de 1963. A família de compilação NASA/NORAD/SAO pode compartilhar a mesma origem instrumental. Os intervalos de publicação não são intervalos instrumentais.

## Duas precisões incomparáveis

Os períodos aparecem com uma casa decimal em minutos, a inclinação com duas casas decimais em graus e apogeu/perigeu em quilômetros inteiros. **Apenas se os números tivessem sido arredondados ao mais próximo** (método não confirmado) as meias unidades de resolução gráfica seriam 0,05 minuto, 0,005 grau e 0,5 quilômetro. Esses valores não medem erro de sensor, de elemento orbital, de previsão de reentrada, nem garantem que a realidade física caiba nesses intervalos. Evite tratá-los como uma distribuição uniforme, `sigma`, tolerância física ou verossimilhança.

O auditor gera um registro por edição e objeto com valor e unidade, época de publicação (separada de época de observação desconhecida), SHA documental e um operador orbital candidato dependente de estado, modelo, convenção, época e erros ainda não recuperados. Os campos `instrument_observation_epoch`, `instrument_sensor` e `instrument_sigma` ficam nulos.

## Reparos e exemplos que a auditoria não deixa regredir

O documento NASA [31/07, PDF p. 7, impressa 5](https://ntrs.nasa.gov/api/citations/19630012290/downloads/19630012290.pdf#page=7) mostra perigeu **452 km** para 1963 3C, não o valor antigo **425 km**, corrigido em C241-L18. Em [31/12, PDF p. 7](https://ntrs.nasa.gov/api/citations/19640005618/downloads/19640005618.pdf#page=7), o período do 3C é **89,2 min**, não a leitura antiga de 89,6 min (errata C227). Esses são reparos de *transcrição impressa*, não novidades instrumentais.

A última **linha de 528 presente nas nove edições selecionadas** é a de 15/10/1963. A época 27/10 do espelho TLE secundário pertence a outra linhagem e não deve ser atribuída a uma edição NASA inexistente na seleção. O [SSR 15/11, impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10) registra o dia catalogado 08/11/1963 para `1963 3B`; não determina hora UTC. Nem a ausência do 528 nas tabelas posteriores prova uma observação negativa de radar.

**Estado do grafo:** `CONNECTED_PENDING_CALIBRATION`, oito arestas de sequência editorial, zero restrições físicas novas, zero cálculo de localização/horário e zero promoção Lean. Os controles de 527/529 após novembro continuam úteis para futura calibração condicional com épocas, instrumento/frame e erro autenticados.

## Reprodução e limites

```sh
python3 -m unittest discover -s tests -p test_tle_ssr_editions_precision_audit.py -v
python3 tools/tle_ssr_editions_precision_audit.py --output /tmp/c241-l27-ssr-editions.json
```

O script recusa documento sem SHA ou com edição/página diferente, linha 528 fictícia, erro antigo de 425/89,6, aparente σ derivado de dígitos e ativação física antes de calibração. Testes sobre ledgers versionados não equivalem a uma nova leitura independente dos PDFs: os downloads e hashes originais são responsabilidade dos workflows das edições correspondentes. Próxima fonte prioritária: fichas de rastreamento SPADATS/NORAD de 528 e a edição 21 não recuperada.
