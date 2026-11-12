# QA-TX-20261112-04: observável, operador e estado não são intercambiáveis

**Tipo:** controle negativo sintético, não observação nova de 1963. **Responsável:** 🦡 Texugo, [issue #19](https://github.com/franklinbaldo/conde-incident/issues/19). Suplemento à [matriz cumulativa C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), com C197–C202 e C179#1 preservados; não cria um novo item histórico C.

## Contraprova discriminante

O validador já conferia se o ID do operador e dos parâmetros existia, mas não se **correspondia** à grandeza e ao objeto da linha NASA. Um atacante podia relabelar uma coluna de um mesmo boletim (por exemplo, declarar um novo `observable` e `variable_id`), apontar período nodal para operador de apogeu ou associar a linha 529 ao estado 527. O registro era aceito como modelo-conectado e podia aumentar a contagem sem nova observação.

O contrato específico das quatro colunas NASA SSR já registradas exige os pares `nodal_period/min/nodal_period_model`, `inclination/deg/inclination_model`, `apogee/km/apogee_model` e `perigee/km/perigee_model`, com parâmetros de estado do próprio NORAD 527/529 e variável latente da **publicação** correspondente. Esta última é um rótulo do modelo, NÃO a época observada instrumentalmente. A ponte C179 do 528 continua sob verificação literal específica, sem promoção a medição de sensor original.

Cinco testes de mutação sintética rejeitam: observável fabricado, troca de operador, troca dimensional de unidade, estado de outro objeto e parâmetro latente de outra data editorial. O corpus intacto continua com **22 observações, 8 diferenças publicadas, duas famílias documentais, um upstream de rastreamento e zero restrições ativadas**. A validação não calcula órbitas.

## Fonte, dependência e limites

Dois boletins contemporâneos NASA SSR [15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) e [30/11/1963](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf), pré-registrados no grafo, compartilham linhagem NORAD/AFS. **Esta fatia não reinspeciona o fac-símile, não cria uma medição primária nova e não aumenta independência.** C179#1 usa o literal TLE secundário de 528 com hash registrado; fontes instrumentais originais, épocas observadas, erro, referencial e conflito RAAN ainda faltam.

Reproduzir: `python3 -m unittest discover -s tests -p 'test_cumulative_constraints.py' -v` e `python3 formal/scripts/check_cumulative_connections.py --output /tmp/conde-cumulative-tx04.json`. Esperado: cinco ataques rejeitados, baseline aceito; nenhum narrowing de domínio em Lean, coordenada, hora ou probabilidade de impacto.
