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

## Emenda C243-T3: influência de uma época, sem replicação independente (11/11/2026)

**Pergunta discriminante, proposta DEPOIS dos resultados C243-T1/T2:** a vitória do 528 isolado e a própria escolha cronológica interna continuam quando se suprime **uma única época de treino**? O novo [controle de influência](../tools/texugo_influence_529.py) reexecuta o *pipeline inteiro* de seleção interna C243-T2 e a ablação quadrático/média/528 C243-T1, uma vez para cada época pré-corte de 527, 528 e 529. O futuro do 529 fica **intacto e sempre fora do ajuste**. Remover 529 altera inclusive a composição da janela interna, deliberadamente: isto é fragilidade do procedimento completo, não estimativa de erro instrumental.

Registrar, para os quatro cortes originais, a escolha sem olhar o futuro, a mudança de escolha, as diferenças RMSE de conjunto e 528 contra o quadrático, alterações de sinal, todas as épocas excluídas e cada `NOT_RUN`. Não converter número ou fração de exclusões em *probabilidade* ou intervalo de confiança: observações e janelas são dependentes, o desenho é **POST_HOC** e não há observações instrumentais independentes. Tampouco há gate que exija melhoria. É ablação numérica de uma linhagem, não estado orbital físico, formalização Lean de destino ou simulação de reentrada.

**Proveniência:** [Parquet espelhado oxzoid, commit 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, passando pela validação linha a linha C243; registros 527/528/529 não são três sensores. Documento coevo independente [NASA 15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) refere-se **somente ao dia do decaimento** 1963-003B. RAAN conflituoso sem resolução, instrumentação e frame não verificados.

**Execução:** depois do extrator de custódia, `python tools/texugo_influence_529.py --parquet /tmp/tle_1963.parquet --csv /tmp/source/norad_527_528_529_1963_numeric.csv --audit /tmp/source/audit.json --output /tmp/influence_529.json`; `python -m unittest discover -s tests -p 'test_texugo_influence_529.py' -v`. `texugo-holdout.yml` executa e arquiva o JSON completo no GitHub Actions do HEAD. **Resultados históricos inicialmente NOT_RUN**, até confirmação do run; os testes artificiais não substituem o espelho nem os dados originais.


### Resultado verificado da emenda C243-T3 (12/11 UTC)

O [run #43131353609](https://github.com/franklinbaldo/conde-incident/actions/runs/43131353609), HEAD `145f501041319c6c5e75871b2c871d8cfa488799`, passou com 60 testes e reexecução do extrator SHA-fixado. [Artefato completo #13904923232](https://github.com/franklinbaldo/conde-incident/actions/runs/43131353609/artifacts/13904923232). [Custódia #43131353594](https://github.com/franklinbaldo/conde-incident/actions/runs/43131353594) e [Scientific checks #43131353634](https://github.com/franklinbaldo/conde-incident/actions/runs/43131353634) também PASS no SHA.

As quatro janelas geraram **72, 83, 91, 95 exclusões individuais de épocas pré-corte**, todas avaliadas (341 no total). Alterou-se a escolha cronológica interna em **2/72**, **5/83**, **4/91** e **0/95**, respectivamente, por remoção de uma época. O sinal da vantagem da **média de doadores** sobre o quadrático mudou em **2, 2, 0, 0** exclusões; o sinal da vantagem do **528 isolado** não mudou em nenhuma das 341. São contagens de ablações *dependentes*, não p-valores, distribuições ou probabilidades. A estabilidade da vantagem de 528 sob exclusão de **uma** época não mostra invariância a blocos temporais, viés compartilhado, modelos físicos ou mudança de linhagem, e não retroativamente valida a seleção pós-hoc de 528. O CSV vem de um único Parquet secundário; a ausência de TLE instrumental primário e o conflito RAAN permanecem, bem como a impossibilidade de inferir queda em Conde.


## Emenda C243-T4: ablação conjunta de blocos temporais, pós-hoc (12/11/2026 UTC)

**Status inicial dos dados históricos: NOT_RUN até execução no GitHub Actions do HEAD.** Depois de C243-T3 (341 exclusões de uma época), testar robustez contra dependência temporal removendo blocos inteiros de **14 e 28 dias**, com bordas fixas a partir de 1963-01-01 00:00 UTC. Para cada bloco, retiram-se simultaneamente todas as épocas **pré-corte** de 527, 528 e 529, sem remover qualquer futuro 529. O algoritmo refaz inteiramente a seleção interna cronológica C243-T2 e os RMSE do baseline quadrático, média conjunta e 528 isolado. Os quatro cortes antigos não mudam.

Os blocos de 14/28 dias, seu alinhamento e as comparações são escolhas analíticas **POST_HOC**, formuladas após observar os resultados anteriores. Cada exclusão, inclusive falta de dados marcada NOT_RUN, fica no JSON; não existe gate de vitória do conjunto. As duas escalas e janelas externas reutilizam as mesmas observações: **não** são observações independentes, bootstrap, intervalos de confiança ou probabilidades. O controle discrimina se a vantagem descritiva do 528 resiste a lacunas correlacionadas, mas não se suas forças/órbitas eram acopladas.

**Proveniência:** [Parquet secundário oxzoid, alegado espelho Space-Track 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09, auditado contra CSV por C243. Os objetos compartilham a mesma linhagem de catálogo. O [boletim NASA de 15/11/1963, p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) é fonte contemporânea apenas do **dia** de decaimento 1963-003B, sem posição, hora ou movimento médio. Ausência de TLE/radar original com época/frame e conflito RAAN 198°/284° seguem impedindo restrição empírica Lean e simulação física de reentrada confiável; qualquer conclusão sobre Conde é INDETERMINADA.

**Reproduzir após o auditor C240:**

    python tools/texugo_block_529.py --parquet /tmp/tle_1963.parquet --csv /tmp/source/norad_527_528_529_1963_numeric.csv --audit /tmp/source/audit.json --output /tmp/block_529.json
    python -m unittest discover -s tests -p 'test_texugo_block_529.py' -v

O workflow texugo-holdout.yml executa o mesmo script no HEAD da PR e arquiva block_529.json com cada exclusão e sinal. Até revalidação do HEAD, não reivindicar resultados históricos novos.

### Contraprova C243-T5: translação artificial das épocas dos doadores (12/11/2026 UTC)

**Pergunta anti-overclaim:** a curvatura emprestada do 527/528 mede de fato a sincronização, a posição relativa ou as forças comuns dos três objetos? O modelo C243 utiliza dos doadores somente o coeficiente quadrático de uma regressão de movimento médio. Essa grandeza é **invariante a translação constante do eixo temporal** quando a amostra pré-corte permanece a mesma. Portanto, mesmo um ajuste numérico bem-sucedido não contém informação suficiente para medir fase relativa, triangulação ou posição de reentrada.

O controle translation_placebo em tools/texugo_block_529.py desloca **artificialmente 28 dias para trás** apenas as épocas 527/528 já anteriores a cada corte, sem mudar seus valores de movimento médio, sem tocar no 529, sem acrescentar dados e sem permitir que uma época posterior entre no treino. Compara quatro RMSE (quadrático, média, 527 e 528 isolados) e duas curvaturas; arquiva diferenças e eventual falha da invariância numérica. É uma **ablação sintética sobre a linhagem histórica secundária**, não uma correção de relógio nem hipótese orbital. A seleção interna C243-T2 não é objeto desse placebo, pois sua fronteira cronológica interna poderia alterar amostras se os tempos fossem deslocados.

O teste sintético está em tests/test_texugo_block_529.py. O JSON block_529.json incluirá translation_placebos nos quatro cortes. **Resultado no espelho e GitHub Actions do novo HEAD: NOT_RUN até execução confirmada.** A invariância matemática do coeficiente não é alegação empírica de órbita: prova apenas que este estimador de curvatura **não testa sincronismo**. A ausência de observações instrumentais primárias/épocas em mesmo frame e o conflito RAAN persistem; Conde permanece INDETERMINADO.


## C243-T6: controle pós-hoc por rotação do alvo 527, 528, 529 (2026-11-12 UTC)

A seleção exclusiva do 529 como alvo pode favorecer, retrospectivamente, uma curvatura de doador específico. Sem reusar ou rebatizar o mesmo holdout como evidência independente, o [script](../tools/texugo_rotate_target.py) testa simetricamente os três alvos nos **mesmos quatro cortes**, com treinos anteriores a cada corte e futuro **do alvo escolhido** usado exclusivamente para pontuar. Cada alvo recebe seu próprio baseline quadrático, linear e dois doadores individuais, além da média igualitária dos dois. A saída inclui todas as combinações alvo×corte, inclusive `NOT_RUN` por falta de futuro ou menos de três épocas pré-corte, e confronta novamente o alvo 529 com o benchmark original: divergência maior que 1e-8 rev/dia é falha explícita de regressão. Não há seleção do melhor alvo após ver o resultado como se fosse predição. Erro do movimento médio **não mede erro de estado orbital/posição**.

Fonte: [espelho oxzoid Space-Track 1963, versão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, procedência instrumental primária ausente; NASA [boletim 15/11/1963, p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) dá apenas dia da decadência do 003B. Três NORADs **não são três fontes independentes**, e a rotação não resolve RAAN nem posição de queda. Formalização Lean condicional de impacto não é autorizada por este teste.

Reprodução após custódia C243: `python -m unittest discover -s tests -p 'test_texugo_rotate_target.py' -v`; `python tools/texugo_rotate_target.py --parquet /tmp/tle_1963.parquet --csv /tmp/source/norad_527_528_529_1963_numeric.csv --audit /tmp/source/audit.json --output /tmp/rotate_target.json`. O GitHub Actions `texugo-holdout.yml` executa e arquiva JSON no HEAD. **Resultados históricos desta emenda: NOT_RUN até conferência do run exato.**


## C243-T7 — antichurn de pontuação pareada e execução no HEAD (12/11/2026 UTC)

**Falha de implementação demonstrada em teste sintético, não descoberta histórica:** a função central `rmse` aplicava `zip(truth, predicted)`, que truncava silenciosamente a série mais longa, e dividia pelo tamanho completo de `truth`. Assim, `rmse([0, 10], [0])` produzia falsamente zero, como se o valor com maior erro não existisse. Ela também permitia propagar NaN/Inf sem rejeição explícita. O novo contrato só aceita vetores **não vazios, de mesma dimensão e finitos**, e mantém exatamente o cálculo anterior para pares íntegros. Um teste artificial exercita o erro truncado, extensão indevida, vetor vazio, NaN, Inf e valor pareado normal. Não há nova métrica, heurística, escolha de modelos ou gate que exija ganho; os scripts C243, T2, T3, T4/T5 e T6 passam a compartilhar esse contrato único.

**Execução verificável:** a PR empilhada sobre #14 não recebeu runs do Actions para os HEADs mais recentes. O workflow preexistente também passa a escutar `push` **somente na branch própria do Texugo**, além de `pull_request`, para rodar o mesmo experimento histórico completo sobre o SHA real e arquivar os mesmos JSONs. Isso não equivale a declarar PASS: T4/T5/T6/T7 permanecem **NOT_RUN no novo HEAD até o run identificado**. Quando executado, o workflow deve reportar inclusive inversões e falhas de blocos, placebos e alvos alternados.

**Proveniência e classificação:** é uma **auditoria de método**, ocorrência C243-T7, não uma nova fonte. Espelho secundário único [oxzoid/Space-Track 1963 no commit 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; consulta instrumental primária e conflito RAAN ainda não resolvidos. A [NASA de 15/11/1963 p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) registra somente a data de decaimento 1963-003B. Nenhuma alegação de impacto, posição, sincronia, probabilidade ou teorema físico é acrescida.


### Reprodução empírica T4/T5/T6 no HEAD C243-T7 (12/11/2026 UTC)

No [Actions #43151459353](https://github.com/franklinbaldo/conde-incident/actions/runs/43151459353), commit de código [`91ebc699cbc84943a59f5e0fb65e1af4be058a17`](https://github.com/franklinbaldo/conde-incident/commit/91ebc699cbc84943a59f5e0fb65e1af4be058a17), o **workflow Texugo terminou SUCCESS**, com **73 testes Python PASS** incluindo a contraprova RMSE, releitura do Parquet e todas as etapas C243/T2/T3/T4/T5/T6. [Artefato #13913473588](https://github.com/franklinbaldo/conde-incident/actions/runs/43151459353/artifacts/13913473588) contém auditoria/CSV e todos os JSONs. SHA-1 original `623b8a57c959d980f013a9ba5e4bf4a8559adc69` e SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; 21/45/57 linhas brutas 527/528/529, 20/45/54 épocas únicas. A verificação instrumental primária continua **NOT_RUN**.

**C243-T4, remoção de blocos (pós-hoc):** 14 dias deu 17, 19, 20, 20 blocos nos cortes 31/08, 28/09, 11/10, 21/10; 28 dias deu 9, 10, 11, 11. Somam **117 remoções de blocos executadas, zero NOT_RUN**, com **15 mudanças do modelo selecionado cronologicamente** e **8 inversões da direção da vantagem da média 527+528 contra o quadrático 529**. Nenhuma exclusão inverteu a direção da vantagem descritiva do 528 isolado. Esses 117 testes reutilizam linhas e épocas dos mesmos objetos; **não são 117 réplicas independentes, tampouco probabilidade**. Em particular, o sinal da vantagem da média se inverteu em cortes onde o resultado original era favorável a ela; não existe superioridade universal do conjunto.

| Corte | 14 dias: blocos / seleção mudou / sinal da média mudou | 28 dias: blocos / seleção mudou / sinal da média mudou |
|---|---|---|
| 31/08 | 17 / 1 / 1 | 9 / 3 / 0 |
| 28/09 | 19 / 4 / 1 | 10 / 3 / 2 |
| 11/10 | 20 / 1 / 1 | 11 / 1 / 1 |
| 21/10 | 20 / 1 / 1 | 11 / 1 / 1 |

**C243-T5, placebo sintético do relógio:** deslocar as épocas anteriores ao corte dos doadores 527/528 **28 dias para trás**, sem alterar valores de movimento médio, manteve curvaturas e RMSE invariantes até `2.31e-13` rev/dia em todos os cortes. Foram deslocadas 46/53/58/61 linhas, respectivamente. Isso atesta uma propriedade algébrica do **estimador de curvatura**, não que os objetos reais teriam as mesmas posições ou velocidade. Um teste que não percebe tal deslocamento não estabelece sincronização, interação dinâmica ou triangulação.

**C243-T6, rodízio pós-hoc do alvo:** com os quatro cortes originais, a média de curvaturas dos outros dois perdeu para o quadrático **4/4 vezes quando o alvo foi 527, 4/4 quando foi 528**, enquanto foi melhor **3/4** quando o alvo foi 529 (31/08 pior). Todos os **12 pares** tiveram status `EVALUATED_POST_HOC`; os tamanhos de futuro variaram de **2 a 28 épocas** conforme alvo e corte, logo os RMSE absolutos não são métricas diretamente comparáveis *entre* alvos. A alegação de que transferência conjunta melhora genericamente todos os três objetos é **contrariada nesse espelho**. Isso não testa um modelo acoplado físico nem prova independência de sensores.

O artefato histórico e os testes de integridade da perda passaram no **HEAD de código 91ebc699**. Esta anotação documental posterior deve receber seu **próprio run no HEAD final** antes de liberação para Gavião/Elefante. O conflito RAAN 198°/284°, a fonte primária instrumental ausente e a inexistência de ponto/horário de impacto verificado permanecem. Nenhuma hipótese geográfica nem probabilidade foi derivada.


## C243-T8: pseudorreplicação das épocas futuras do 529 (12/11/2026 UTC)

Quatro cortes retrospectivos não constituem quatro fontes independentes. O relatório holdout_529.json agora acrescenta holdout_overlap ao mesmo replay de Parquet e CSV com SHA fixado, sem novo script nem gate de superioridade. Conta, somente para cortes efetivamente avaliados, o conjunto de épocas UTC futuras por corte, interseções aos pares, ocorrências pontuadas e épocas distintas reutilizadas. Um corte NOT_RUN não cria observações. A regressão sintética constrói 10 pontuações distribuídas em apenas 4 épocas distintas e 6 usos repetidos; esses números são artificiais, não registros de 1963.

Proveniência: um único espelho numérico oxzoid Space-Track de 1963, revisão 4b4fb3a, SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09; NASA Situation Report de 15/11/1963, página impressa 8, apenas dia de decaimento 1963-003B. Sem TLE primário, sensores independentes, frame, incertezas físicas ou resolução RAAN. Sem prior, valor-p, posição terminal, probabilidade ou conclusão sobre Conde.

Reprodução: python -m unittest discover -s tests -p 'test_*.py' -v; gerar Parquet e CSV com tools/audit_norad_1963.py --download; rodar tools/texugo_holdout_529.py --parquet /tmp/tle_1963.parquet --csv /tmp/source/norad_527_528_529_1963_numeric.csv --audit /tmp/source/audit.json --output /tmp/holdout_529.json; examinar holdout_overlap. O workflow Texugo já executa o comando e arquiva o JSON original. O resultado histórico T8 permanece NOT_RUN até GitHub Actions no HEAD final. A branch já incorporou por merge de dois pais, sem rebase, C241-T4 a T7 da Tartaruga e manteve C242/C243 anteriores.


## C243-T9: pontuação disjunta de épocas futuras 529 (12/11/2026 UTC)

**Pergunta discriminante:** a vantagem numérica persiste quando cada época futura do 529 conta uma única vez, em vez das 93 pontuações redundantes identificadas em C243-T8? Sem novo script, gate de vitória, nova hipótese orbital ou novos cortes, a função disjoint_horizon_diagnostics no mesmo leitor tools/texugo_holdout_529.py reutiliza **exatamente os coeficientes passados** dos quatro cortes originais. Cada época posterior ao primeiro corte é alocada uma vez, em (31/08, 28/09], (28/09, 11/10], (11/10, 21/10] ou após 21/10. O RMSE por trecho e o agregado ponderado por época usam as **mesmas previsões, sem refit nem consulta ao futuro para escolher modelo**.

Pelo inventário de T8 (28/24/21/20 épocas por futuro aninhado), os trechos devem ter **4/3/1/20 épocas**, somando 28 épocas distintas, **sujeito a confirmação pelo replay no HEAD**. O trecho com uma só época não permite inferência robusta. O agregado não é a média não ponderada dos quatro RMSE; soma os erros quadrados por época antes de extrair a raiz. NOT_RUN exclui explicitamente as épocas não pontuadas e conta as faltantes como não avaliadas, jamais como acerto. Testes sintéticos verificam partição, contagem única, pontuação ponderada, NOT_RUN, duplicatas e cortes repetidos.

**Cautelas:** todos os cortes/seleções e esta ablação são **POST_HOC** e partem da mesma linhagem secundária oxzoid/Space-Track 1963, revisão 4b4fb3a, Parquet SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. Particionar o futuro **não** cria medições instrumentais independentes, validação cega prospectiva, probabilidades ou intervalos de confiança. A NASA de [15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) atesta somente o dia de decaimento do 1963-003B; não é fonte da série de movimento médio. Continuam ausentes TLEs instrumentais primários com época/frame/erro e resolução do conflito RAAN. Portanto não há uma nova restrição Lean historicamente rastreável nem evidência física que possa limitar com segurança a trajetória terminal; impacto/local/hora em Conde permanecem INDETERMINADOS.

**Reprodução:** python -m unittest discover -s tests -p 'test_texugo_holdout_529.py' -v; gerar Parquet e CSV com tools/audit_norad_1963.py --download; rodar python tools/texugo_holdout_529.py --parquet /tmp/tle_1963.parquet --csv /tmp/source/norad_527_528_529_1963_numeric.csv --audit /tmp/source/audit.json --output /tmp/holdout_529.json; examinar o campo disjoint_holdout. O workflow existente arquiva o mesmo JSON no GitHub Actions, sem novo gate. Resultado histórico foi executado no HEAD dea14a0ba; ver seção seguinte e revalidar HEAD documental final.


**C243-T9, replay histórico executado (HEAD dea14a0ba0691cbe15490e194e8a0d21721530d7):** [GitHub Actions Texugo #43165959868](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868) SUCCESS; [artefato original #13920171288](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868/artifacts/13920171288), com Parquet SHA-256 fixado, CSV custodiado e 115 testes Python PASS. A matriz incluiu também C241-T8 da Tartaruga por merge de dois pais, sem rebase, com [custódia #43165959736](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959736) e [Scientific checks #43165959834](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959834) PASS no mesmo commit.

| Trecho do futuro do 529 | Épocas únicas | RMSE quadrático | RMSE média 527+528 | Melhor dos dois |
|---|---:|---:|---:|---|
| 31/08–28/09 | 4 | 0,010525039 | 0,011014283 | Quadrático |
| 28/09–11/10 | 3 | 0,010711596 | 0,009848541 | Média |
| 11/10–21/10 | **1** | 0,018127297 | 0,016582726 | Média, UMA época |
| após 21/10 | **20** | 0,223236815 | 0,215116674 | Média |
| **RMSE agregado por 28 épocas, uma vez cada** | **28** | **0,188775134** | **0,181909995** | Média (pós-hoc) |

RMSE em rev/dia. A transferência isolada do 528 no agregado foi **0,145072060** rev/dia, melhor que a média, novamente uma seleção apenas descritiva e pós-hoc. A média perde no primeiro trecho; sua vantagem agregada de ~0,006865 rev/dia depende fortemente de 20/28 épocas concentradas após o último corte. Ter eliminado a dupla contagem **não** criou medições independentes e o resultado não testa estado orbital, forças comuns ou localização de impacto. **Comparação documental com radar primário e restrição física Lean continuam NOT_RUN.** A confirmação é no SHA acima; toda alteração posterior exige revalidação do novo HEAD.


## C243-T10: uma próxima época 529 por vez, controle prequential (12/11/2026)

O controle rolling_origin_holdout no leitor já existente testa se a vantagem da curvatura média 527/528 persiste em horizontes curtos. Para cada origem igual à última época catalogada do 529, ajusta modelos com 529/527/528 somente até aquela origem e prevê a próxima época 529. Registra cada erro, horizonte, origem, alvo, baseline quadrático, linear, persistência, doadores isolados e média. Um alvo conta uma única vez; treino insuficiente ou singular gera NOT_RUN, nunca acerto artificial. Os testes sintéticos incluem doadores deliberadamente errados, detecção de vazamento temporal, duplicatas e baseline ingênuo.

Este é experimento retrospectivo pós-hoc (decidido após C243-T9), não validação prospectiva. Alvos que já foram pontuados podem alimentar treino posterior; portanto os resultados não são réplicas independentes. O JSON auditado já é preservado no workflow existente; nenhuma nova regra obriga o modelo conjunto a ganhar. Resultado empírico no novo HEAD: NOT_RUN até Actions.

Linhagem: espelho secundário oxzoid/Space-Track, revisão 4b4fb3a, arquivo tle_1963.parquet SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09; comparação independente entre seus bytes e cada linha CSV; não são três instrumentos autônomos. NASA Situation Report 15/11/1963 p.8 documenta apenas dia de decaimento do 1963-003B. Faltam os elementos instrumentais primários com época/frame/erro e resolução RAAN 198,5261 vs 284,1520 graus: nenhuma nova premissa orbital física habilitada para Lean 4.35.0, simulação de queda ou probabilidade.

Reproduzir com python -m unittest discover -s tests -p test_texugo_holdout_529.py -v e o comando de auditoria+holdout indicado em C243-T9; examinar o campo rolling_origin_holdout e o artefato do Actions no SHA efetivo. Resultado quanto a Conde: INDETERMINADO.


**C243-T10 — replay no espelho original (HEAD 054f60509729a2807644ed37bc571b6953ddc160):** [Texugo Actions #43172444338](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338) **SUCCESS**, 132 testes Python PASS, custódia Parquet↔CSV executada; [artefato #13922149343](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338/artifacts/13922149343). Foram **53 alvos consecutivos possíveis, 51 pontuados e 2 NOT_RUN por histórico insuficiente**. Em comparações de erro absoluto por origem, **33/51 vitórias do quadrático**, **18/51 da média**, zero empates; não são 51 réplicas independentes. RMSE agregado dos mesmos 51 alvos, em revoluções/dia: **persistência da última medida 0,026903935; quadrático 0,074988368; doador 528 0,079369300; média conjunta 0,097122160; doador 527 0,116988818; linear 0,117357459**. Este resultado negativo **inverte a conclusão descritiva de C243-T9** quando trocamos o horizonte longo disjunto por próxima época: a transferência conjunta **perde** para o quadrático e para um baseline de persistência. A mudança de desenho foi definida depois dos resultados anteriores, logo não constitui um novo experimento prospectivo nem valida causalidade física. Os espaçamentos entre épocas são irregulares, a sequência é dependente e o catálogo é uma única linhagem secundária. A ausência dos TLEs instrumentais originais impede testes dinâmicos/Lean físico; Conde continua indeterminado. Qualquer merge ou commit documental após 054f605 requer novo CI no HEAD final.


## C243-T11: concentração de erro e deleção pareada de épocas pontuadas (12/11/2026)

**Pergunta discriminante inédita:** o placar prequential do T10 (51 alvos/53 possíveis) depende de poucos erros grandes ou muda quando se retira um bloco **de alvos pontuados**, diferentemente de T3/T4, que removiam épocas do **treino**? A função \`rolling_tail_sensitivity_diagnostics\` usa exatamente as previsões e erros fixos do T10: mede MAE e mediana de erro absoluto, fração do SSE correspondente à pior época de cada modelo, contribuições pareadas ao contraste quadrático versus média e mudanças de classificação após remover (a) cada alvo separadamente, (b) janelas de 28 dias iniciadas nas épocas alvo. Não recalibra coeficientes, não seleciona cortes pelo futuro e não confunde remoção de treino com remoção de pontuação. As janelas se sobrepõem e são diagnósticos **pós-hoc**, não réplicas independentes.

Controles sintéticos verificam perda pareada, caso adversarial em que **um único outlier inverte o vencedor**, reversão também por bloco, preservação de NOT_RUN, duplicatas e NaN. São explicitamente artificiais, não dados históricos. O relatório mantém todas as previsões, erros e horizontes anteriores e acrescenta o campo \`rolling_tail_sensitivity\` ao JSON SHA-auditado existente; o workflow atual arquiva o mesmo JSON, sem novos gates arbitrários. **Resultado no espelho 1963: NOT_RUN até execução no novo HEAD**, incluindo resultados negativos.

**Fonte e linhagem:** [oxzoid/Space-Track Parquet 1963 commit 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 \`c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09\`. Cada linha CSV é confrontada com os bytes Parquet originais e época/source_row. Não são três sensores; todos os modelos usam a mesma linhagem secundária. [NASA Situation Report 15/11/1963 p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) documenta só a **data civil** de decaimento 1963-003B, não trajetória terminal. Sem observações instrumentais originais (época/frame/covariância), resolução de RAAN 284,1520° vs 198,5261° ou evidência de impacto, nenhuma restrição física primária adicional pode ser promovida a Lean 4.35.0: simulação de reentrada e impacto em Conde continuam **INDETERMINADOS**, sem probabilidades.

**Reprodução no HEAD:** \`python -m unittest discover -s tests -p 'test_*.py' -v\` e executar \`tools/audit_norad_1963.py --download\` seguido de \`tools/texugo_holdout_529.py --parquet <arquivo> --csv <csv> --audit <json> --output <saida>\`; ler \`rolling_tail_sensitivity\`. O workflow \`.github/workflows/texugo-holdout.yml\` executa o replay completo e arquiva o JSON. Revisão Gavião e integração Elefante após CI no SHA atual; nenhum merge pelo Texugo.


### Replay C243-T11 efetivo (HEAD 65476d09859f5d0ab1744a5c887a74273ab224db)

[Holdout Actions #43179955290](https://github.com/franklinbaldo/conde-incident/actions/runs/43179955290) **SUCCESS**, 159/159 testes Python PASS, origem Parquet SHA-pinado reaberta e confrontada ao CSV; [artefato #13925094889](https://github.com/franklinbaldo/conde-incident/actions/runs/43179955290/artifacts/13925094889). [Custódia #43179955359](https://github.com/franklinbaldo/conde-incident/actions/runs/43179955359) e [verificações científicas #43179955358](https://github.com/franklinbaldo/conde-incident/actions/runs/43179955358) também SUCCESS no mesmo SHA. Uma primeira execução falhou no teste **sintético** porque o valor manipulado \`0\` era indistinguível de erro numérico de \`~1e-14\` no limite de tolerância; trocado por \`10.0\` e reexecutado, preservando a falha como regressão de desenho de teste, não achado histórico ([run anterior](https://github.com/franklinbaldo/conde-incident/actions/runs/43179669542)).

| Controle pareado, 51 próximas épocas 529 | Quadrático 529 | Média 527+528 | Persistência |
| --- | ---: | ---: | ---: |
| RMSE, rev/dia (C243-T10) | 0,074988 | 0,097122 | **0,026904** |
| MAE, rev/dia (T11) | 0,038059 | 0,046511 | **0,016963** |
| Mediana \|erro\|, rev/dia (T11) | 0,008748 | 0,008986 | **0,008154** |
| Maior participação de uma época na SSE (T11) | **30,05%** | **30,69%** | **25,24%** |

- A maior SSE do quadrático e da média foi a observação catalogada de **30/12/1963 11:25:41 UTC**; isto **não** é horário de reentrada, nem coordenada espacial. Para persistência, a maior foi 28/12 05:25 UTC.
- O somatório de SSE conjunta menos quadrática é positivo em **0,194282 (rev/dia)²** nos 51 alvos. Os três maiores contrastes pareados em magnitude ocorreram 30, 29 e 28/12, somando aproximadamente **69,18% da soma de magnitudes** desses contrastes.
- **Resultados negativos necessários:** remover isoladamente cada uma das 51 épocas **não mudou nenhuma vez** o vencedor quadrático sobre a média; remover cada um de 51 blocos móveis de **28 dias de alvos pontuados** também não mudou o vencedor (**0/51 e 0/51**, 0 NOT_RUN). Os modelos continuam ajustados sobre o passado: este procedimento *retira pontuação*, não testa influência sobre coeficientes de treinamento.
- A maior participação individual na perda é relevante mesmo quando o vencedor pareado não muda. Não inferir robustez a origem sistematicamente enviesada, a séries de outro instrumento, a outros horizontes, a refits do treino nem a perturbações físicas. **Um único espelho secundário, inferência numérica pós-hoc, Conde indeterminado.** O conteúdo documental adicional requer CI do novo HEAD.

## C243-T12: tendências locais sem doadores, contraprova de complexidade (12/11/2026 UTC, 🦡)

**Pergunta discriminante:** a transferência de curvatura 527/528 melhora o próximo valor catalogado de movimento médio do 529 quando comparada não apenas ao quadrático global e à persistência, mas a duas alternativas **sem informação dos doadores** que respeitam o passado recente do alvo? O resultado de C243-T10 mostrou persistência superior; portanto esta pergunta foi concebida **após conhecer** C243-T10/T11, e não é evidência prospectiva.

No mesmo `rolling_origin_holdout` existente (sem criar script/workflow separado), foram adicionados dois controles de cálculo, com tamanhos **fixados antes da nova execução**: (1) reta secante nos **dois últimos registros 529 anteriores** à origem; (2) regressão linear OLS nos **três últimos registros 529 anteriores** à origem. Ambos usam datas UTC verdadeiras e extrapolam até **a mesma próxima época 529** dos outros modelos. Estes dois controles não usam 527/528 nem amostras do 529 posteriores à origem. O corte mínimo original de três registros 529 e três registros por doador é mantido; espera-se preservar os **51 alvos pareados / 2 NOT_RUN** se a entrada histórica e os ajustes continuarem válidos. RMSE, MAE e mediana usam os mesmos alvos; **não escolher o melhor tamanho de janela após olhar o holdout**.

**Falsificação bidirecional sem sandbagging:** em série sintética com quebra de inclinação, uma tendência recente pode superar o quadrático global; em série sintética com erros alternados, extrapolar os últimos dois pontos pode ser pior que persistir o último valor. São contraprovas artificiais declaradas, não dados históricos. Outros testes verificam blindagem do futuro 529, pareamento, caso exatamente linear e NOT_RUN. Se ambos piorarem no espelho, registrar a piora; caso melhorem, isso ainda não demonstra mecanismo físico comum.

**Fonte/linhagem e limite formal:** espelho **secundário** [oxzoid/Space-Track Parquet 1963 revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, auditado bytes Parquet → CSV por `audit_norad_1963.py` e `load_audited`. Os satélites 527/528/529 compartilham linhagem catalográfica e não são três sensores independentes. [NASA/Goddard 15/11/1963, p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) fornece somente **08/11/1963**, dia de decaimento de 1963-003B, sem hora/local. TLEs primários com quadro/época/incerteza e origem do RAAN divergente não foram obtidos. Esses controles de movimento médio não produzem conjunto físico admissível reduzido para uma nova premissa Lean 4.35.0 nem simulação de impacto; resultado sobre Conde: **INDETERMINADO**.

**Como reproduzir:** `python -m unittest discover -s tests -p 'test_*.py' -v`; `python tools/audit_norad_1963.py --download --parquet /tmp/tle_1963.parquet --output /tmp/source`; `python tools/texugo_holdout_529.py --parquet /tmp/tle_1963.parquet --csv /tmp/source/norad_527_528_529_1963_numeric.csv --audit /tmp/source/audit.json --output /tmp/holdout.json`; ler `rolling_origin_holdout.pooled_rmse_rev_day` e `rolling_tail_sensitivity` no JSON arquivado no workflow `texugo-holdout.yml`. **Estado da nova execução histórica no registro desta emenda: NOT_RUN até verificação de Actions no HEAD.** Não extrair probabilidades, p-valores, posição, hora ou causalidade.
