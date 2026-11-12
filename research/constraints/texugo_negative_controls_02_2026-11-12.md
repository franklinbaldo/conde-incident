# QA-TX-20261112-02 — ID novo não é medição nova

**Controle de falsificação de metadados (não é fonte histórica nova).** Issue de responsabilidade 🦡 Texugo [#19](https://github.com/franklinbaldo/conde-incident/issues/19); registro suplementar da [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), com C179 (TLE secundário 528) e C197 (dia de decaimento publicado pela NASA) mantidos em sua condição original.

## Ataques que passam no validador anterior

1. Copiar uma linha do mesmo boletim NASA, mudar o ID, o nome da variável e até o suposto `matrix_local_id`; `input_observations` e `candidate_constraints_recorded` aumentavam sem nenhuma nova observação.
2. Repetir a mesma tabela com novo ID e valor discordante; o validador não percebia a colisão de origem e objeto.
3. Reportar um número finito extremo em minutos: ao converter a segundos, o produto podia se tornar infinito apesar de o número de entrada passar na checagem `isfinite`.

## Regra e fronteira

O verificador agora recusa observações com IDs diferentes mas a mesma **fonte, objeto, observável, data de publicação, época de observação e época do elemento**. Duas leituras legítimas no mesmo documento devem ter **proveniência de linha/instrumento ou época individualizada**, não apenas um ID novo. O verificador também recusa conversões que produzam não finitos. Os dois boletins [NASA 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) e [30/11/1963](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf) têm a mesma linhagem de rastreamento NASA/NORAD; suas tabelas não foram reinspecionadas nesta alteração.

**Teste:** `python3 -m unittest discover -s tests -p 'test_cumulative_constraints.py' -v`; `python3 formal/scripts/check_cumulative_connections.py --output /tmp/conde-cumulative.json`. Esperado no corpus: 22 observações, 8 diferenças, 2 famílias documentais e 1 linhagem upstream, **zero** restrições físicas ativadas. Esses ataques são sintéticos e nunca constituem TLE primário, posição de queda ou probabilidade. A diferença de conectividade aceita para os ataques é **zero**, não um estreitamento físico de Θ. O projeto só pode ativar restrições após obter épocas instrumentais originais, erro e forward model calibrado.
