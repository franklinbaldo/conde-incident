---
type: Guide
title: "C241-L18: observações compiladas de julho e controles posteriores ao decaimento do 528"
description: "Três fac-símiles NASA rastreados por página, bytes, fonte e limites de inferência; preserva conflito de dezembro."
---

# C241-L18: procurar o passado também nas órbitas que sobreviveram

**Pergunta científica:** os boletins de situação orbital publicados antes e
depois de 8/11/1963 oferecem novos observáveis para restringir os estados dos
NORAD 527/528/529 e os parâmetros comuns de gravidade e atmosfera?

**Resposta documental:** sim, há novos *registros de valores orbitais compilados*
com sua genealogia; **não** há, nesses PDFs, fichas brutas de sensores com
instante próprio, quadro de referência e covariâncias. Não contar três boletins
da mesma rede NASA/Goddard-NORAD-SAO como três observações independentes.

## Documentos com custódia

Dados, hash SHA-256, tamanho, índice de página e transcrição estão no
[ledger](nasa_ssr_jul_dec_1963_C241-L18.json). Os índices PDF são base zero.

- [NASA SSR v3 nº 15 de 31/07/1963, NTRS 19630012290, PDF p.7, impressa p.5](https://ntrs.nasa.gov/api/citations/19630012290/downloads/19630012290.pdf):
  3A 94,6 min, 537/458 km; 3B 93,6 min, 463/415 km; 3C
  93,9 min, 498/425 km. Inclinações 81,88° nas três linhas.
  SHA256 `9b00bf8323b1de80a34920f73c658f70f766a51632a13473a408679f0e5a03d9`.
- [NASA SSR v3 nº 23 de 30/11/1963, NTRS 19640002493, PDF p.7, impressa p.5](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf):
  3A 94,6 min, inclinação 81,88°, alturas 533/459 km;
  3C 92,2 min, inclinação 81,86°, alturas 390/368 km.
  O 3B não figura na tabela *Objects in Orbit*, coerentemente com
  o registro de seu decaimento no dia 8/11 feito no boletim de 15/11 (C197).
- [NASA SSR v3 nº 25 de 31/12/1963, NTRS 19640005618, PDF p.7, impressa p.5](https://ntrs.nasa.gov/api/citations/19640005618/downloads/19640005618.pdf):
  3A 94,6 min, inclinação 81,89°, alturas 530/461 km; 3C
  81,82°, alturas 335/333 km, com **período controverso**. O fac-símile
  foi lido como 89,2 min nesta rodada, mas C227 havia anotado 89,6 min.
  A divergência requer segunda leitura independente, sem apagamento da
  transcrição anterior.

A referência "as of 1200Z" refere-se à situação **computada/compilada**
para o boletim. Não é, sem o log de rastreamento original, o instante de cada
sensor. A listagem em 31/12 do 3C não fixa seu horário terminal, ainda que o
catálogo posterior indique decaimento nesse mesmo dia.

## Assimilação temporal e restrições científicas

Definir estados `x_j(t)` com dinâmica acoplada apenas por parâmetros físicos
comuns `g=(mu,J2,atmosfera(t),orientacaoTerrestre(t))`; cada peça mantém suas
próprias características (massa, área, coeficiente balístico, atitude).
Para cada linha `k` do objeto `j`, seu período, inclinação e altitudes
impressos alimentam um operador observacional `h_j(x_j(t_k),g)` **somente
após** definir época real `t_k`, convenção orbital e erro de medição/publicação.

Uma linha posterior à saída do 528 ainda pode restringir `g` usando
527 e 529, e assim retroagir sobre `x_528(t)` pela propagação conjunta.
Isso requer que a dependência compartilhada seja identificável. Caso
contrário, o novo dado informa apenas os parâmetros do objeto observado.
A incerteza não é obrigada a diminuir em toda métrica: fontes correlacionadas,
erros de modelo ou leituras inconsistentes podem deixar o domínio inalterado
ou revelar que o modelo precisa ser ampliado.

**Resultado aritmético condicional em Lean:** entre os boletins de
30/11 e 31/12, a mudança impressa do 3C excede a mudança impressa do
3A por pelo menos 2,40 minutos, admitindo ambos 89,2 e 89,6 e
arredondamento hipotético de 0,1 min. Isso **não** é uma taxa atmosférica,
nem uma medição de distância entre satélites, nem uma prova da hora/local de queda.

- Fonte: C241-L18; vínculos prévios C241-L11, C241-L12, C241-L16, C241-L17 e C227.
- Contrato de separações coépocas: C241-P10 (`RelativeTrajectories.lean`).
- Teoremas condicionais: `formal/Conde1963/SsrSurvivorIntervals.lean`.
- Status do domínio físico: **CONNECTED_PENDING_CALIBRATION**, sem exclusão
  de Conde, sem posterior numérica, sem inferência de rastreamento independente.

## Próximas medições a recuperar

Priorizar o SSR v3 nº 24 (meados de dezembro de 1963), boletins de 1964
com o 527 ainda em órbita, e principalmente registros *primários* de
observação NORAD/SAO com (estação, época UTC, direção/range, erro e frame).
CelesTrak disponibiliza solicitação histórica sob CAPTCHA: usar a
interface autorizada, sem contornar seus controles. Após recuperar um
TLE primário, ajustar primeiro 527/529 com holdout pós-528 antes de
projetar o intervalo de trajetória de 528 em 8/11.
