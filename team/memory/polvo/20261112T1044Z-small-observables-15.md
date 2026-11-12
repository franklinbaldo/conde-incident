---
kind: OKF
agent: polvo
date: 2026-11-12
scope: franklinbaldo/conde-incident
issue: 15
pr: https://github.com/franklinbaldo/conde-incident/pull/70
---

# Fatia separada da PR #17: observáveis C179 / C151

**Motivo:** proprietário pediu PRs pequenas, revisáveis e integráveis. A PR #17 tem cerca de 60 arquivos e depende da #1; esta entrega extrai um único comportamento numérico comprovado e reduz o escopo a **script + teste + CI + esta memória**. Não altera nem substitui a PR #1, o Castor ou o blog.

**Entradas:** matriz congelada da PR #1, blob Git SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7`. C179#1: espelho secundário AFSPC NORAD 528, https://www.itau.magnetic-declination.com/satellite/?s=528, data 27/10/1963 14:40:16 UTC no texto da matriz, n=15,74901460 rev/dia, RAAN 198,5261°, i=81,8615°, e=0,0017147. **Não** é documento primário de rastreamento de 1963 nem uma observação independente do Parquet. C151#1: dados de vento medidos em **Recife** no perfil NOAA IGRA `BRM00082900` para 08/11/1963, 12 UTC nominal, https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip ; horário real de lançamento não registrado; cinco níveis da mesma origem NCDC, nenhum vento observado em Conde. A fonte primária NASA para dia de decaimento catalogado 08/11, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf (C131/C197, um único boletim), **não** foi reinspecionada e não entra como restrição geométrica.

**Questão falsificável:** os números da matriz geram por operações com unidades os mesmos observáveis numéricos, sem transformar alteração de unidade em nova testemunha e sem identificar vento Recife como local de queda? Script `formal/scripts/source_observables.py`: valida SHA do blob, extrai exclusivamente as linhas C151/C179, converte n[rev/dia]→rad/s→a/perigeu keplerianos + derivada nodal J2; p[hPa]→Pa e vento meteorológico “de onde” para vetor leste/norte. Sensibilidade hipotética 50 m/s de descida fixa entre 11km e 1,56km no perfil de Recife resulta em cerca de 188,8s e ~1,3km de deriva horizontal **parcial**, não até o solo. Dobrando a velocidade hipotética reduz-se a deriva pela metade. **Não** atribui massa, sobrevivência ou perfil de Conde ao 528.

**Antes → depois:** restrição física de RAAN na época de referência: **[0°,360°) → [0°,360°)**, sem redução; o mesmo para posição/tempo terminal. São novos observáveis computados de números rastreáveis, não limites de erro físicos. O domínio formal permanece não vazio sob os parâmetros livres, mas não foi validada distribuição de erro instrumental nem nova observação orbital. Baseline/holdout de 527/529 e compatibilidade órbita terminal continuam NOT_RUN. ZIP original Evidence.lean 154 proposições/151 IDs ausente; a biblioteca não foi reconstruída por suposição. Não confundir sucesso do teste de parsing com validação histórica.

**Testes:** `python3 -m unittest discover -s formal/tests -v`, `python3 formal/scripts/source_observables.py --matrix research/evidence_matrix_C001-C238_2026-11-11.md --assumed-descent-mps 50 --output /tmp/conde-observables.json`, `cd formal && lake build`, todos no workflow head real; status CI deve ser preenchido após execução, não inferido daqui.

**Próximo:** depois de #1 e desta PR passarem por Gavião e integração de Elefante, remover a duplicata `physical_observable_bridge.py` da grande PR #17 ao fatiá-la, preservando apenas as diferenças materiais. Perguntar à Tartaruga dados espaciais/tempo/origem adequados para intervalo de erro físico e ao Castor um teste com holdout real que reduza o domínio; não adicionar teoremas abstratos. Sem merge próprio, força de branch, contatos ou publicação.

**Validação reproduzida da fatia antes do fechamento OKF:** commit `31ccca559236af2841be63f82806e1df261d5f0b`, [GitHub Actions #43204659649](https://github.com/franklinbaldo/conde-incident/actions/runs/43204659649), **SUCCESS** nos jobs `lean` e `web`. `python3 -m unittest discover -s formal/tests -v` confirmou **5/5** regressões; o extrator emitiu `weather=RECIFE_ONLY` e `historical_domain_reduction=NOT_RUN`; `lake update`, `lake build` com Lean 4.35.0 e `#print axioms` das cinco provas já presentes em `Core.lean` passaram. A verificação dos axiomas nesta PR usa `formal/Conde1963/SourceAxiomAudit.lean` (não acrescenta teorema ou resultado histórico). Houve duas falhas previamente corrigidas: checkout inicial apontava ao merge ref em vez do SHA head e a expressão regular capturava vírgula terminal da excentricidade, ambas solucionadas antes do PASS. **A rodada final após atualizar esta memória precisa conferir o novo HEAD**, e o comentário na PR registra esse SHA final. Scope final: 5 arquivos.
