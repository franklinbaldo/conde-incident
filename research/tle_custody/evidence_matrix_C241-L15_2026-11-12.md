---
type: Guide
title: "C241-L15: NASA SP-4004 1963-3 não identifica individualmente o 528"
description: "Custódia do livro NASA anual; separa lançamento agregado, objeto 3B e dependência explícita da série SSR."
---

# C241-L15#1: a mesma agência não é uma segunda medição

**Fonte primária editorial:** [NASA, *Astronautics and Aeronautics, 1963* (NASA SP-4004)](https://www.nasa.gov/wp-content/uploads/2023/04/sp-4004-1963.pdf), produzido pelo NASA Historical Staff e publicado em **1964**, apêndice A, página impressa **501**. Arquivo recuperado em 12/11/2026: **18.442.378 bytes**, SHA-256 `194fdcbc26509fc7ce4ec775aafa4914aa54c57c4617af99d1581790e10ef73d`. No texto extraído do PDF oficial, o apêndice identifica o grupo **`1963-3`** como *DOD Probe/Thor-Agena*, com perigeu inicial **286 milhas estatutárias** e situação textual *Still in orbit*. **Verificação visual da linha e correspondência dos campos à impressão: NOT_RUN**, não é um novo TLE e não possui identificação de componente individual. Não converter milhas em km para alegar correspondência orbital pontual.

**Linhagem declarada pelo próprio livro:** o prefácio do apêndice atribui a compilação a Frank W. Anderson Jr. e diz que os dados orbitais podem provir da órbita inicial, do *Satellite Situation Report* e/ou do relatório presidencial de 1963. **Não identifica qual dessas fontes alimentou a linha particular `1963-3`.** Portanto `SP-4004 -> POSSIBLE_SOURCE_SSR`, não `INDEPENDENT_ORBITAL_OBSERVATION`. A edição é primária quanto ao seu próprio conteúdo editorial, mas secundária quanto a observações instrumentais.

**Conexão cumulativa:** [C241-L12](evidence_matrix_C241-L12_2026-11-12.md) registra no SSR de 15/10/1963 **`1963 3A`, `3B`, `3C`** individualmente; [C241-L11](evidence_matrix_C241-L11_2026-11-12.md) registra a adição incremental do **`1963 3B`** aos decaídos em **08/11/1963** no SSR de 15/11. A grafia **`1963-3` sem sufixo não deve ser automaticamente atribuída ao `3B`/NORAD 528**. Assim, *Still in orbit* no nível agregado não refuta o registro específico de decaimento, mesmo que a publicação do anuário seja posterior. A possível dependência de SSR não duplica o número de sensores. Data editorial não é epoch de observação.

**Arestas/variáveis:** fonte oficial SP-4004 e hash → célula editorial `1963-3` (unidade milhas, status de grupo, data de observação `null`) → vínculo de lançamento com as designações 3A/B/C (`child_piece_identifier=null`) → `POSSIBLE_SSR_SOURCE` → relações com C241-L12 e C241-L11. Estado `CONNECTED_PENDING_CALIBRATION`, independência `NOT_ESTABLISHED`, restrição Lean `NOT_PROMOTED`, domínio admissível não avaliado. **Não inferir** frame, sensor, covariância, peça S00528, hora/posição terminal ou qual RAAN é instrumental. A RAAN 284,1520° permanece sem fonte e inativa; 198,5261° é espelho secundário.

**Reprodução:** `python3 -m unittest discover -s tests -p 'test_tle_nasa_annual_group_audit.py' -v`; baixar o PDF oficial e executar `python3 tools/tle_nasa_annual_group_audit.py --ledger research/tle_custody/nasa_sp4004_1963_group_custody_C241-L15.json --october research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json --november research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json --pdf /tmp/sp4004.pdf`. O teste de hash valida o **arquivo capturado**, não autentica OCR ou tabelas do livro; em caso de alteração na CDN, registrar outra variante e reinspecionar antes de aprovar.

**Resultado negativo:** não foram recuperados nesta fatia TLEs instrumentais 527–529, a edição nº 21 de outubro/1963, identificação material do 528 nem observações radar/sigma/frame; Conde permanece **INDETERMINATE**.
