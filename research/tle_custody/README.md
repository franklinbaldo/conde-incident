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

O extrator agora faz **comparação dos dados, não somente de checksums**. Lê o par literal 528 de 27/10 já preservado e validado, interpreta o campo de dia e fração com `Decimal` exato, busca por **época dentro de 1 segundo** as linhas 528 do Parquet original com SHA fixado, e confronta independentemente inclinação, RAAN, excentricidade, argumento de perigeu, anomalia média e movimento médio. As tolerâncias explicitadas no código só admitem arredondamento float32 do espelho; não são tolerâncias orbitais nem licença para escolher uma órbita. Comparar dois espelhos da mesma cadeia NORAD não constitui duas observações físicas.

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
