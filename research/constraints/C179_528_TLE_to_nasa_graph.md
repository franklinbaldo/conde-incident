# C179#1 → NORAD 528 → NASA 527/529: ligação cumulativa verificada

**Pergunta falsificável.** O grafo que preservava 16 entradas NASA para 527/529 consegue incorporar seis campos de uma representação TLE secundária do 528, sem confundir epoch de referência com observação instrumental, contar espelhos como sensores independentes, ou promover RAAN 284,1520° sem fonte?

## Proveniência

- Matriz original congelada, C179#1: research/evidence_matrix_C001-C238_2026-11-11.md, Git blob SHA a7978c3a75a153b16ab70118a92c434bba674cb7.
- [Espelho secundário atribuído à AFSPC](https://www.itau.magnetic-declination.com/satellite/?s=528), par literal versionado em research/tle_custody/mirror_528_1963-10-27.tle, SHA-256 18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd; [auditoria C241-L1](../tle_custody/evidence_matrix_C241-L1_2026-11-12.md) verifica representação e checksum, NÃO custódia NORAD original em 1963.
- Epoch de **referência dos elementos TLE**: 1963-10-27T14:40:16.132512Z. Epoch das medições instrumentais usadas no ajuste, covariância e correspondência com o frame físico: desconhecidos.
- Seis campos **do mesmo registro**, não seis observações independentes: inclinação 81,8615°, RAAN 198,5261°, e 0,0017147, argumento do perigeu 104,7477°, anomalia média 255,4423°, movimento médio 15,74901460 rev/dia.
- RAAN legado 284,1520° foi introduzido no [commit inicial 807a118](https://github.com/franklinbaldo/conde-incident/commit/807a118939fac50b48d649b1045461bfcc79b140) em 11/11/2026 com comentário “Reconstructed nodal angle at epoch”, **sem referência instrumental**. Foi retirado de operação no [commit 0318594](https://github.com/franklinbaldo/conde-incident/commit/0318594011cce0c856eecfb0fb6debc5fc4a480b). Diferença aritmética 85,6259°, NÃO ângulo orbital observado.
- [NASA SSR 15/11](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) e [30/11](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf) fornecem 16 registros resumidos para 527/529; a publicação não fixa o instante de cada rastreamento. Não somar NASA e espelho AFSPC como dois sensores independentes.

## Ponte física condicional

Fórmulas para um proxy Kepler/J2 de elementos médios TLE, NÃO propagação SGP4 nem estado osculante:

    n_rad_s = 2*pi*n_rev_day/86400
    a_km = (mu_km3_s2/n_rad_s²)^(1/3)
    hp_km = a_km*(1-e)-R_equator_km
    RAAN_rate_rad_s = -1.5*J2*n_rad_s*(R_equator_km/(a_km*(1-e²)))²*cos(i)

Constantes matemáticas do modelo: mu = 398600,4418 km³/s²; raio equatorial = 6378,137 km; J2 = 1,08262668e-3. Recomputando independentemente dos campos auditados: **a = 6723,048603 km; h_perigeu = 333,383592 km; precessão nodal J2 proxy = −1,173124071 graus/dia**. A taxa não foi medida como variação temporal do RAAN.

| Progresso | Antes | Depois |
|---|---:|---:|
| Observáveis rastreados no grafo | 16 | 22 |
| Pontes físicas computadas para 528 | 0 | 1 |
| Objetos na ligação dinâmica de forças compartilhadas | 527/529 | 527/528/529 |
| Famílias documentais | 1 | 2 |
| Redes instrumentais tratadas como independentes | 1 não demonstrada | 1 não demonstrada |
| Restrições físicas duras ativadas | 0 | 0 |

O domínio físico admissível não sofreu redução verificada: ainda faltam origem do TLE, erros/covariância, epoch das observações e controle de frame. O domínio **do registro serializado** é determinado pelo hash, mas isso não implica que os elementos físicos reais sejam conhecidos exatamente. O encadeamento físico é uma hipótese conectada, não uma localização de reentrada.

**Holdout 527/529: NOT_RUN nesta fatia.** Sem épocas de observação e erros, a comparação de trajetórias em janelas comuns seria espúria. O resultado negativo anterior registrado em formal/Conde1963/Core.lean continua como controle: MAE quadrático 0,01412 rev/dia e conjunto H60 0,02595 rev/dia; NÃO são novos scores.

### Reprodução

    python3 -m unittest discover -s tests -p test_cumulative_constraints.py -v
    python3 -m unittest discover -s tests -p test_tle_literal_layout.py -v
    python3 -m unittest discover -s formal/tests -p test_physical_observable_bridge.py -v
    python3 formal/scripts/check_cumulative_connections.py --output /tmp/conde-528-handoff.json
    # Em CI com Lean 4.35.0: cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean

**Dado faltante para promover a restrição:** registro NORAD original de 528, série de épocas e conversão validada TLE→modelo, erros de medição e holdout sincronizado com 527/529. Só então calcular domínio antes/depois com testemunhas físicas e erro versus baseline. Não se acrescentaram teoremas Lean circulares. A biblioteca histórica Evidence.lean (154 proposições/151 rótulos, colisões C44–C46) segue **NOT_RUN**: busca de nomes de arquivos em /workspace não encontrou o pacote ZIP original.
