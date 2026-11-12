---
type: Guide
title: "C241-P6: teste de rotação sideral para o conflito RAAN de outubro"
description: "Confronto numérico condicional de 284,1520° versus 198,5261° com rotação Greenwich, dois carimbos e sensibilidade declarada."
---

# C241-P6: a diferença de RAAN não coincide com uma simples rotação de Greenwich

**Pergunta falsificável (issue #15):** e se o RAAN legado **284,1520°** e o RAAN **198,5261°** do par TLE secundário do NORAD 528 fossem o mesmo vetor nodal, mas com um deles expresso em um quadro girado de ±GMST em torno do eixo terrestre? A hipótese testada é **somente uma rotação de zero angular** no instante impresso, não uma transformação TEME/PEF completa nem uma calibração de sensores.

## Linhagem inspecionável

- C25#1, C179#1, C241-L8, C241-P5; o último já verificou que as épocas impressas de outubro diferem em apenas **16,132608 s**, enquanto o RAAN difere em **85,6259°**.
- Construção legada: duas linhas TLE copiadas do antigo src/lib/constants.ts, [blob Git SHA-1 0284f1217557b0ea891b5e51b6ac56bd13529d3f](https://github.com/franklinbaldo/conde-incident/blob/0284f1217557b0ea891b5e51b6ac56bd13529d3f/src/lib/constants.ts); **origem instrumental não recuperada**.
- Par secundário literal: [research/tle_custody/mirror_528_1963-10-27.tle](../tle_custody/mirror_528_1963-10-27.tle), SHA-256 18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd, espelho [itau.magnetic-declination.com](https://www.itau.magnetic-declination.com/satellite/?s=528), **não NORAD primário**. As duas linhas e checksums são verificados pelo parser existente.
- Equação sideral: [US Naval Observatory, Sidereal Time](https://aa.usno.navy.mil/data/siderealtime) define o relógio como UT1; a forma polinomial aproximada está em [Max Planck, Greenwich mean sidereal time, eq. 20](https://www2.mps.mpg.de/homes/fraenz/systems/systems3art/node10.html). Uso do polinômio GMST clássico em graus, com JD calculado a partir do carimbo UTC como **substituto hipotético de UT1**, pois a correção histórica UT1−UTC não foi recuperada.

## Resultados em graus, sem ajuste dos dados

Em cada carimbo, calcular GMST(JD_UTC_proxy) e os dois candidatos wrap(198,5261 ± GMST). O resíduo circular assinado é wrap180(284,1520 − candidato).

| Época impressa 1963 UTC | GMST proxy (°) | Candidato −GMST (°) | Resíduo (°) | Candidato +GMST (°) | Resíduo (°) |
|---|---:|---:|---:|---:|---:|
| Legado, 27/10 14:39:59,999904 | 255,240240 | 303,285860 | −19,133860 | 93,766340 | −169,614340 |
| Secundário, 27/10 14:40:16,132512 | 255,307643 | 303,218457 | **−19,066457** | 93,833743 | −169,681743 |

**Baseline sem rotação:** discrepância circular **85,625900°**. A melhor versão da hipótese elementar (−GMST) reduz a discrepância *aritmética* a **19,066457°**, mas não a zero. Ao variar o argumento de GMST em **±60 s** ao redor de cada época, o menor resíduo absoluto da versão −GMST no carimbo secundário ainda é **18,815773°**. Os 60 segundos são um teste de sensibilidade escolhido, **não** uma incerteza histórica observada de UT1−UTC.

A escala de correção temporal extra para fazer coincidir −GMST no carimbo secundário é cerca de **4563,46 s (76,06 min)**, e não os 16,13 s entre os dois TLEs. Isso não identifica o verdadeiro deslocamento temporal ou referencial; apenas expõe a magnitude requerida por esta transformação de um eixo.

**Controles e resultado negativo:** os dois sinais e ambos os carimbos foram confrontados, sem escolher a variante que se ajuste a posteriori. C241-P5 encontrou cruzamentos em agosto para 527/528/529, mas os três vêm da mesma linhagem secundária e não possuem um par legado autenticado coevo para validar um deslocamento de frame. Não há holdout instrumental independente nem erro em metros/km ou sigma de rastreamento: NOT_RUN. O teste **refuta apenas a explicação por uma rotação sideral simples sob o proxy UTC e a sensibilidade especificada**. Não refuta genericamente qualquer mudança de referência, época ou cópia histórica.

**Domínio antes/depois:** hipótese elementar de uma única rotação sideral de ±GMST nas épocas impressas: nenhum dos quatro candidatos zera o resíduo dentro do teste de ±60 s. Domínio físico admissível de órbitas e locais de reentrada **inalterado**, não-vazio **não reavaliado**: faltam TLE/medição primária do 528 com frame, época instrumental, histórico UT1−UTC, transformação de referência definida e erros/covariância. Não foi ativada restrição Lean; localização de queda **indeterminada**. Não tomar a data catalogada NASA C197#1 como posição de impacto.

## Reprodução

1. python3 -m unittest discover -s tests -p test_tle_legacy_sidereal_rotation.py -v
2. python3 tools/tle_legacy_sidereal_rotation.py
3. cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean

O script para caso real falha se o SHA-256 do TLE literal for alterado. Os testes de calendário J2000, sinal circular, dois carimbos, fonte pinada e controle de fuso horário são determinísticos. Não adiciona gate JSON fictício nem teorema sem dado físico.
