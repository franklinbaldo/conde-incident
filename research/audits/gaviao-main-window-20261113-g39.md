---
type: Guide
title: '🦅 G39: identidade das fontes cartográficas e quatorze integrações'
description: Auditoria retrospectiva da main, contraprovas adversariais de linhagem cartográfica CGEO-25 e limites científicos da interpretação histórica.
---

# G39: um SHA declarado não fixa o endereço da fonte

**Janela retrospectiva fechada:** `1dd6e5619801c685c97a7b2bfc218bad5b811919` exclusivo até `4a5f0d35bc10c14927e1b948b63c516f5184ddfb` inclusivo, antes da correção G39. O [manifesto](gaviao-main-window-20261113-g39.json) registra 14 integrações first-parent, 15 commits no DAG, um merge convencional (#484), um commit lateral, nomes dos arquivos tocados e resultados dos check-runs por SHA. Não foram inferidos pushes diretos pela ausência de sufixo no assunto.

## Achado G39-F1: troca documental sem mudar o hash declarado

A PR #488 apresentou em `research/geo/cgeo25_esplanada_edition_lineage.json` três fontes cartográficas com SHA-256 declarado e tamanhos publicados. O validador `tools/cgeo25_esplanada_lineage.py` conferia os digests do próprio manifesto, mas para a URL exigia somente prefixo `https://`, e para `local_filename` apenas sufixo `.pdf`. A identidade exata do catálogo SUDENE e dos bitstreams SGB, a página indicada e a legenda cartográfica não eram todas verificadas. Também podiam ser adicionados novos campos não inspecionados ao objeto de fonte.

**Contraprova isolada, sem alterar fonte real:** seis mutações foram aceitas pelo validador antigo: URL externa, troca do identificador do bitstream no mesmo domínio SGB, outro nome local de arquivo, legenda fictícia com impacto de NORAD 528, índice de página SGB alterado e campo adicional de posição histórica fictícia. O novo teste falhou nos seis casos antes do reparo. Após a correção, exige URLs e metadados específicos de cada fonte, conjunto fechado de chaves e controle positivo do manifesto original.

A correção **não baixa os três PDFs** nem prova correspondência entre bytes vivos, fac-símile e campos do catálogo. O replay local com `--sources-dir` continua sendo a verificação de bytes, quando os exemplares preservados estiverem disponíveis. A atribuição de uma fonte a uma edição de 1973 permanece posterior ao incidente de 1963. Nenhuma localização de queda ou erro horizontal foi inferido.

## Demais integrações e ressalvas

- #481 e #490 ampliaram triagens orbitais condicionais; comparação de períodos de dezembro de 1963 não é um ajuste orbital histórico calibrado.
- #485 documentou canais institucionais GSFC–NORAD. Canal de intercâmbio não é medição instrumental individual dos objetos 527/528/529.
- #487 e #484 conectaram vetores meteorológicos e linhagem Caravelas, sem promover uma estação distante a meteorologia observada em Conde.
- #491 identificou a publicação da Lei 628/1953 no DOE de 1º/01/1954. Esta rodada não reinspecionou as páginas originais e não considerou demonstrado o polígono municipal de 1963.
- #492 corrigiu a preservação dos feeds JSON no Pages; a disponibilidade HTTP posterior foi declarada na PR, mas não foi reproduzida independentemente aqui.
- #493 e #496 alteraram navegação e narrativa, com ressalva editorial explícita sobre a coincidência dos dois buracos de quatro metros em notícias distintas.

**CI do corte:** as integrações #483, #486, #488 e #492 apresentavam checks `cancelled` na consulta da API de check-runs; as demais tinham somente conclusões `success` na consulta. Cancelamento de uma execução concorrente não foi convertido em aprovação. O estado do CI da correção G39 deve ser registrado separadamente no HEAD da própria PR e após eventual merge.

**Resultado:** deficiência de verificação no código do projeto, não adulteração comprovada das fontes. Nenhuma nova observação fixa a hora ou a posição terminal de NORAD 528; a hipótese Conde continua indeterminada. Próxima janela após `4a5f0d35`, incorporando a própria correção e os merges concorrentes.
