# QA-TX-20261112-03: identidade documental e linhagem

Controle negativo SINTÉTICO, não nova observação de 1963. Responsável: 🦡 Texugo, [issue #19](https://github.com/franklinbaldo/conde-incident/issues/19). O suplemento acompanha a [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), especialmente C179 e C197; não cria ID C histórico para um teste sintético.

## Ataques negativos

1. Alias de fonte: duplicar o boletim NASA 15/11 com outro source_id e source_family, replicando uma observação. O grafo anterior podia contar fonte e observação como independentes. Variar só #page=8 na URL não cria outro documento.
2. Data fabricada: copiar uma linha do mesmo documento e alterar published_on para 16/11 (fonte de 15/11), escapando da deduplicação. A data da publicação não equivale à época física de aquisição, ainda desconhecida.
3. Sensor inventado: substituir upstream_tracking_family em apenas uma das duas publicações NASA da mesma família, criando falsa origem instrumental.
4. Status cosmético: registrar link_status de medição primária confirmada mantendo constraint_status pendente.

Agora os quatro ataques são rejeitados por URL sem fragmento, concordância de publicação, consistência de linhagem da família e status de conexão pendente. Novas linhas comprovadamente distintas continuam permitidas; o verificador é uma defesa de proveniência, não um teste dinâmico.

## Fontes e custódia

[NASA SSR de 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) e [NASA SSR 30/11/1963](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf): publicações contemporâneas, uma linhagem de rastreamento NASA/NORAD. C179#1: [TLE secundário 528](https://www.itau.magnetic-declination.com/satellite/?s=528), literal SHA-256 18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd; origem instrumental primária não disponível. Não houve reinspeção visual dos fac-símiles nesta alteração.

Reprodução: python3 -m unittest discover -s tests -p test_cumulative_constraints.py -v ; python3 formal/scripts/check_cumulative_connections.py --output /tmp/conde-connected-handoff.json. Esperados 22 observações, 8 diferenças, 2 famílias documentais, 1 upstream e 0 restrições físicas ativadas. Nenhuma órbita terminal, probabilidade ou queda em Conde foi inferida; conflito RAAN permanece.
