# 🦅 Revisão independente: Caderno 10 / C243-T8 e C243-T9

**Escopo:** PR editorial [#56](https://github.com/franklinbaldo/conde-incident/pull/56), story blob na revisão `5dac6acc1f6f16eef57662bf3dbec70e27a50474`, após [capítulo 09 #53](https://github.com/franklinbaldo/conde-incident/pull/53); issue única de Gavião [#16](https://github.com/franklinbaldo/conde-incident/issues/16). Este parecer não é uma publicação ou identificação de queda.

## 1. Autenticidade e dependência dos documentos

| Item | Documento/URL, ocorrência | Verificação desta revisão | Independência e limite |
|---|---|---|---|
| NASA *Satellite Situation Report* 15/11/1963, p. impressa 8, PDF índice 9, [fac-símile NTRS](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) | C131/C197 | Imagem diretamente inspecionada: linha 1963 3B / DECAY 8 NOV 63; não consta hora/local | C131/C197 são ocorrências da MESMA fonte; não há posição terminal nem identidade física de um objeto achado no solo |
| FBIS 03, p. 1, [fac-símile do documento retransmitido](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) | C01/C02 | Imagem diretamente inspecionada: `RIO DE JANEIRO RADIO TUPI ... 2330 8 NOV 63 W`; texto noticia esfera, cratera e corpo | Transcrição de relato jornalístico, NÃO registro sonoro, medição de radar, nem duas testemunhas independentes |
| [Parquet oxzoid/Space-Track, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet) | C243-T8/T9 na [matriz da PR #20 SHA 74ff98f8](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/evidence_matrix_C001-C238_2026-11-11.md) | Hash alegado SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; conferência de bytes e replay independente obrigatórios no CI desta PR | Um único espelho numérico secundário, SEM pares TLE originais/radar, proveniência instrumental, frame ou covariâncias auditadas |
| [Texugo #20, relatório C243-T8/T9](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/texugo_holdout_529.md) | C243-T8/T9 | Tabela e algoritmo lidos diretamente no SHA fixado; [CI anterior #43165959868](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868) declara replay | O relatório e a notícia **dependem do mesmo espelho e do mesmo experimento**; não são réplicas instrumentais independentes |

A matriz cumulativa C01–C238 da [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1) foi consultada, mantendo C197–C202 como correção da leitura NASA. A origem instrumental de 527–529 e o conflito RAAN 284,1520° × ~198,5261° permanecem abertos. Não converter referência de um documento em testemunho físico adicional.

## 2. Auditoria de coerência numérica (independente de Texugo)

O [verificador independente](../tools/gaviao_ch10_independent.py) **não importa** o código do Texugo, lê diretamente o Parquet pinado, rejeita SHA-256 diferente, deduplica por objeto+época (recusando duplicatas contraditórias), realiza regressão por SVD/NumPy e pontua uma só vez cada época futura no seu trecho. Não escolhe corte/modelo pelo futuro. Os [testes adversariais](../tests/test_gaviao_ch10_independent.py) usam dados declaradamente **sintéticos** e incluem entrada adulterada, faltas, duplicatas, NaN e vazamento. O workflow verifica `git rev-parse HEAD` contra o SHA real e fornece artefato JSON.

**Contas auditáveis independentemente da regressão, calculadas sobre a tabela publicada (não substituem replay):**

- Usos nos futuros aninhados: `28+24+21+20 = 93`. A alocação disjunta `4+3+1+20 = 28` não acrescenta observações.
- RMSE agregado correto: `sqrt((4*r1² + 3*r2² + 1*r3² + 20*r4²)/28)`, **não** média simples dos quatro RMSE.
- Essa conta dá quadrático `0,1887751337` e média `0,1819099949` rev/dia, reproduzindo por aritmética os arredondamentos da reportagem.
- **Achado adicional sobre concentração da métrica:** os 20 pontos do último trecho respondem por **99,888%** da soma de erros quadráticos do quadrático e **99,887%** da soma da transferência conjunta (não apenas 20/28=71,43% das épocas). Cerca de **99,91% da diferença entre as somas de erros quadráticos** também provém do último trecho, segundo os RMSE publicados. Esta é decomposição **algébrica de números relatados**, não novo dado instrumental, estimativa de incerteza ou significância estatística.
- Excluído apenas o último trecho, agregando as primeiras oito épocas, obtêm-se `0,0118105861` (quadrático) e `0,0114631246` (média), ambos rev/dia. Essa exclusão é diagnóstico pós-hoc; não valida a escolha do modelo nem compara independência temporal.
- O modelo conjunto piora no primeiro trecho (`0,011014283 > 0,010525039`). O terceiro tem apenas uma época; a escolha isolada do 528 (`0,145072060`) é retrospectiva.

**Reexecução independente concluída no HEAD de código/documentação `b9e95142d3cef2059cd92b94eec448d77b471fc6`:** [GitHub Actions #43171030913](https://github.com/franklinbaldo/conde-incident/actions/runs/43171030913) SUCCESS, `TESTED_SHA` verificado, **12/12 testes sintéticos** e leitura do Parquet pinado com `numpy.linalg.lstsq` sem import de Texugo. O JSON do artefato [#13921987815](https://github.com/franklinbaldo/conde-incident/actions/runs/43171030913/artifacts/13921987815) registra 93 usos, 28 épocas, 4/3/1/20, RMSE `0.188775133548` e `0.181909995184` rev/dia, participação de SSE no último trecho 0.9988816306 e 0.9988654468. Outros sete workflows herdados ficaram verdes **no mesmo SHA**. Alterações documentais posteriores requerem gate novamente no HEAD final.

**Estado dos níveis de verificação:** tabela, contas e replay independente do Parquet = verificados como computação do espelho; sensor de 1963 = NÃO VERIFICADO; uma *joint physical fit* com holdout posicional e erro = NÃO EXECUTADA.

## 3. Lean 4.35.0, física e limites de inferência

O C243-T9 testa movimento médio catalogado (rev/dia), não vetor de estado, fase, referencial, sincronização ou forças acopladas. Nenhuma restrição física nova rastreável a observação primária foi verificada; não há demonstração aqui de **domínio não vazio e reduzido** de parâmetros nem teorema Lean de localização. A cadeia exigida na proposta [#28](https://github.com/franklinbaldo/conde-incident/pull/28) interrompe-se antes da etapa de restrição empírica/validação dinâmica. Um kernel Lean atestaria somente implicações sob premissas explicitadas.

Reentrada em um dia da NASA **não** determina longitude, hora ou impacto; FBIS **não** atesta corpo ou cratera no solo. As cinco saídas científicas possíveis permanecem abertas, e com esta evidência o resultado físico é **INDETERMINADO**, não `Conde confirmado` nem `Conde excluído`.

## 4. Auditoria editorial e condições para integração

O texto da #56 distingue adequadamente recontagem de evidência, usa números rastreáveis e explicita resultados negativos. Há **uma precisão terminológica recomendada**: na abertura, substituir `curvatura orbital` por `curvatura da série temporal de movimento médio`, porque não se mediu curvatura geométrica da trajetória. Outra oportunidade jornalística: mostrar que o último trecho concentra aproximadamente 99,9% da perda quadrática, não só 20/28 datas, **claramente como análise derivada**.

Parecer editorial só é favorável condicionalmente a replay numérico independente verde no SHA final e ausência de mudanças factuais posteriores. O CI não autentica elementos NORAD originais. A #3 usa Zola, enquanto #22 propõe SSG Rust; essa divergência arquitetural bloqueia publicação independentemente desta revisão. Nenhuma mudança no texto da Coruja, blog pessoal ou outras branches; sem publicação, contato ou merge.

**Próxima pergunta discriminante:** existe holdout posicional de um objeto distinto (527/528) com efemérides primárias, frame e erros conhecidos, que falsifique a hipótese de curvatura compartilhada? A ablação de alvo de C243-T6 já contraria universalidade *no espelho*, mas não substitui dados físicos.
