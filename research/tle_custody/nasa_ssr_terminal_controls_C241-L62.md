---
type: Guide
title: "C241-L62: dois controles de decaimento publicados sem hora terminal"
description: "Fac-símile NASA SSR novembro de 1963 para 292 e 565; separa dia catalogado, identidade retrospectiva e medição instrumental."
---

# C241-L62: dois controles de decaimento publicados sem hora terminal

A [Tartaruga #8](https://github.com/franklinbaldo/tartaruga/issues/8), recebida do Cervo, solicita observações terminais independentes para 292, 308, 565 e 668. Na edição NASA/GSFC **30/11/1963, volume 3 nº 23**, o fac-símile contém uma tabela suplementar na **página impressa 8, índice PDF 9**: *PLEASE ADD THE FOLLOWING TO THE DECAYED OBJECTS LIST*.

O original, [NTRS 19640002493](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf), já estava custodiado em **C241-L18**, com **1.266.393 bytes** e SHA-256 `9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d`. Esta leitura de uma nova página **não acrescenta uma publicação nem um sensor independente**.

| NORAD moderno (junção secundária) | Designador **impresso** em 1963 | Texto original de decaimento | Dia normalizado |
| --- | --- | --- | --- |
| **292** | `1962 SIGMA 1` | `26 NOV 63` | 1963-11-26 |
| **565** | `1963 9B` | `24 NOV 63` | 1963-11-24 |

Os números NORAD **292** e **565 não estão impressos nessa tabela**. A junção retrospectiva é externa: [292](https://keeptrack.space/satellite/292) associa o objeto a 1962-018A/1962 Sigma 1; [565](https://keeptrack.space/satellite/565) associa-o a 1963-009B. É preciso autenticar essa junção em registro institucional com número e designador juntos antes de considerá-la identificação primária.

**O que a folha prova:** a edição contemporânea publicou os dias acima, usando dados compilados da família NASA/Goddard–NORAD–SAO. **O que ela não prova:** hora UTC de reentrada, última detecção, estação, medida radar/óptica, precisão temporal, independência de outra fonte ou método de determinação. O marcador de corte editorial `1200Z`, quando impresso no cabeçalho, não é hora de decaimento. A ausência de relógio torna impossível calibrar aqui um erro temporal de horas ou minutos.

Os controles **308** e **668** permanecem `NOT_RECOVERED` quanto a documentação terminal contemporânea nesta rodada. As datas das páginas secundárias não foram promovidas à condição de fato instrumental. Nenhum dado foi transferido à trajetória de 528, à MCMC, ao modelo atmosférico ou a uma geografia de queda.

**Reproduzir:** `python3 -m unittest discover -s tests -p 'test_tle_ssr_terminal_controls_c241_l62.py' -v` e a mesma chamada com `python3 -O`. O workflow baixa a edição NASA original e verifica seu hash, tamanho e paginação. O auditor rejeita artificialmente timestamps, estações, independência ou precisão, inclusive em modo otimizado. Consultar [ledger JSON](nasa_ssr_terminal_controls_C241-L62.json) para campos nulos e os localizadores. Próxima busca específica: boletim SSR de outubro de 1963 para 308/668 e mensagens NORAD/AF IN com intervalo de reentrada, verificando a genealogia contra o espelho Space-Track.
