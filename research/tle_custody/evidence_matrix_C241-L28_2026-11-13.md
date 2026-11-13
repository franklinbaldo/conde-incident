---
type: Guide
title: "C241-L28: 527 identificado por catálogo NASA original de 1964–1967"
description: "Quatro fac-símiles NASA com SHA-256 e leitura visual vinculam 1963 03A ao número 527, sem atribuir observações instrumentais."
---

# C241-L28: confirmação documental do catálogo 527

**Pergunta:** a correspondência `1963 03A = NORAD 527`, antes atribuída a catálogos secundários, aparece impressa em documentos originais contemporâneos? **Sim, como identidade de catálogo.** Quatro edições NASA/Goddard de 1964 a 1967 mostram na mesma linha o designador `1963 03A` e o número `527`, diferentemente das tabelas NASA de 1963 que não traziam o número nessa coluna. Não é uma nova medição de posição nem prova de identificação física de peças.

| Edição | NASA NTRS | Página PDF (1–base) / impressa | Período (min) | Incl. (graus) | Apo/perigeu (km) |
|---|---|---|---|---|---|
| 31/05/1964, vol. 4 nº 10 | [19640017911](https://ntrs.nasa.gov/citations/19640017911) | 7 / 5 | 94,5 | 81,89 | 528 / 462 |
| 15/05/1965, vol. 5 nº 9 | [19650016819](https://ntrs.nasa.gov/citations/19650016819) | 7 / 5 | 94,4 | 81,89 | 524 / 460 |
| 15/02/1966, vol. 6 nº 3 | [19660012484](https://ntrs.nasa.gov/citations/19660012484) | 6 / 5 | 94,4 | 81,88 | 520 / 457 |
| 31/08/1967, vol. 7 nº 16 | [19680005210](https://ntrs.nasa.gov/citations/19680005210) | 6 / 5 | 93,7 | 81,90 | 479 / 436 |

**Custódia:** capturas exatas em 13/11/2026, leitura direta da imagem da página impressa 5, PDF integral baixado da NASA. Comprimento e SHA-256:

- `19640017911.pdf`: 471.961 bytes; `720094637a05182e76aa1189fd15e72ef8b207cb9b94a91cd5bb02786f25b479`
- `19650016819.pdf`: 759.944 bytes; `c476e42459e13039780076315f03054c774f83a0bbadef5a61d32ba3b88eccf1`
- `19660012484.pdf`: 889.027 bytes; `4e7829a7b2b105e3c4af9b0fc0db3af64d25a90f8426ab625d84d771fb7589b8`
- `19680005210.pdf`: 1.154.109 bytes; `808e8d4bb04d3ae8d1a265fc59c97d1b6152019f9bc8785bececbdfb1d64f29d`

**Distinção de escopo:** o vínculo primário demonstrado aqui é somente **1963 03A / 527**. Nenhuma das quatro linhas certifica diretamente o pareamento 3B / 528 ou 3C / 529. Esses vínculos conservam sua cadeia de proveniência secundária, com as etiquetas de identidade de objetos físicos ainda mais restritas. As quatro edições pertencem à mesma genealogia de compilação NASA/NORAD/SAO, não a quatro sensores independentes.

## Conexão cumulativa

O [compilado C241-L27](nasa_ssr_editions_precision_C241-L27.json) documenta 527 em 1963, com períodos publicados de aproximadamente 94,6 min nas edições selecionadas. Estas **quatro novas edições** estendem a sequência editorial entre 1964 e 1967: `94,5 → 94,4 → 94,4 → 93,7 min`. A diferença aritmética das duas pontas é **-0,8 min** ao longo de **1.187 dias entre datas de publicação**, não uma medição da taxa física de decaimento, nem o intervalo entre duas observações instrumentais; épocas de ajustamento, sensores, referências e covariâncias seguem desconhecidos. O valor publicado de perigeu muda inclusive em sentidos distintos na união com 1963, logo não pressupor monotonicidade por arrasto.

O [ledger C241-L28](nasa_527_1964_1967_crosswalk_C241-L28.json) cria quatro ligações entre publicações, preserva unidade, data, página, SHA e variáveis nulas, e dá uma identidade de catálogo primária ao 527. Isso prepara um futuro controle da série 527/528/529, mas **não estreita agora o domínio físico** de queda nem altera o estado epistemológico do dia NASA de decaimento do 528.

## Reprodução

```sh
python3 -m unittest discover -s tests -p test_nasa_527_1964_1967_custody.py -v
python3 tools/nasa_527_1964_1967_custody.py --output /tmp/c241-l28.json
# Com PDFs oficiais baixados: acrescentar --pdf-dir /diretorio/dos/pdfs
```

O workflow de PR baixa os quatro PDFs da NASA, rejeita bytes que mudaram, exige HEAD exato e guarda relatório de auditoria; os testes rejeitam troca de designadores, época instrumental fabricada, falsa atribuição de identidade primária a 528/529 e promoção indevida de sigma/Lean. O código reexecuta a *custódia dos bytes*, não faz leitura visual automática das linhas impressas. A transcrição foi conferida por inspeção humana nas páginas e está congelada no ledger, com possibilidade de errata documentada.

**Próximo teste prioritário:** obter documento original que imprima `1963 03B` com o número de catálogo `528`, ou registros de sensor SPADATS relacionados ao 528 com data, quadro e erro. A cadeia de 527 ficou mais firme, mas não comprova queda em Conde.
