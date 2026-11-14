---
type: Experiment
title: "C241: triagem retrospectiva de controles de reentrada de 1963"
description: "Quatro candidatos documentais com múltiplas épocas orbitais no espelho e rótulos terminais apenas secundários"
experiment_id: C241-1963-TERMINAL-CONTROLS-R59
verification_status: SECONDARY_ARCHIVE_SEARCH_NOT_CALIBRATED
---

# Quatro controles de arquivo para investigar, zero calibrações terminais

**Pergunta:** além dos controles 637 (dia NASA sem hora) e 688 (intervalo documental de 110 minutos, mas uma época orbital), quais objetos de 1963 oferecem *duas ou mais épocas catalogadas* e rótulos públicos de decaimento que ajudem a procurar uma fonte terminal independente?

Este é um **rastreamento de fontes retrospectivo** feito em 14/11/2026, após inspeção dos dados e de datas de decaimento: **não é holdout cego, inferência orbital nem estimativa de probabilidade**. Não se declarou a data de nenhuma ficha como uma medição instrumental.

## Custódia e método

Corpus: [espelho Space-Track/oxzoid, versão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), **SHA-256 integral** c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09, 4.567 linhas. É **uma única linhagem secundária**. Deduplicar por (NORAD, época UTC); dados conflitantes na mesma época são erro; mais linhas ou cópias não tornam sensores independentes. Usar mean motion para um **perigeu proxy kepleriano**, não altitude instrumental observada.

Os dias públicos [292](https://keeptrack.space/satellite/00292), [308](https://keeptrack.space/satellite/00308), [565](https://keeptrack.space/satellite/565) e [668](https://keeptrack.space/satellite/00668) são **pistas de busca secundárias**, possivelmente de genealogia catalográfica compartilhada, e não intervalos terminais independentes. A fonte não comprova UTC nem incerteza. Os controles existentes, 637 (NASA SSR de 15/11/1963, p. 8) e 688 (AF IN 23784, 14/11/1963, p. 2), têm status documental diferente e são mantidos no relatório para comparação, não entram no ranking novo. Para 688, o documento informa 22h10–24h00 Z de 12/11, mas **não** fornece covariância de rastreio; não se empresta a secante do 687.

O corte em 00h UTC do dia anunciado é **hipótese contrafactual de triagem**, explicitamente não uma autenticação da convenção temporal. O código bloqueia vazamento de linhas posteriores ao corte; isso não torna o desenho prospectivo.

## Resultado reproduzido no espelho SHA-pinado

| NORAD | Dia público de decaimento | Épocas únicas em 1963 | Último perigeu proxy (km) | Status |
|---|---|---:|---:|---|
| **292** (1962-018A) | 26/11 | **53** | 193,994 | Candidato documental |
| **308** (1962-024A) | 30/10 | **52** | 160,551 | Candidato documental |
| **565** (1963-009B) | 24/11 | **31** | 209,869 | Candidato documental |
| **668** (1963-037A) | 12/10 | **10** | 141,563 | Candidato documental |
| 637 (1963-035A) | 07/11, NASA | 25 | 199,439 | Controle existente, só dia |
| 688 (1963-044B) | 12/11, AF IN | **1** | 182,309 | Intervalo 110 min, sem secante |
| 528 (1963-003B) | 08/11, NASA | 45 | 333,384 | Alvo, não controle |

A ordenação 292 → 308 → 565 → 668 reflete **somente disponibilidade de épocas catalogadas** para procurar evidência, não comparabilidade atmosférica, qualidade de sensor ou poder preditivo. A altitude proxy do 528 é maior e foi observada em outra data: não transferir densidade, escala de tempo ou parâmetro balístico de controle algum.

**Ganhos reais:** quatro identificadores e páginas de arquivo concretas; 146 épocas distintas somadas nesses quatro controles (53+52+31+10), **não 146 observações instrumentais independentes**. No modelo local n(t)=n0+s(t-t0), duas épocas distintas bastam para estimar *algebricamente* uma secante de catálogo. Isso **não** torna a secante uma previsão física, nem cria um erro de previsão de reentrada.

**Não identificados:** tempo terminal calibrado dos quatro novos controles, distribuição/σ de erro temporal, densidade atmosférica individual, massa/área/Cd, seleção e covariância instrumental. O intervalo documentado de 688 não corrige a falta de segunda época. MCMC histórico permanece NOT_RUN; posterior de massa/impacto, probabilidade de queda e restrição geográfica de Conde permanecem nulos, e a restrição ativa para 528 é falsa.

## Próximas observações discriminantes

Priorizar nos **boletins NASA originais contemporâneos** e em registros NORAD/AF IN quaisquer datas e, sobretudo, **intervalos/horas UTC instrumentais** de 292, 308, 565 e 668. Para cada objeto, exigir identificação física, instante/evento de término distinguido de data de catálogo, página/fac-símile/hash, estação e política de seleção, além da cadeia do TLE. Sem isso, a fonte de data não é independente do catálogo. Somente então congelar origem temporal, modelo físico e conjunto de validação antes de calcular erros preditivos, inclusive negativos.

**Reprodução:** executar 'python3 tools/c241_1963_terminal_control_screen.py --parquet /tmp/tle_1963.parquet --output /tmp/c241-1963-controls.json --check', após conferir SHA dos bytes; e 'python3 -m unittest discover -s tests -p test_c241_1963_terminal_control_screen.py -v'. A CI reexecuta Parquet pinado, 12 controles adversariais e asserções que impedem promoção indevida para calibração. Fonte original, script e relatório devem ser auditados no **SHA do HEAD testado**.

Articulação: [Conde #647](https://github.com/franklinbaldo/conde-incident/issues/647), [Cervo #4](https://github.com/franklinbaldo/cervo/issues/4), [Cafezinho #5](https://github.com/franklinbaldo/cafezinho/issues/5). Nenhuma mudança de evidência ativa ou modelo numérico foi promovida.
