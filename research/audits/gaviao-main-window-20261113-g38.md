---
type: Guide
title: '🦅 G38: integridade de transcrições NASA e auditoria de dezesseis integrações'
description: Auditoria retrospectiva da main, contraprovas ao cálculo SSR G37 e reutilização do verificador de custódia C241-L18.
---

# G38: a custódia declarada não basta para validar células derivadas

**Janela imutável:** após `4decea805580d59e0388508c6700f2a0c9df583c` (exclusivo, G37) até `1dd6e5619801c685c97a7b2bfc218bad5b811919` (inclusivo, anterior à correção G38). O [manifesto SHA a SHA](gaviao-main-window-20261113-g38.json) contém **16 integrações first-parent, 18 commits DAG, dois merges convencionais e dois commits laterais**. As duas integrações sem marcador de PR na mensagem têm associação documentada: `6981ca13` = #461 e `a66e6487` = #478. Não foram classificadas como pushes diretos pela ausência de sufixo no título.

## Achado G38-F1: cálculo derivado aceitava células impressas adulteradas

A entrega #471 criou `tools/ssr_crossfield_screen_g37.py`, um teste dimensional condicional dos sete registros publicados em três *Satellite Situation Reports*. Ela verificava IDs NTRS e **os hashes declarados**, mas só bloqueava alterações nos dois campos de interesse de dezembro. Não chamava o validador independente já existente `tools/tle_nasa_ssr_jul_dec_audit.py`, que confere valores das sete linhas e identidade documental completa. Assim, uma nova entrada com o **mesmo SHA declarado** mas com período de julho de 529 alterado de `93.9` para `92.0`, ou apogeu de novembro de 529 alterado de `390` para `999` km, era aceita e alterava o resultado computacional. Também eram aceitos URL original substituído, data publicada e hora de referência da edição alteradas. Isso é uma falha de integridade entre transcrição e produto derivado; **não** é prova de adulteração real dos PDFs.

**Contraprova:** seis alterações independentes (período, apogeu, inclinação de julho, URL, data de edição e instante editorial de referência), preservando os campos `sha256`, foram todas aceitas pelo `build()` anterior. Dois novos testes adversariais com subtestes observaram seis falhas antes da correção. Controle positivo: o ledger original ainda reproduz as sete células.

**Correção mínima:** reutilizar `validate(ledger)` do validador C241-L18, sem criar outro catálogo de valores fixos; manter as verificações físicas do G37 e seus erros específicos anteriores ao gate de origem. Isso impede que dados ainda não autenticados como transcrições da custódia entrem no derivado. O valor de resíduo publicado **não foi alterado**; esta é correção de verificação, não nova medida de órbita.

## Reprodução e limites

- Antes da correção: 6 mutantes aceitos. Após: todos rejeitados; **9/9 testes G37**, **23/23 testes de custódia L18** e **1.302 testes Python** no conjunto do projeto (2 skipped) aprovados no checkout de trabalho. A execução direta `python3 tools/ssr_crossfield_screen_g37.py --check` permanece sem drift.
- A validação aqui vincula os sete campos à **transcrição pinada no próprio repositório**, não compara os pixels do PDF durante cada chamada, não recupera novas observações instrumentais nem estabelece a data observada de 528.
- O histórico de CI foi observado pelo endpoint oficial `commits/{sha}/check-runs`, sem supor que todos os checks sejam executados uma única vez. **15 integrações tinham apenas checks com conclusão `success`; #476 apresentava 22 success e 1 cancelled**, registrado sem converter cancelamento em aprovação. #473 apresentou 44 conclusões `success` (execuções duplicadas) em vez de presumir 22. A própria correção deve aguardar CI no SHA exato antes de merge.
- As novas dependências documentais NARA/IBGE/UWM, vetores ISD, testes ópticos e seções SSG não provam hora ou posição terminal; a análise de anomalia impressa de 529 em dezembro permanece **condicional** à convenção e época de cada coluna do SSR. **Conde segue indeterminado**.

A auditoria não autoriza inferir queda nem sobrevoo, nem publica diretamente artigos no blog pessoal. A próxima janela começa após `1dd6e56`, incluindo esta correção e as integrações concorrentes.
