# Custódia TLE, NORAD 527 / 528 / 529 (1963)

**Estado: auditoria de espelho secundário.** Esta fatia não recupera observações militares originais, não localiza reentrada em Conde e não identifica fisicamente a peça 528. É uma PR empilhada sobre a [fundação científica #1](https://github.com/franklinbaldo/conde-incident/pull/1), que contém a matriz C001–C238.

## Duas cadeias diferentes

1. **Origem alegada para a série numérica:** Space-Track.org (exportações em lote) → cópia/transformação Parquet disponível em [oxzoid/space-track-tle-history, arquivo 1963](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet) (fork da coleção juliensimon). O website descreve o acervo como extraído do Space-Track, **sem cadeia de custódia por observação, identificador do boletim AFSPC/Space-Track original ou imagem do registro de 1963**. Por isso ele é **espelho**, não fonte instrumental independente. Blob do arquivo com SHA256 declarado na página: `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` (275 kB, commit do fork `4b4fb3a`). O script rejeita qualquer arquivo cujos bytes não tenham esse hash.
2. **Par TLE divulgado por outro espelho:** [itau.magnetic-declination.com, NORAD 528](https://www.itau.magnetic-declination.com/satellite/?s=528). Capturadas as linhas **atuais publicadas** em [mirror_528_1963-10-27.tle](mirror_528_1963-10-27.tle). SHA256 do **arquivo com exatamente duas linhas e LF final**: `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; hashes das linhas ASCII sem LF: primeira `bb930fe1d4175af653490c327ec9d6cc4e4fb7be43d972bf3391b0f1c5144f36`, segunda `bd47f09ddd4648e6ae59b6fd03d86550c994b980f118486b1c03f589250f599a`. Ambos os dígitos de checksum TLE **passam** (0 e 4). Isto prova integridade *sintática das linhas preservadas*, **não autenticidade histórica ou equivalência com os bytes do Parquet**.

**Não confundir:** SHA-256 verifica arquivo; checksum de TLE verifica 68 colunas de um par específico; proveniência de rastreamento requer um registro primário; identidade física requer documento de engenharia/objeto. São quatro perguntas distintas.

## Par secundário NORAD 528, não primário

| Campo de linha 1/2 | Resultado observado no par espelhado |
|---|---|
| Número e designador | 00528, 63003 B |
| Época bruta | `63300.61129783` (dia do ano com fração) |
| Época interpretada | **1963-10-27 14:40:16.132512 UTC**, não 14:40:00 |
| Inclinação | 81,8615° |
| RAAN | **198,5261°** |
| Excentricidade | 0,0017147 |
| Argumento do perigeu / anomalia média | 104,7477° / 255,4423° |
| Movimento médio | 15,74901460 **revoluções/dia** |
| `n-dot / 2` em campo de linha 1 | 0,00686563 (metade da derivada, **não** a derivada total) |
| BSTAR em linha 1 | zero na linha espelhada; **não** é prova de arrasto físico nulo |
| Checksum dos dois registros | PASS sintático, 0 / 4 |
| Autenticidade primária NORAD e frame original | **NOT_VERIFIED** |

O [script legado na main](https://github.com/franklinbaldo/conde-incident/blob/main/norad528_reconstruction.py) assume **RAAN 284,1520°** e **e 0,00842**, sem vincular uma linha original identificável. A diferença angular pontual é **85,6259°**. O script antigo ainda assume horário arredondado 14:40:00. Não selecionar a série por resultar numa trajetória conveniente; antes verificar **mesma época, catálogo, elemento médio/osculador, frame, fonte e sequência**. Não transformar RAAN de um referencial em outro ad hoc. O par secundário não resolve sozinho o conflito entre séries.

## Extração reproduzível, sem forjar TLE

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pip install pyarrow==21.0.0
python tools/audit_norad_1963.py --download \
  --parquet /tmp/tle_1963.parquet --output /tmp/norad-1963-audit
```

A rotina lê **apenas** os IDs 527/528/529, mantém época UTC até microssegundos, índice original de linha, unidades/colunas originais, duplicatas, limites físicos, contagem de registros e épocas únicas. Produz `norad_527_528_529_1963_numeric.csv` e `audit.json`. O CSV é uma **extração numérica auditável**, não reconstrução de duas linhas TLE; os campos com floats reformatados não preservam necessariamente os dígitos/codificação originais. Não gera linhas TLE. Se campo/fuso/hash estiver ausente ou inválido, **FAIL**. O workflow [`tle-custody.yml`](../../.github/workflows/tle-custody.yml) faz o download pela rede autorizada do GitHub Actions e preserva saída como artefato, com SHA do HEAD.

Os contadores históricos **21/45/57** encontrados em C25 e **20/45/54** na ficha são **alegações de cortes/acervos distintos**. O extrator registra os valores *efetivamente lidos* sem tratá-los como equivalência, e não aceita um número fixo de linhas como prova de autenticidade. Ausência de registros no espelho não é prova de ausência original.

Os testes unitários empregam dados inventados **expressamente sintéticos** e contraprovas; o teste do par 528 usa a transcrição literal do espelho atual. **Nenhum teste de dinâmica SGP4, holdout histórico, declínio terminal ou previsão de impacto é reivindicado.**

## Fontes primárias e linhagem de identidade

- **NASA/Goddard, *Satellite Situation Report* 15/11/1963, p. impressa 8**, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf): seção `DECAYED OBJECTS` traz 1963-003B com **dia 8 NOV 63**, mas sem horário/local. Esta página foi documentada e visualmente auditada na matriz C197, **não reinspecionada nesta fatia**. A NASA incorporava rastreamento NORAD, portanto não é corroborador instrumental independente do espelho.
- **NRO, *The SIGINT Satellite Story*** (obra institucional concluída em 1994, versão parcialmente desclassificada/recuperada em 2016), [PDF institucional liberado](https://www.governmentattic.org/19docs/NRO-SIGINTsatStory_1994u.pdf): matriz C172–C173 aponta missão 7153/FTV 2313 como SIGINT **não tripulada**, sem identificar a peça S00528. Não se assume leitura visual deste PDF nesta fatia.
- **GCAT/McDowell, [currentcat](https://planet4589.org/space/gcat/data/derived/currentcat.html)** (catálogo histórico derivado): S00527=payload 1963-003A, S00528=component 1963-003B, S00529=component 1963-003C; associação física de 528 a tampa, cobertura, esfera ou estágio permanece **indeterminada**. O rótulo genérico Agena D não deve sobrepor o registro de Agena B da missão sem documento de engenharia.
- **CelesTrak, [TLE format](https://celestrak.org/columns/v04n03/)**: posições/checksum e interpretação de unidades; formato TLE contemporâneo **não é fac-símile de 1963**.
- Matriz cumulativa [C172–C202](../evidence_matrix_C001-C238_2026-11-11.md), rastreia dependência e registra falhas de previsões de holdout. A presente fatia acrescenta C240, **sem alterar retroativamente os IDs anteriores**.

**Limite decisivo em aberto:** precisamos de arquivos brutos primários NORAD/USAF/Space-Track de 1963, para 527/528/529, com arquivo original por época e eventual identificação de objeto, antes de auditar 45 registros de 528 como TLEs originais e resolver o conflito RAAN. Sem captura não se preenche o vazio com órbita sintética.


## Confronto de espelhos no mesmo instante (C241, 11/11/2026)

O extrator agora faz **comparação dos dados, não somente de checksums**. Lê o par literal 528 de 27/10 já preservado e validado, interpreta o campo de dia e fração com `Decimal` exato, busca por **época dentro de meia unidade da resolução TLE (432 µs)** as linhas 528 do Parquet original com SHA fixado, e confronta independentemente inclinação, RAAN, excentricidade, argumento de perigeu, anomalia média e movimento médio. As tolerâncias explicitadas no código só admitem arredondamento float32 do espelho; não são tolerâncias orbitais nem licença para escolher uma órbita. Comparar dois espelhos da mesma cadeia NORAD não constitui duas observações físicas.

`audit.json -> mirror_comparison_528.status` pode ser `MATCH_WITHIN_ROUNDING`, `FIELD_DIVERGENCE`, `NO_MATCHING_EPOCH` ou `AMBIGUOUS_DUPLICATE_EPOCH`. **Nenhum dos quatro resolve a autenticidade histórica:** se não houver coincidência, preservar o resultado negativo em vez de alterar arbitrariamente épocas/RAAN. O relatório inclui cada índice `source_row`, a diferença temporal, diferenças de cada campo, SHA-1/SHA-256 do par literal, hashes das linhas e o contraste legado 284,1520° sem usá-lo como dado observado. A passagem do relatório ao GitHub Actions ainda depende de run real em HEAD, não se proclama resultado do confronto antes da execução do Parquet.

A exportação inclui agora `norad_528_epochs_1963.csv`, separado do CSV geral, com **todas as linhas 528 realmente presentes**, índices preservados e hash SHA-1/SHA-256 de ambos os CSVs em `audit.json -> derived_file_hashes`. Não se completa artificialmente até 45, não se colapsam duplicatas: `duplicate_epoch_conflicts` separa a coincidência temporal com valores discordantes da simples repetição idêntica. Não há linha original de radar de 1963, código TLE, checksum de cada um dos 45 ou frame autenticado disponível nesse espelho, portanto essas provas ficam **NOT_RUN/NOT_VERIFIED**.

Os controles sintéticos verificam UTC e dia ordinal não bissexto, envolvimento angular 359,99°↔0,01°, coincidência dentro do arredondamento, divergência deliberada de RAAN 284,1520°, ausência de época e duplicidade conflitante; checam também que o CSV usa LF real e tem hash de saída reproduzível. O teste com bytes do par espelhado de 528 valida *sintaxe*, não origem instrumental.

**Tentativa de fonte secundária adicional:** as páginas públicas de 527 e 529 no espelho itau retornaram HTTP 502 nesta rodada, logo não foram transcritas nem consideradas resultados negativos sobre a existência de TLEs. O acervo numérico original permanece restrito ao Parquet fixado. **Observação decisiva ainda ausente:** pares TLE originais/boletins de elementos de 527–529 com proveniência do sistema de rastreamento, frame e época de emissão, e identificação de engenharia da peça S00528.


## Resultado executado no acervo integral de 1963 (CI de 11/11/2026)

**Fato agora efetivamente verificado no GitHub Actions**, não somente declarado pelo card: [workflow de custódia #43104710399](https://github.com/franklinbaldo/conde-incident/actions/runs/43104710399) e [verificações científicas #43104710510](https://github.com/franklinbaldo/conde-incident/actions/runs/43104710510) finalizaram **PASS no SHA `964d142716efbe60a7ae687ff52d3bde98ac8e71`**. O workflow baixou e conferiu o Parquet `SHA256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, `SHA1 623b8a57c959d980f013a9ba5e4bf4a8559adc69`, executou **14/14 testes** e produziu [artefato CSV+JSON #13894270124](https://github.com/franklinbaldo/conde-incident/actions/runs/43104710399/artifacts/13894270124). O próprio ZIP do artefato tem SHA-256 `66557f245f8df98d1f6b92cb1cc961654b58261c14b1f9c1d74e4a2f1a511f36`, segundo log GitHub.

| Objeto | Linhas 1963 | Épocas UTC distintas | Mesma época repetida | Duplicatas conflitantes |
|---|---:|---:|---:|---:|
| NORAD 527 | 21 | 20 | 1 | 0 |
| NORAD 528 | **45** | **45** | 0 | 0 |
| NORAD 529 | 57 | 54 | 3 | 0 |

A contagem anterior **21/45/57** em C25/C123 era *linhas*, enquanto **20/45/54** era *épocas únicas*. A incompatibilidade de contagens estava portanto na **definição estatística**, não em 7 elementos ausentes. Essa conclusão diz respeito exclusivamente ao espelho com hash conferido, não a uma auditoria dos TLEs primários.

**Confronto do 528:** índice físico do Parquet `source_row=3017`, época **1963-10-27 14:40:16.132512 UTC**; TLE espelhado com idêntica época (`epoch_delta_seconds=0`), e RAAN Parquet `198.52609252929688°` comparado ao campo literal `198.5261°`, diferença **0,000007470703°**. Os **seis campos** passaram no limiar de arredondamento `float32` (`MATCH_WITHIN_ROUNDING`). O dado do app `284.1520°` permanece sem linhagem e **conflito NÃO RESOLVIDO**. Coincidência entre dois espelhos pode simplesmente indicar cópia da mesma exportação.

**Hashes dos derivados:** CSV geral SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`; CSV exclusivo das 45 épocas do 528 SHA-256 `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`. Ver todos os campos de custódia em `audit.json` no artefato.

**Validação neste HEAD posterior às anotações:** os runs citados validam precisamente `964d142`; novas alterações meramente documentais requerem verificação do respectivo HEAD antes de revisão e integração. **Ainda ausentes:** 45 pares de linhas históricas originais com seus checksums, identificação material da peça 528, frame e registros de radar primários, observação terminal com UTC/local. Não se infere impacto em Conde.

## Correção dos insumos operacionais legados por decisão do proprietário (11/11/2026)

**Decisão aplicada ao código, não autenticação primária:** o app `src/lib/constants.ts`, a exportação Python e `norad528_reconstruction.py` deixaram de usar o vetor sem cadeia de fonte `RAAN=284,1520° / e=0,00842 / época 14:40:00` como insumo nominal do **528**. Agora usam exatamente o par TLE secundário preservado neste diretório: época `63300.61129783`, RAAN `198,5261°`, e `0,0017147`, argumento do perigeu `104,7477°`, anomalia média `255,4423°` e n `15,74901460 rev/dia`. O instante de `Date` em JavaScript tem precisão de milissegundos (`14:40:16.132Z`), enquanto o campo literal TLE conserva os `132512` microssegundos.

**Custódia:** URL do espelho itau, SHA-256 das duas linhas `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; confirmação numérica de mesma época por `source_row=3017` no Parquet oxzoid `SHA256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. Ambas as cópias podem derivar de uma fonte comum. A escolha operacional significa **melhor rastreabilidade entre os dados disponíveis**, e não resolução instrumental do conflito. O valor 284,1520° segue documentado aqui e no histórico Git para auditoria; não é mais silenciosamente tratado como elemento observado.

Para **527 e 529**, cujos vetores embutidos no app não dispõem de par TLE autenticado, a classificação foi rebaixada para `HIPOTESE` e a proveniência sinaliza explicitamente o cenário sintético legado. Os pares ainda presentes nas estruturas são placeholders que mantêm a compatibilidade de código, **não observações históricas**; não devem fundamentar reconstruções cruzadas/holdout antes de substituição por épocas do CSV custodiado. A cronologia foi corrigida para não apresentar esses vetores como TLEs oficiais, nem a marca `23:59` como horário observado de decaimento. Os valores de passagem terminal produzidos pelo modelo antigo continuam **exploratórios, não previsões físicas**.

**Regressão reproduzível:** `python -m unittest discover -s tests -p 'test_*.py' -v`, incluindo `tests/test_orbital_constants_provenance.py`, bloqueia retorno de RAAN, época e elementos sem fonte ao código operacional e a classificação primária falsa de 527/529. CI de custódia deve validar o novo HEAD antes de merge. Não há novo documento primário, horário terminal ou localização de queda.

## Auditoria temporal adversarial da RAAN legada (C241, complemento de 11/11/2026)

A comparação inicialmente aceitava épocas numéricas separadas por até **1 segundo**, apesar de a fração decimal do dia no TLE (8 dígitos) ter incremento de **0,000864 segundo**. Isso poderia criar uma falsa "mesma época" e passar despercebido a quem observasse apenas a RAAN. O código passou a usar `timedelta` com contagem inteira de microssegundos, tolerância inclusiva de **432 µs** (meia unidade de quantização do campo TLE), e um status separado `NEAR_EPOCH_NOT_EQUAL` para diferenças de **433 µs a 1 s**. Os casos com delta maior continuam `NO_MATCHING_EPOCH`; candidatos próximos permanecem no relatório como **dados não correspondentes**, sem ser descarregados ou fundidos. O valor exato conhecido no espelho Parquet é delta **zero**; a correção não exige mudar a observação.

O mesmo relatório `audit.json -> mirror_comparison_528.legacy_raan_temporal_audit` pesquisa o valor **284,1520° apenas como chave angular** em **todas as épocas reais** do 528, ordenando os três registros do espelho secundário mais próximos, com `source_row`, `epoch_utc`, `distance_to_legacy_deg` e deslocamento temporal em dias relativamente a 27/10. Também conserva os valores **somente** da época do par literal, para impedir a substituição de uma época por outra. Esse confronto é um diagnóstico de possível erro de data/transcrição, não uma hipótese ajustada nem uma prova de que o vetor legado tenha existido naquele instante: proximidade angular isolada não recupera frame, formato de elemento, cadeia instrumental ou peça física.

A [página oficial de arquivos históricos CelesTrak](https://celestrak.org/norad/archives/) lista séries públicas sobretudo entre **1980–2004** e direciona pedidos fora dessas coleções (inclusive **1963**) a **Special Data Request**. Foi consultada publicamente, sem enviar pedido: **nenhum par instrumental de 1963 foi obtido por essa via**. A [TLE API listada na página NASA Open APIs](https://api.nasa.gov/) é descrita como atualização **diária** derivada de CelesTrak, não documentação primária da época de 1963. Também não é fonte orbital independente para resolver 198° versus 284°.

**Reprodução:** `python -m unittest discover -s tests -p 'test_*.py' -v` testa desvios sintéticos de 432/433 µs, 1,000001 s, duplicidade e confronto de valor em datas distintas. A execução sobre o Parquet SHA-256 fixado é a mesma rotina de extração do workflow, que produz hashes dos CSV e o ledger completo. Não se atesta o novo HEAD antes de observar seu CI.

### Observação efetiva do corpus pinado, não inferência de origem da RAAN

A execução real do [NORAD custody #43113160100](https://github.com/franklinbaldo/conde-incident/actions/runs/43113160100), no commit de código e testes `49a833844e9476c23bcc990508838f2e582b0bce`, concluiu **success**, com **22/22 testes PASS** e download/extração do Parquet no SHA-256 já fixado. O confronto com a época do TLE literal continuou `MATCH_WITHIN_ROUNDING` e índice **3017**. Na pesquisa dos **45 registros reais** do 528 pelo valor 284,1520°, o ponto *angularmente* mais próximo foi:

| Campo auditado | Resultado computado a partir do espelho |
|---|---|
| Linha fonte | `source_row=2998` |
| Data/época UTC | **1963-08-12T13:35:30.863616Z** |
| RAAN do espelho | **284,3310852050781°** |
| Distância angular de 284,1520° | **0,1790852050781°** |
| Separação em relação à época literal do par 528 em 27/10 | **−76,04496839 dias** |
| RAAN na época literal de 27/10, linha 3017 | **198,52609252929688°** |

Isso é um **novo teste discriminante, com resultado negativo para a identidade de época**: a melhor proximidade encontrada é **76 dias antes**, e o registro 3017 no dia 27/10 continua em 198,5261°. Uma hipótese de transposição/confusão de época passou a ser investigável, mas a distância de 0,179° e a similaridade angular por si sós **não provam** que 284,1520° veio do registro de agosto; tampouco provam que o valor foi inventado. Antes de optar entre hipóteses, exigir uma cadeia primária do vetor legado, época, quadro de referência, elemento médio e tipo de propagador. **Nenhuma órbita ou local de impacto foram ajustados a partir dessa busca.**

A reconciliação de tolerância temporal (432 µs) também passou no conjunto real com diferença de época **0 µs**. O log do workflow exibe os três vizinhos angulares com índices e datas, enquanto o artefato `audit.json` mantém os 45 registros completos e sua fonte. Os demais dois vizinhos mais próximos são `source_row=2999` em 16/08 (280,112396°) e `source_row=3000` em 20/08 (275,108093°). Essas proximidades são **dependentes de um único acervo numérico secundário**, não novas observações NORAD independentes.


### Gate contra falso CI de HEAD

O GitHub Actions acionado por `pull_request` usa por padrão o ref sintético `refs/pull/N/merge`; uma execução com `github.sha` nesse evento demonstra o **merge de teste**, não necessariamente o SHA do HEAD de origem. Por isso o workflow de custódia agora faz checkout explícito de `${{ github.event.pull_request.head.sha || github.sha }}`, verifica que `git rev-parse HEAD` é exatamente esse SHA, imprime `audited_source_head=`, e nomeia o artefato com a mesma identidade. Há teste automatizado de não regressão desta configuração. `workflow_dispatch` continua a usar o SHA fornecido pelo evento, igualmente atestado.

As execuções anteriores, inclusive [#43113160100](https://github.com/franklinbaldo/conde-incident/actions/runs/43113160100), **continuam demonstrando os dados e controles naquela versão**, mas não devem ser rotuladas como atestação do checkout do HEAD exato. A nova atestação só vale após CI verde do commit que contém esta correção. O **workflow científico separado** mantém seu próprio escopo/gate; esta correção não alega ter mudado seu checkout.


## Confronto adversarial dos seis campos legados, sem trocar épocas (C241-T2, 11/11/2026)

**Pergunta falsificável:** a aparente aproximação angular entre `RAAN=284,1520°` e um registro do espelho em agosto significa que o **vetor completo** do simulador antigo foi extraído de alguma das 45 épocas numéricas do NORAD 528? O teste não escolhe o registro mais conveniente nem monta um vetor somando campos de datas diferentes.

**Cadeias e objetos distintos:**

- **Origem do vetor alegado:** `src/lib/constants.ts` **anterior à PR #14**, blob Git SHA-1 `0284f1217557b0ea891b5e51b6ac56bd13529d3f`, continha as linhas literais `63300.61111111`, `284.1520`, `0084200`, `142.3150`, `218.4210` e `15.74900000`. O programa [`tools/legacy_528_fingerprint.py`](../../tools/legacy_528_fingerprint.py) conserva essas duas linhas **rotuladas como legado não autenticado**, com checksums de formato válidos. Um checksum válido pode acompanhar dados digitados manualmente; **não** comprova emissão NORAD.
- **Série testada:** `norad_528_epochs_1963.csv`, SHA-256 `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`, derivado das **45 épocas** do único [Parquet oxzoid pinado](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. O material-fonte continua secundário e não constitui radar adicional.
- **Checagem:** simultaneamente `inclination`, `raan`, `eccentricity`, `arg_perigee`, `mean_anomaly`, `mean_motion`; índices de linha e época são mantidos. Tolerâncias de **serialização textual/float32 apenas**, detalhadas no código, não são erro orbital: 0,00008° nos ângulos, 0,00000006 em excentricidade e 0,000000006 rev/dia em movimento médio. A época é confrontada separadamente no limiar de 432 µs. Não se confunde coincidência de uma coluna com coincidência dos seis campos.

**Resultado realmente executado:** [NORAD custody #43122019452](https://github.com/franklinbaldo/conde-incident/actions/runs/43122019452), SHA de fonte `cb52253845f607d835f98839423b091d730cfda6`, **SUCCESS, 30 testes PASS**; [Scientific checks #43122019297](https://github.com/franklinbaldo/conde-incident/actions/runs/43122019297) também SUCCESS. O log audita `audited_source_head=` igual ao SHA de fonte, download Parquet e comparação adversarial. **Zero das 45 épocas coincide com os seis campos**, e **zero coincide com a época literal legada** (27/10 às 14:39:59,999904 UTC, distinta da linha rastreável 27/10 às 14:40:16,132512 UTC).

| Campo no registro *mais próximo por RAAN* (`source_row=2998`, 12/08/1963 13:35:30,863616 UTC) | Desvio absoluto para o vetor legado |
|---|---:|
| Inclinação | 0,007701660156° |
| RAAN | **0,179085205078°** |
| Excentricidade | 0,005076799922 |
| Argumento do perigeu | 97,491898956299° |
| Anomalia média | 97,025411132813° |
| Movimento médio | 0,300998650000 rev/dia |

**Conclusão restrita:** a hipótese simples de que **a linha de agosto inteira** originou o vetor legado fica **refutada dentro das 45 linhas do espelho**: no próprio candidato selecionado exclusivamente por RAAN, os demais elementos discordam muito além do arredondamento. Isso **não refuta** que 284,1520° tenha sido tirado isoladamente de outro registro, quadro de referência ou fonte ainda não recuperada; tampouco demonstra uma origem manual específica. Um par inventado pode passar checksum, e um espelho pode repetir informação instrumental antiga sem comprová-la.

**Handoff para o fluxo científico:** C241-T2 é um **controle de coerência de proveniência**, não uma nova medição e não uma restrição dinâmica autenticada em Lean. O conjunto de candidatos de igualdade literal entre o vetor legado e as 45 épocas secundárias é **vazio**; o subconjunto rastreável para 27/10 do *espelho* continua **não vazio** (linha 3017) e distinto. Esses domínios se referem à identificação de registros digitais, **não** a parâmetros físicos admissíveis da reentrada. Não passar 284,1520° ao simulador físico como medição de 1963; qualquer formalização Lean posterior deverá ser **condicional** à autenticação do quadro, da época, das linhas NORAD originais e às dependências. Nem a existência do vetor 528 comprova colisão com o solo.

**Reproduzir no checkout da PR #14:**

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pip install pyarrow==21.0.0
python tools/audit_norad_1963.py --download --parquet /tmp/tle_1963.parquet --output /tmp/tle-audit
python tools/legacy_528_fingerprint.py --csv /tmp/tle-audit/norad_528_epochs_1963.csv --output /tmp/tle-audit/legacy_528_fingerprint.json
```

O `legacy_528_fingerprint.json` é arquivado com o CSV e `audit.json` pelo workflow. Ainda **NOT_RECOVERED**: 45 pares TLE primários e seus checksums originais, elementos/frame NORAD por época, boletins de radar, identidade de engenharia da peça 528 e observação terminal UTC/geográfica. Nenhum contato, publicação no blog ou merge.


## C241-T3 — disponibilidade temporal cruzada 527/528/529 (12/11/2026 UTC, 🐢)

**Questão delimitada:** em cada uma das 45 épocas do NORAD 528 no
espelho numérico de 1963, qual é a época registrada mais próxima para
527 e 529? Há coincidência exata (0 µs), proximidade de meia unidade
de época TLE (432 µs), ou disponibilidade em bandas de 6, 24 e 72 horas?
As bandas são **perguntas pré-fixadas sobre cobertura do catálogo**,
NÃO erros instrumentais, medições simultâneas ou uma interpolação
orbital autorizada. Um vetor catalogado num dia não fornece o vetor
físico de outro objeto numa hora distinta.

Ferramenta: [auditoria temporal](../../tools/cross_object_epoch_support.py).
Ela verifica o SHA-256 do CSV geral derivado
3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231
antes de ler os registros, além dos controles prévios do extrator
sobre o Parquet de origem. Preserva cada source_row física; conserva
duplicatas equivalentes e **falha** se a mesma época/objeto contiver
estados divergentes. Rejeita épocas sem UTC, campos não finitos e
índices físicos duplicados. Relata sinal e distância absoluta em µs
até cada vizinho de 527/529, inclusive quando o vizinho esteja depois
da época 528, e conta fontes cronológicas distintas reutilizadas
para não inflar o número de testemunhos. Empates vão para a época anterior.
O JSON preserva uma linha 528 por época e as datas limites do acervo.

Reprodução no HEAD da PR #14:

~~~sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pip install pyarrow==21.0.0
python tools/audit_norad_1963.py --download --parquet /tmp/tle_1963.parquet --output /tmp/tle-audit
python tools/cross_object_epoch_support.py --csv /tmp/tle-audit/norad_527_528_529_1963_numeric.csv --output /tmp/tle-audit/cross_object_epoch_support.json
~~~

O workflow de custódia anexa cross_object_epoch_support.json com os
CSVs auditados. **Os números reais das janelas dependem de CI do HEAD
final**: testes sintéticos só mostram o funcionamento do método, não
a cobertura da série histórica. A contagem completa de 45 épocas
continua C241-T2 e é uma contagem da cópia, não de transcrições
instrumentais primárias.

Fonte da árvore de dependências: [espelho oxzoid 1963, revisão
4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet),
Parquet SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09.
NORAD 527/528/529 neste arquivo podem compartilhar a mesma cadeia
Space-Track. A versão de 528 do [espelho itau](https://www.itau.magnetic-declination.com/satellite/?s=528)
não certifica independência física da medida. O [NASA Satellite
Situation Report 15 Nov 1963, p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
registra o dia 8/11, não hora ou local terminal.

**Fluxo até o simulador:** estes são apenas pares de épocas
*documentalmente* admissíveis para solicitar eventual ajuste conjunto.
Não são restrições físicas Lean certificáveis nem um domínio dinâmico
não vazio. Para transformá-los em limite orbital, permanecem
indispensáveis a série NORAD primária com frame, época, tipo de elemento
e erro instrumental, seguida de propagação e holdouts numéricos
calibrados. Não escolher 284,1520° ou 198,5261° por conveniência,
não inferir fase/posição geográfica, e não tratar reentrada como
queda confirmada em Conde. Identidade física da peça S00528 segue
sem documentação primária de engenharia.


### C241-T3: resultados do acervo pinado, observados em CI do HEAD 4ed7c63

[Custódia Actions #43130028928](https://github.com/franklinbaldo/conde-incident/actions/runs/43130028928)
concluiu **SUCCESS no source HEAD 4ed7c635600f1b7510e2132fea8ea3b583620ea6**,
registrado também como audited_source_head no log; **39/39 testes PASS**,
Parquet e CSV com SHA-256 conferidos e saída JSON arquivada no
[artefato #13904024160](https://github.com/franklinbaldo/conde-incident/actions/runs/43130028928/artifacts/13904024160),
digest ZIP SHA-256 902766df555d796458fae5f730bdea64b25f86cdb26ca04025109931131f46ed.
[Scientific checks #43130028914](https://github.com/franklinbaldo/conde-incident/actions/runs/43130028914)
também SUCCESS no mesmo HEAD.

| Janela de proximidade temporal | Épocas 528 com 527 próximo | Épocas 528 com 529 próximo | 527 **e** 529 próximos, cada um |
|---|---:|---:|---:|
| até 6 horas | 2 | 6 | **1** |
| até 24 horas | 5 | 18 | **2** |
| até 72 horas | 16 | 35 | **15** |
| mesma época UTC, delta 0 µs | 0 | 0 | **0** |
| proximidade ≤432 µs | 0 | 0 | **0** |

**Novo resultado negativo importante:** das 45 épocas 528 deste arquivo,
**nenhuma** tem horário **exatamente igual** ao de 527 ou 529, nem
correspondência dentro de meia unidade de quantização temporal TLE.
As 15 épocas 528 que têm *ambos* os outros objetos a até 72 h
não são 15 observações instrumentais simultâneas. Dentro de 72 h,
os vizinhos mais próximos efetivamente reutilizam apenas **13 épocas
distintas do 527** e **28 do 529**. Tratar todos como medidas
independentes inflaria artificialmente a informação.

Extremos da série secundária: 528 de **17/01/1963
16:18:12.350304 UTC** até **27/10/1963 14:40:16.132512 UTC**; 527
até **17/12/1963** e 529 até **30/12/1963**. Não há no espelho fixado
época posterior a 27/10 para 528: qualquer extrapolação até 08/11 exige
modelo, erro acumulado e validação, e **não é observação terminal**.
A data NASA do dia 08/11 segue sem horário ou posição.

**Limite epistêmico:** zero coincidências exatas significa apenas zero
registros com timestamps iguais no espelho secundário pinado,
não ausência de rastreamento histórico nem impossibilidade de ajuste
conjunto. O conjunto de linhas próximas é documental, não restrição
Lean física; não resolve o conflito RAAN nem prova impacto.


## C241-T4: grade temporal TLE e gate para epocas contraditorias (12/11/2026 UTC)

**Pergunta estrita:** os carimbos UTC do CSV secundario, sem recuperar line1/line2, sao *representaveis* pela grade de 8 casas decimais do dia do formato TLE (864 microssegundos por unidade a partir de 00:00 UTC)? A [especificacao CelesTrak](https://celestrak.org/columns/v04n03/) define o campo da linha 1, colunas 21–32; e **documentacao tecnica posterior**, nao um boletim NORAD de 1963.

Fatia verificavel: [tools/tle_epoch_grid_audit.py](../../tools/tle_epoch_grid_audit.py), [seis contraprovas sinteticas](../../tests/test_tle_epoch_grid_audit.py) e um teste de contradicao de estados no extrator. A ferramenta exige o CSV integral SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`, conserva `source_row`, verifica UTC sem float e publica `tle_epoch_grid_report.json`. **Novo gate fail-closed:** estados numericos distintos para mesmo NORAD+epoca deixam `audit.json` rastreavel, mas agora impedem sucesso do script; duplicatas identicas nao falham.

**Resultado empirico no arquivo fixado:** [CI custodia #43136329241](https://github.com/franklinbaldo/conde-incident/actions/runs/43136329241), commit de codigo `e96c54871c25de56336a042778071154eaa33d06`, **46/46 testes PASS**, Parquet e CSV fonte SHA-256 conferidos. Todos os **123/123 carimbos** caem *exatamente* na grade: 527 **21/21** (20 epocas distintas), 528 **45/45** (45), 529 **57/57** (54). Desvio maximo: **0 µs**, nenhum `OFF_GRID`; zero conflito de duplicata no espelho validado. [Verificacoes cientificas #43136329367](https://github.com/franklinbaldo/conde-incident/actions/runs/43136329367) aprovaram no mesmo SHA. Uma hipotese testavel (compatibilidade representacional com epoca codificada em 8 decimais) **nao foi falsificada**; isso **nao** demonstra que essas 123 linhas tenham sido originadas de TLEs primarios, e muito menos que 45 observacoes instrumentais individuais sobrevivam.

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/tle_epoch_grid_audit.py \
  --csv /tmp/norad-1963-audit/norad_527_528_529_1963_numeric.csv \
  --output /tmp/norad-1963-audit/tle_epoch_grid_report.json
```

**Linhagem de dados:** fonte secundaria [oxzoid Parquet 1963](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet) (revisao 4b4fb3a, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`) → [extrator com verificacao de hash](../../tools/audit_norad_1963.py) → CSV fixado → analise exata em microssegundos → JSON arquivado por GitHub Actions. Nenhum ramo fornece aqui transcricao coeva independente. O [NASA Satellite Situation Report de 15/11/1963, p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) continua sendo documento primario **somente para o dia de decaimento** (08/11), nao para essas epocas ou um local de impacto. CelesTrak instrui o *formato* e nao atesta o acervo.

**Nao inferir** origem original de line1/line2, checksum de 45 pares, TEME historico, frame, sistema de rastreamento, precisao observacional, componente material 528 ou derivadas orbitais. O dominio nao vazio encontrado e de **representacao documental**, sem restricao numerica fisica adicional em Lean 4.35.0 ou no simulador; nao ha dominio dinamico admissivel novo. O conflito **RAAN 198,5261° versus 284,1520° permanece aberto**. Faltam os originais NORAD/AFSPC com epocas, metadados de frame, incerteza e procedencia, a identidade fisica S00528 e observacoes terminais independentes. Resultado relativo a Conde: **INDETERMINADO**.


## C241-T5 — integridade de colunas dos pares TLE literais (12/11/2026 UTC, 🐢)

**Questão:** uma linha com checksum correto pode ainda conter um campo fisicamente inválido, corrupto ou deslocado? **Sim:** o algoritmo de checksum soma dígitos e sinais `-` em quaisquer posições, sem verificar significado, calendário, separadores, faixas ou consistência entre as duas linhas. Por isso `checksum == PASS` isoladamente não é validação do vetor. A nova contraprova modifica uma RAAN para `284.1520°`, recalcula o checksum e ainda obtém linha sintaticamente válida: **o dígito não decide qual RAAN veio do NORAD**.

- Fonte numérica literal fixada: [espelho itau S00528](https://www.itau.magnetic-declination.com/satellite/?s=528), `research/tle_custody/mirror_528_1963-10-27.tle`, SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; somente **um** par, a época de 27/10, não os 45 originais.
- Especificação de representação utilizada: [CelesTrak, TLE format](https://celestrak.org/columns/v04n03/), **posterior a 1963**. Testa 69 colunas ASCII, prefixos 1/2, números de catálogo coincidentes, campos de designador/época com dia válido, separadores e quantização decimal, inclinação/RAAN/excentricidade, movimento médio positivo e notação compacta de n-double-dot/BSTAR; preserva os tokens brutos, `epoch_utc`, unidades, checksum lido/calculado e SHA-256 de ambas as linhas no JSON.
- `tools/tle_literal_layout.py` **não** reconstitui linhas a partir de floats do Parquet. `validate_raw_tle`, usado no confronto dos espelhos, agora só admite par literal depois do gate de estrutura. `tests/test_tle_literal_layout.py` cria **somente mutações sintéticas com checksums recalculados** e as rejeita quando o conteúdo é inconsistente; diferenças de RAAN válidas são preservadas como conflito de origem.
- Reproduzir: `python -m unittest discover -s tests -p 'test_*.py' -v` e `python tools/tle_literal_layout.py --pair research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/secondary_528_literal_fields.json`. O workflow de custódia arquiva esse JSON sob o SHA do **HEAD** da PR. O JSON do caso literal registra 528, `63300.61129783`, `1963-10-27T14:40:16.132512Z`, RAAN `198.5261°`, checksum `0/4`, conflito `UNRESOLVED` e `NOT_VERIFIED` para origem NORAD/frame.
- Dependência: espelho itau e Parquet oxzoid podem remontar ao mesmo sistema Space-Track. A especificação CelesTrak é regra de formato, não sensor independente. **Documentos primários ainda ausentes:** line1/line2 originais para cada época de 527/528/529, seus checksums históricos, indicação de quadro e metadados do rastreamento, documento de peça S00528, fonte de `284.1520°`. Nenhum desses itens foi inferido do teste. NASA C197 registra somente 08/11 como dia de decaimento. Sem restrição física nova, domínio orbital Lean, horário ou local de reentrada.

**Status C241-T5:** auditoria de representação/testes de falha fechada; **não** validação histórica ou inferência dinâmica. CI do HEAD final deve ser citado separadamente após conclusão no GitHub Actions.


## C241-T6 — prova de esquema e integridade das casas decimais

O [viewer do espelho oxzoid](https://huggingface.co/datasets/oxzoid/space-track-tle-history) publica inclination, raan, eccentricity, arg_perigee e mean_anomaly em **float32**, mas mean_motion, mean_motion_dot e bstar em **float64**. A época é timestamp[us, tz=UTC]. A auditoria distingue os dois formatos. Em particular, não se deve alegar perda de dígitos do movimento médio por hipotética conversão a float32 que **não ocorreu no corpus**.

A ferramenta [tle_numeric_precision_audit.py](../../tools/tle_numeric_precision_audit.py) recebe o Parquet 1963 já baixado e valida seu SHA-256 fixo c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. Exige tipos exatos via PyArrow, avalia ida/volta de cada campo na grade decimal TLE (4 casas para quatro ângulos, 7 para excentricidade, 8 para movimento médio float64) e testa os valores decimais adjacentes para detectar representações colidentes. Gera JSON com source_row, época, tipo, status, resíduos e totais. Gate do CI falha com campo inconsistente, mas preserva saída para perícia. Os testes são sintéticos; o espelho não vira observação primária por passar no teste.

Reprodução no workflow após o extrator: python tools/tle_numeric_precision_audit.py --parquet /tmp/tle_1963.parquet --output /tmp/norad-1963-audit/tle_numeric_precision_report.json.

**Restrição epistemológica:** valores orbitais numericamente reversíveis não são os TLEs literais originais. O Parquet não preserva line1/line2, os dígitos de checksum, os metadados de coleta de 1963, número de conjunto, tipo de efeméride, número de revolução, frame histórico certificado, nem a identificação física da peça. Nenhum TLE foi fabricado. RAAN 198,5261° versus 284,1520° continua sem proveniência resolvida; nem reentrada geográfica nem impacto em Conde foram demonstrados.


**Resultado empírico da C241-T6 (fonte fixada, HEAD 45c608a3db0f30c3ba1cf8ee5261085508e07a64):** [custódia #43150035578](https://github.com/franklinbaldo/conde-incident/actions/runs/43150035578) **SUCCESS**, 66/66 testes, [artefato #13912379474](https://github.com/franklinbaldo/conde-incident/actions/runs/43150035578/artifacts/13912379474) com digest SHA-256 717d8b9770e387d23ded6ec563c864f89826762e6e638b52a06f0e0f07e6fdf9; [scientific checks #43150035546](https://github.com/franklinbaldo/conde-incident/actions/runs/43150035546) **SUCCESS no mesmo HEAD**. Testou **123 registros, 738/738 projeções de campos orbitais** compatíveis com grade decimal TLE e sem colisões com vizinhos imediatos (por campo: 123/123). **Conclusão positiva limitada:** na precisão publicada do espelho, os seis *valores numéricos* não demonstram perda de dígitos TLE. **Conclusão negativa decisiva:** ausência dos bytes de line1/line2 e de metadados históricos impossibilita autenticar/reproduzir os 45 pares/checksums originais. O conflito de RAAN continua aberto; o arquivo não fornece sensor, frame, erro ou impacto. Um novo commit documental ou de código após esse SHA exige CI novamente.


## C241-T7: Cronologia circular de RAAN, sem simular a órbita (12/11/2026)

Esta auditoria separa **aritmética entre registros** de uma inferência dinâmica. O script [`tools/raan_epoch_continuity_audit.py`](../../tools/raan_epoch_continuity_audit.py) lê somente o CSV fixado das 45 épocas NORAD 528 (SHA-256 `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`). Requer origem de 1963 em UTC, identificação por linha física `source_row` sem repetição, ordem estrita de épocas e ângulo RAAN no intervalo [0,360). Calcula diferenças circulares assinadas de menor arco e tempo transcorrido em microssegundos inteiros. Um arco exatamente de 180° tem dois sinais equivalentes e provoca falha explícita em vez de escolher direção. Expõe **todas** as diferenças entre registros consecutivos, lacunas de amostragem maiores que 72h, o maior intervalo, e os pontos de cobertura próximos da data de decaimento da NASA. Não interpola amostras, ajusta J2, transforma TEME/equinócio, calcula forças ou gera trajetórias.

**Correção de representação horária:** o registro legado sem cadeia NORAD, `63300.61111111`, equivale literalmente a **1963-10-27 14:39:59.999904 UTC**, ao passo que `63300.61129783` no par secundário pinado equivale a **14:40:16.132512 UTC**. A separação é **16,132608 segundos**, bem maior que a meia unidade temporal TLE de 432 microssegundos. Mesmo a escrita coloquial `14:40:00` do legado já é um arredondamento de 96 microssegundos. As RAANs **284,1520° e 198,5261°** diferem 85,6259°; nenhuma atribuição instrumental, transformação de frame ou causa dessa divergência foi comprovada. Uma RAAN encontrada em outra data não é valor da época-alvo.

**O salto até novembro é ausência de cobertura, não reentrada medida:** o boletim NASA de 15/11/1963, p. impressa 8 ([NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)) registra apenas *8 NOV 63* para 1963-003B. O script reporta a diferença entre a última amostra 528 do espelho e **o começo/fim do dia civil de 08/11**. Não escolhe 23:59 ou qualquer outro horário terminal; os dois limites civis não representam barras de erro físicas nem demonstram um local de queda. A origem observacional completa dos 45 pares, checksum individual, sensor, frame teórico e a identidade de engenharia de S00528 seguem **NOT_RECOVERED**. O ramo oxzoid e o par itau podem compartilhar a mesma extração de Space-Track.

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/raan_epoch_continuity_audit.py \
  --csv /tmp/tle-audit/norad_528_epochs_1963.csv \
  --pair research/tle_custody/mirror_528_1963-10-27.tle \
  --output /tmp/tle-audit/raan_epoch_continuity.json
```

O arquivo CSV é produzido previamente pela extração Parquet de SHA fixado no mesmo workflow. O JSON de saída conserva `source_row`, UTC e deltas para revisão. **Os quocientes \u0394RAAN/\u0394tempo do relatório são números descritivos sobre registros médios/catálogo** e não um fit de precessão: intervalos com lacunas, diferenças de frame, ajustes de parâmetros e incerteza instrumental inexistente não podem virar limite físico. Assim, a sequência ciência primária → restrição Lean → domínio físico reduzido → simulação → holdout permanece **bloqueada** nesse ponto. Nenhuma conclusão sobre impacto em Conde.


### C241-T7: saída observada no corpus pinado, não cenário (12/11/2026)

Em [custódia #43155873680](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680), HEAD `f3cb5d056af51135959acb88b6813b3018b210d5`: **78/78 testes PASS**, hash fixado do Parquet verificado, **45 amostras, 44 intervalos**. São **32 intervalos acima de 72h** e apenas **3 até 24h** no conjunto de amostras do 528. A maior lacuna de registro é **23,53529262 dias**, de 06/02/1963 05:33:01.197504Z (linha 2978) a 01/03/1963 18:23:50.479872Z (linha 2979). A última amostra 528 permanece de 27/10/1963 14:40:16.132512Z. Entre essa amostra e os limites do dia civil 08/11/1963 decorrem **11,38870217 a 12,38870217 dias**. Essas distâncias temporais mostram a falta de observação terminal no arquivo, **não** intervalo calculado de incerteza de reentrada.

O comparador registra `RAAN_legacy=284,1520°` e `RAAN_literal_mirror=198,5261°`, distância circular **85,6259°**, com **16.132.608 microssegundos** entre épocas textuais. A amostra mais próxima pelo ângulo permanece de **12/08/1963** (linha 2998, RAAN 284,331085°, a 0,179085°), e não na época de 27/10. Isso não resolve a identidade física do 528 nem o frame ou a genealogia do número legado. [Scientific checks #43155873831](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873831) também passou no SHA testado. [Artefato auditável #13915508369](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680/artifacts/13915508369) contém o novo `raan_epoch_continuity.json`; SHA-256 do ZIP `11415cc6e4aef003158f1bab49f68abeede687fc5e417c5994899502d5a670c7`. Atualizações posteriores requerem novo CI no HEAD final.


## C241-T8: NORAD 527/528/529 e o limite da identidade fisica

**Pergunta:** os tres objetos numericamente rastreados podem ser ligados a
identificadores COSPAR e rotulos de catalogo sem confundir rotulo secundario
com reconhecimento material de destroco? Sim, como verificacao de **chaves**,
nao como autenticacao de observacoes ou de objeto fisico.

Fontes consultadas em 12/11/2026, transcritas com URLs e data em
[catalog_identity_527_529_2026-11-12.json](catalog_identity_527_529_2026-11-12.json):

| SATCAT | COSPAR | Nome em catalogo secundario | Tipo atribuido pelo catalogo |
|---|---|---|---|
| 527 | 1963-003A | FTV 2313 | payload |
| 528 | 1963-003B | FTV 2313 DEB | satellite debris |
| 529 | 1963-003C | FTV 2313 DEB | satellite debris |

As tres fichas de [Itau (527)](https://www.itau.magnetic-declination.com/satellite/?s=527),
[Itau (528)](https://www.itau.magnetic-declination.com/satellite/?s=528) e
[Itau (529)](https://www.itau.magnetic-declination.com/satellite/?s=529)
apresentam mesmo dia de lancamento 16/01/1963. Os agregadores
[KeepTrack 528](https://keeptrack.space/satellite/00528) e
[529](https://keeptrack.space/satellite/00529) repetem nome, tipo e COSPAR,
mas nao constituem instrumento de radar ou reconstrucoes independentes.
O boletim contemporaneo [NASA 15/11/1963, p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
ja conferido em C197 informa o dia 08/11 para 1963 3B, sem horario
ou local. Nesta rodada, o fac-simile NASA nao foi reinspecionado.

O novo [auditor](../../tools/tle_identity_lineage_audit.py)
usa o CSV de NORAD 527–529 produzido a partir do
[Parquet oxzoid fixado](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet)
(revisao 4b4fb3a, SHA256
`c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`,
CSV SHA256
`3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`)
e compara os campos textuais de designador de todas as 123 linhas aos
IDs esperados, preservando `source_row`, grafia exata e duplicatas.
Valida tambem o unico par literal preservado de 528 (SHA256
`18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`),
conferindo o fragmento de linha1 `63003  B` por meio de
`tle_literal_layout.py` e seus checksums. O programa gera
`tle_catalog_identity_lineage.json`, com caminhos, SHA, contagem e
rotulos de origem. Testes sintéticos de contraprova impedem troca A/B/C,
contagem errada, source_row repetida e promocao de classe de catalogo
a prova primaria.

Reproducao, apos extrair o Parquet pelo workflow que confere SHA:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/tle_identity_lineage_audit.py \
  --csv /tmp/tle-audit/norad_527_528_529_1963_numeric.csv \
  --ledger research/tle_custody/catalog_identity_527_529_2026-11-12.json \
  --pair research/tle_custody/mirror_528_1963-10-27.tle \
  --output /tmp/tle-audit/tle_catalog_identity_lineage.json
```

**Interpretacao crucial:** *FTV 2313 DEB* e um nome de catalogo, NAO uma
folha de engenharia da peca nem prova de massa, dimensoes, material,
anteparo, estagio ou componente desprendido. A ficha 527 ('payload')
nao permite atribuir sua geometria, ano de reentrada ou outro metadado
fisico ao 528. Nem NASA/Itau/KeepTrack sao tres sensores independentes.
**Resultado negativo**: ate aqui nao foi localizada uma folha tecnica
NRO/NORAD que relacione S00528 a uma peca concreta, seu serial, massa,
mecanismo de separacao ou propriedades balisticas. Sem tal documento e
sem 45 TLEs instrumentais/frame/incertezas, nao ha restricao dinamica
nova admissivel em Lean 4.35.0. O conflito RAAN e a localizacao de
reentrada permanecem **NAO RESOLVIDOS**; Conde **INDETERMINADO**.


## C241-T9: n-dot/2 e BSTAR, duas perguntas de escala diferentes

O formato TLE preserva na linha 1 a **metade da primeira derivada do movimento médio** (n-dot/2, em rev/dia²), a sexta parte da segunda derivada e o termo BSTAR. A [especificação CelesTrak](https://celestrak.org/columns/v04n03/) define a posição das colunas. A [página de esquema do espelho oxzoid](https://huggingface.co/datasets/oxzoid/space-track-tle-history) chama o campo Parquet de mean_motion_dot e o descreve como derivada. Sem os bytes históricos originais de exportação, **não assumir automaticamente fator 1 ou 2** entre a coluna numérica e o campo impresso.

O novo **tools/tle_drag_term_lineage_audit.py** verifica índice original, época UTC e hash do CSV; resume a distribuição de mean_motion_dot e BSTAR para 527/528/529; compara o registro 528 da mesma época com o **único** par TLE literal secundário; testa separadamente valor impresso n-dot/2 e dobro n-dot, com tolerâncias exclusivamente de serialização. Compara BSTAR de modo independente, e documenta a **ausência da segunda derivada** no esquema Parquet. Não cria TLE sintéticos. Não infere massa/área/densidade atmosférica, arrasto físico ou posição terminal a partir de um valor zero.

Reproduzir após gerar o CSV hash-bound pelo workflow:

    python tools/tle_drag_term_lineage_audit.py --csv /tmp/norad-1963-audit/norad_527_528_529_1963_numeric.csv --pair research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/norad-1963-audit/tle_line1_drag_terms.json

A fonte numérica é oxzoid 1963 Parquet rev 4b4fb3a SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**, CSV derivado SHA-256 **3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231**, par Itau 528 SHA-256 **18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd**. O CSV é secundário e pode compartilhar exatamente a fonte do par literal: coincidência entre eles **não significa duas observações de radar independentes**. Sem 45 pares NORAD primários, quadro, sensor, erros e identidade material de 528, nenhuma restrição física foi admitida em Lean 4.35.0. RAAN legada 284,1520° continua sem autenticação; resultado Conde **indeterminado**.


**Execução observada C241-T9 no HEAD 30533c1b713b459811c3266b078977b302f94f33:** [custódia #43170566947](https://github.com/franklinbaldo/conde-incident/actions/runs/43170566947) **SUCCESS**, checkout verificou audited_source_head, **103/103 testes**, auditoria do Parquet no hash pinado, [artefato #13922410859](https://github.com/franklinbaldo/conde-incident/actions/runs/43170566947/artifacts/13922410859), ZIP sha256 ae1bc2904005d2d7447ec43fdfe0f2d468f62c10380f9732a09eadbdaff6e6ab; [scientific checks #43170567112](https://github.com/franklinbaldo/conde-incident/actions/runs/43170567112) SUCCESS no mesmo HEAD. Resultado **n-dot 528 na mesma época = 0,00686563**, idêntico ao **campo TLE codificado como metade da derivada**. A hipótese *de que a coluna do espelho traz sempre a derivada integral/dobrada* **não é compatível com esse par**; o espelho usa pelo menos nesse registro o valor literalmente codificado, não o dobro de 0,01373126. Isto só audita serialização de uma fonte secundária, **não prova a derivada física**. Nos **123 registros**, **BSTAR é zero nos 123/123**: 527 21/21, 528 45/45, 529 57/57. Por outro lado, **mean_motion_dot é não zero em 123/123**; intervalos publicados: 527 0,00000344–0,00005916; 528 0,0000039–0,00913699; 529 0,00000305–0,04059205 (unidade do campo, **não** estimativa física de aceleração). A linha literal 528 também tem BSTAR zero. A uniformidade BSTAR=0 demanda investigação de formato/origem e **não** autoriza concluir arrasto físico zero. NASA 08/11 continua data civil, não localização. Não altera conflito RAAN nem libera Lean físico. A memória final/novos commits documentais exigem novo CI no SHA final.


### C241-T10 — controle da explicação por defasagem de 16 segundos (12/11/2026)

Executar no checkout da PR #14, após a extração pinada:

```sh
python tools/tle_raan_epoch_offset_j2_audit.py \
  --csv /tmp/tle-audit/norad_528_epochs_1963.csv \
  --pair research/tle_custody/mirror_528_1963-10-27.tle \
  --output /tmp/tle-audit/raan_epoch_offset_j2_conditional.json
python -m unittest tests/test_tle_raan_epoch_offset_j2_audit.py -v
```

A ferramenta exige o SHA-256 `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e` do CSV 528, as 45 épocas, uma amostra na época do par literal, compatibilidade de RAAN com o par espelhado, SHA `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd` e checksums das duas linhas. Armazena fontes, SHA, índices, números e status explícitos, sem recriar TLE primário. A trilha detalhada está em [C241-T10 na matriz](../evidence_matrix_C001-C238_2026-11-11.md).

**Contraprova restringida, não uma órbita identificada:** o literal legado de época 27/10/1963 14:39:59,999904Z difere do secundário 14:40:16,132512Z em apenas 16,132608 s, mas suas RAANs estão separadas por 85,6259°. Se ambos fossem descrições do *mesmo nó no mesmo frame*, regidas neste intervalo apenas pela aproximação J2 secular de primeira ordem, o desvio estimado seria ~0,0002191°, e não 85,6259°. A hipótese **defasagem temporal de 16 s isoladamente** não passa nesse modelo. A origem do 284,1520° continua **não recuperada**; os dados não justificam equiparar aproximação J2 com a física histórica do satélite, nem usar isso como prova Lean de local/hora de reentrada. O relatório é condicional aos parâmetros do modelo e conserva as hipóteses rivais.

**Gates de origem:** falta NORAD primário (45 pares, sensores, erro, frame), a peça física 528 identificada por documentação de engenharia e posição/hora terminal; sem observação primária não há domínio físico reduzido e não vazio a entregar ao simulador/Lean. A NASA só atesta dia de decaimento em C197. CI deve ser reexecutado no HEAD final da PR; resultado só confirmado por run real.


## C241-T11: secantes de n e teste negativo de promoção de n-dot a medição

A fonte de entrada é EXCLUSIVAMENTE o CSV derivado de [oxzoid Parquet 1963 rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet) SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**, com CSV de 527/528/529 SHA-256 **3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231**. O novo [auditor](../../tools/tle_mean_motion_secant_audit.py) preserva source_row, IDs, designador, valores decimais e carimbo UTC (grade 864 µs); exige 21/45/57 registros e 20/45/54 épocas distintas; conserva índices de duplicatas idênticas e recusa duplicata com estado contraditório. Calcula Δn/Δt para pares *adjacentes* de cada objeto, não uma trajetória interpolada. Todos os intervalos, inclusive lacunas grandes, ficam no JSON; resumos separados para ≤24h/≤72h evitam transformar grande lacuna em taxa local.

O campo *mean_motion_dot* do Parquet coincide em **uma** época do 528 com a metade da derivada impressa na linha TLE secundária (C241-T9). **Se**, e somente se, essa escala valer em todas as épocas e o campo variar suavemente, um controle linear ingênuo no intervalo é Δn previsto = Δdias × (dot_codificado_antes + dot_codificado_depois). O programa calcula o residual rev/dia e informa intervalos com os dois dot positivos mas Δn negativo. **Isto é um teste de consistência descritivo entre parâmetros ajustados em épocas distintas**, nunca medida física independente de drag, ausência de força, predição, erro calibrado ou holdout de dinâmica. Nenhuma premissa Lean 4.35.0 sobre órbita histórica é promovida.

    python tools/tle_mean_motion_secant_audit.py --csv /tmp/tle-audit/norad_527_528_529_1963_numeric.csv --output /tmp/tle-audit/mean_motion_secants_c241_t11.json
    python -m unittest discover -s tests -p 'test_*.py' -v

Referências de proveniência e independência: [formato TLE CelesTrak](https://celestrak.org/columns/v04n03/), [Itau 528](https://www.itau.magnetic-declination.com/satellite/?s=528) (mesma possível linhagem numérica), [NASA 15/11/1963 p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) (fonte primária apenas da **data civil** 08/11; não reaberta nesta rodada). Faltam os 45 pares instrumentais, sensores, erro, frame e identidade física S00528 documentada pela NRO; não há observação terminal em novembro no espelho. RAAN **284,1520° versus 198,5261°** permanece sem solução primária, Conde **indeterminado**. A matriz contém C241-T11 e os resultados medidos devem ser confirmados no CI do **HEAD final** antes de se afirmarem contagens novas.
