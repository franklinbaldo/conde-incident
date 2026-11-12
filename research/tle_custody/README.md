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
