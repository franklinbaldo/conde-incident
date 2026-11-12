# 🦡 Controle negativo: baseline quadrático versus curvatura conjunta, holdout 529

**Status (11/11/2026):** protocolo *pré-registrado no código*, ainda não uma validação orbital. Este experimento não infere longitude, impacto, probabilidade, arrasto real, parentesco dinâmico nem causa do relato de Conde.

## Evidência, custódia e dependência

A matriz cumulativa da [PR científica #1](https://github.com/franklinbaldo/conde-incident/pull/1) (C20, C25, C179–C185, C197, C238) distingue a data de decaimento do componente 1963-003B do lugar da queda. O original coevo [NASA *Satellite Situation Report*, 15/11/1963, p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) somente registra **08/11/1963**, sem hora e sem localização.

O conjunto numérico do experimento procede do [Parquet oxzoid/space-track-tle-history, 1963, commit 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), **espelho secundário** que declara origem Space-Track e tem SHA-256 fixado `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. O extrator e auditor `tools/audit_norad_1963.py` pertencem à [PR de custódia #14](https://github.com/franklinbaldo/conde-incident/pull/14). O relatório `audit.json` e seu CSV devem ser produzidos na **mesma execução**, após baixar e comparar os bytes originais por SHA-256. O leitor Texugo **reabre independentemente** o Parquet, confere SHA-1/SHA-256 e confronta todas as tuplas `(source_row, norad_id, epoch, mean_motion)` com o CSV. Apenas coincidir o JSON de auditoria não basta; um CSV modificado, truncado ou duplicado deve falhar. A ausência de `line1/line2`, proveniência individual, frame e instrumentos originais mantém a verificação primária **NOT_RUN**.

As observações 527/528/529 vêm da **mesma linhagem** de catálogo; não são três medições institucionalmente independentes. O ajuste de uma curvatura numérica conjunta não deve ser chamado de triangulação física. Não há priors, posterior bayesiana, localização nem identificação de objeto por esta rotina.

## Pergunta e modelos pré-definidos

A pergunta mínima e falsificável é se uma **curvatura compartilhada** do movimento médio (rev/dia) estimada nos satélites 527 e 528 melhora a extrapolação temporal do 529 sobre um baseline que ignora os companheiros.

Cortes UTC inclusivos de treino: **31/08, 28/09, 11/10 e 21/10/1963**, antes de ver o teste, equivalentes aos cortes da investigação anterior C20. Em cada corte:

1. **Baseline:** regressão quadrática de movimento médio `n529(t)=a+b*x+c*x²`, usando **somente épocas 529 até 23:59:59 UTC do corte**.
2. **Controle de transferência (não é modelo orbital acoplado):** regressões quadráticas separadas em 527 e 528, somente com épocas anteriores ao corte. Tomar a **média igualitária** dos dois coeficientes de curvatura, não dar maior peso ao objeto com mais registros. Com essa curvatura fixada, ajustar **apenas intercepto e inclinação** próprios do 529 anterior ao corte.
3. **Controle negativo intencional:** repetir com sinal invertido da curvatura compartilhada. A operação não tem interpretação física, serve para perceber que qualquer transferência indiscriminada pode ganhar ou perder.
4. **Teste temporal:** previsões confrontadas exclusivamente com épocas 529 **posteriores** ao corte. Nenhuma época futura de 527/528/529 entra no ajuste. Métrica primária RMSE em revoluções/dia, número de épocas e horizontes registrados, inclusive ganhos, empates, pioras e `NOT_RUN`.

Por definição o 529 **não é um objeto inteiro completamente oculto**: seus valores pré-corte ajustam posição inicial no espaço de movimentos médios. O holdout cego é **a sequência futura do 529**, não um teste leave-one-satellite-out estrito. Não se deve anunciar a comparação de séries numéricas como reconstrução do estado vetorial osculador.

Não há busca de parâmetros pelo resultado dos cortes, significância estatística, probabilidades nem seleção do melhor corte após olhar o futuro. Os mesmos objetos, a mesma fonte e cortes temporais sobrepostos restringem qualquer inferência de generalização. Um resultado `JOINT_BETTER` isolado **não comprova** causa física nem informa reentrada do 528; `BASELINE_BETTER` é uma falsificação útil da alegação universal de superioridade do compartilhamento.

## Reproduzir na PR, sem download de produção

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pip install pyarrow==21.0.0
python tools/audit_norad_1963.py --download \
  --parquet /tmp/tle_1963.parquet --output /tmp/conde-source
python tools/texugo_holdout_529.py \
  --parquet /tmp/tle_1963.parquet \
  --csv /tmp/conde-source/norad_527_528_529_1963_numeric.csv \
  --audit /tmp/conde-source/audit.json \
  --output /tmp/conde-holdout-529.json
```

No GitHub Actions `.github/workflows/texugo-holdout.yml` executa o mesmo procedimento no **HEAD exato** da PR e publica CSV, `audit.json` e resultados JSON como artefatos. O CI só pode certificar execução reproduzível, integridade do espelho e testes; não deve reprovar `BASELINE_BETTER`. Um bloqueio de rede de HF ou ausência de registro produz falha/NOT_RUN, **não** paridade histórica.

## Resultado do primeiro replay real (HEAD 44c09b4; 11/11/2026)

O [GitHub Actions #43100111352](https://github.com/franklinbaldo/conde-incident/actions/runs/43100111352) terminou **SUCCESS** no SHA `44c09b454a25885416f1b295a02d55fe3d80efac`, com instalação `pyarrow==21.0.0`, auditoria SHA-256 do Parquet espelhado e arquivo JSON arquivado como [artefato #13892185614](https://github.com/franklinbaldo/conde-incident/actions/runs/43100111352/artifacts/13892185614). A auditoria de custódia [#43100111367](https://github.com/franklinbaldo/conde-incident/actions/runs/43100111367) e o CI científico [#43100111436](https://github.com/franklinbaldo/conde-incident/actions/runs/43100111436) também passaram no mesmo SHA. A tabela abaixo é transcrição de valores numéricos do **log do workflow**, não de medições primárias. Os holdouts se sobrepõem e não são réplicas independentes.

| Corte UTC | Amostras 529 futuras | RMSE 529 quadrático (rev/dia) | RMSE transferido (rev/dia) | Vencedor descritivo |
|---|---:|---:|---:|---|
| 31/08 | 28 | 0.210299289 | 0.211762185 | Quadrático |
| 28/09 | 24 | 0.216540216 | 0.214537239 | Transferência |
| 11/10 | 21 | 0.223016327 | 0.219896277 | Transferência |
| 21/10 | 20 | 0.223236815 | 0.215116674 | Transferência |

**Resultado negativo real:** em 31/08, a transferência **piorou** o RMSE do 529 em cerca de `0.001462895` rev/dia (não é o resultado sintético de 2,03084). Nos demais três cortes a redução vai de `0.002002977` a `0.008120140` rev/dia, apenas dentro do mesmo catálogo secundário. Não há teste de significância, separação de linhagens, propagação vetorial ou prova de maior acurácia orbital. A contraprova de CSV falso foi descoberta após esse replay; a nova validação por comparação Parquet↔CSV precisa de GitHub Actions no **novo HEAD**, sem herdar o PASS anterior.

## Emenda de ablação pós-resultado: doadores isolados e baseline linear (11/11/2026)

**Status do desenho: POST_HOC.** Esta emenda foi introduzida **depois** de observar os quatro RMSE históricos acima; não é pré-registro nem uma nova amostra independente. Mantém exatamente os quatro cortes originais e a métrica original, sem escolher corte, doador ou hiperparâmetro para maximizar desempenho.

Para cada corte e com **os mesmos dados de treinamento anteriores ao corte**, o script calcula também: (a) curvatura transferida só do 527; (b) curvatura transferida só do 528; (c) baseline **linear** treinado só no 529; (d) controle de sinal invertido já existente. Todos são avaliados no **mesmo futuro oculto do 529**, sem refit no teste. O JSON inclui cada RMSE e três indicadores descritivos: ganho conjunto sobre ambos os doadores isolados, sobre a regressão linear e sobre a curvatura invertida. **Não há nova barreira de CI por vencer esses controles.**

Esta ablação discrimina uma hipótese particularmente fraca: a média 527/528 pode reduzir RMSE perante o quadrático próprio do 529 simplesmente por regularização acidental, enquanto um único doador ou um modelo mais simples já faria melhor. Um doador isolado ganhar **não** valida ligação física nem independência de fonte. Os testes sintéticos agora incluem explicitamente um doador correto e outro incorreto, um 529 exatamente linear e alteração de todos os valores futuros sem mudar nenhum coeficiente ajustado.

### Releitura independente do artefato já aprovado, antes do novo CI

Recuperei o [ZIP histórico do workflow anterior, artefato #13896035257](https://github.com/franklinbaldo/conde-incident/actions/runs/43109127688/artifacts/13896035257), validado no HEAD anterior `36b6064`. Sua saída contém **123 linhas brutas = 119 épocas distintas** (20/45/54 para 527/528/529); a releitura descartou somente repetições idênticas de época, exatamente como faz `parse_csv`. Com regressão NumPy independente, os RMSE originais do quadrático e da média coincidiram até erro absoluto menor que `1.1e-13` rev/dia. Na mesma amostra secundária, os controles adicionais renderam:

| Corte | Quadrático 529 | Média 527+528 | 527 isolado | 528 isolado | Linear 529 |
|---|---:|---:|---:|---:|---:|
| 31/08 | 0,210299289 | 0,211762185 | 0,235461981 | **0,188806986** | 0,244950058 |
| 28/09 | 0,216540216 | 0,214537239 | 0,245414540 | **0,184754193** | 0,253475516 |
| 11/10 | 0,223016327 | 0,219896277 | 0,257283361 | **0,183954136** | 0,262876770 |
| 21/10 | 0,223236815 | 0,215116674 | 0,260942304 | **0,171610907** | 0,265515032 |

RMSE em rev/dia, sobre o mesmo futuro temporal do 529. A **média de doadores perdeu para o 528 isolado em todos os quatro cortes**, inclusive naqueles em que superou o baseline quadrático. Portanto, os três ganhos da média perante o quadrático não identificam uma vantagem da **combinação** dos dois doadores: um único doador já fornece previsões descritivas melhores. O 527 isolado ficou pior que a média e que o quadrático em todos os cortes.

Esses cálculos são uma **reprodução local independente** dos números do artefato anterior, não os resultados do novo workflow: **CI do HEAD desta emenda ainda NOT_RUN/não confirmado**, e esta análise foi concebida pós-hoc sobre a mesma série. Comparações de janelas correlacionadas não permitem inferir relevância estatística, causalidade física, escolha válida futura do 528 nem localização de reentrada. O controle com sinal invertido também foi calculado, mas não selecionado como concorrente preditivo.

**Fonte e custódia inalteradas:** Parquet oxzoid commit `4b4fb3a`, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; NASA 15/11/1963 p.8 para **dia**, não lugar. A ablação não acrescenta observações de radar, não resolve RAAN e não pode produzir probabilidades. Comparações históricas adicionais **NOT_RUN até o novo workflow no HEAD da emenda**.

## Controles negativos executáveis

`tests/test_texugo_holdout_529.py` contém dados **100% artificiais**, em dois sentidos: ganho da transferência quando há curvatura realmente compartilhada e treino escasso/perturbado; piora quando a curvatura do 529 diverge; teste anti-vazamento alterando apenas observações pós-corte (coeficientes devem ser invariantes); rejeição de fonte/hash falsos, duplicata conflitante e `NOT_RUN` quando não há amostras. Estes testes provam propriedades do procedimento, **não** dados de 1963.

**Próximo experimento discriminante:** só após recuperar observações TLE primárias completas, com época, frame e proveniência individual, confrontar estados dinâmicos verdadeiramente propagados (e não apenas `n(t)`) sobre janelas de validação independentes, controle SGP4 calibrado e holdout físico 529; comparar o ganho nos resíduos angulares e ao longo da órbita. O conflito RAAN 198,5261°/284,1520° permanece intacto.

Nenhuma página de blog, arquivo histórico ou contato externo foi alterado.


## Emenda C243-T2: seleção cronológica interna contra o oráculo retrospectivo (11/11/2026)

**Motivo falsificável:** a vitória descritiva do 528 isolado nos quatro cortes foi descoberta olhando o mesmo futuro do 529. Escolher 528 por isso seria *vazamento de rótulo do holdout* (seleção por oráculo), não previsão. Um controle adicional `tools/texugo_nested_529.py` escolhe entre quadrático 529, linha 529, média 527+528 e doadores isolados usando **exclusivamente o último quarto das observações 529 pré-corte** como validação cronológica interna; ajusta cada concorrente usando apenas épocas anteriores a essa janela interna, incluindo as dos doadores. Em seguida congela a escolha, reajusta o modelo escolhido em todos os dados pré-corte permitidos e calcula erro apenas no futuro 529. Preserva os **mesmos quatro cortes** anteriores. A janela interna e o holdout externo não se misturam, mas os quatro experimentos externos permanecem temporalmente correlacionados.

O relatório arquiva separadamente erros internos de todos os candidatos, modelo realmente selecionado sem futuro, RMSE externo de todos os candidatos, diferença contra baseline quadrático e a mínima RMSE externa escolhida **com conhecimento do futuro**, explicitamente rotulada como **oráculo não admissível**. Nenhuma regra obriga melhora; insuficiência de registros produz `NOT_RUN`, inclusive resultado negativo. O protocolo foi criado **depois de examinar C243-T1** e continua retrospectivo e exploratório, sem pré-registro externo, prova causal, teste de satélite inteiro oculto, confiança estatística ou previsão orbital.

**Reprodução:** executar o auditor de Parquet SHA-pinado de C240, depois `python tools/texugo_nested_529.py --parquet /tmp/tle_1963.parquet --csv /tmp/source/norad_527_528_529_1963_numeric.csv --audit /tmp/source/audit.json --output /tmp/nested_529.json` e `python -m unittest discover -s tests -p 'test_texugo_nested_529.py' -v`. O workflow `texugo-holdout.yml` no HEAD da PR preserva também `nested_529.json`. Referência numérica: [Parquet oxzoid 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` (espelho secundário, não sensores independentes). O registro de época NASA [15/11/1963, p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) só estabelece o dia do decaimento 1963-003B, não local nem hora.

**Estado antes do CI deste commit:** controles sintéticos propostos; avaliação numérica histórica e aprovação no novo HEAD **NOT_RUN** até execução do workflow. O resultado pode contrariar tanto a vitória retrospectiva do 528 quanto a média de doadores; reportar `NOT_RUN` caso os dados não sustentem a divisão interna. Sem prova Lean de posição admissível, sem dados primários instrumentais e sem resolução RAAN não existe inferência sobre Conde.
