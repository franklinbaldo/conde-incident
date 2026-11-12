# OKF — 🐢 Tartaruga, 12/11/2026, sessão C241-L1

## Contexto
AGENTS.md, team/tartaruga.md, skill conde-tartaruga, issue #13,
draft #14 e matriz principal C001–C238 lidos. Main no início:
`7b4e86f30e7d65146422c544f5926d6799d1a871`. PR #14 tinha 52 arquivos contra a base empilhada,
e #83/#84 já trouxeram para main o par 528 e a correção operacional.

## Entrega verificável
Isolar da PR #14 exatamente o auditor literal 69 colunas/checksum
`tools/tle_literal_layout.py` (blob de origem `46316d1d527361ed4e5582980266157a3eb8a45f`), e dez
testes adversariais `tests/test_tle_literal_layout.py`
(blob `ebd6222e896fe88a6ab0168e370d5dcf31839fea`), adicionando workflow que verifica o HEAD e
arquiva relatório JSON, mais ocorrência C241-L1 da matriz. Não arrastar
código/dados/CI volumosos da PR empilhada para main.

## Evidência e limites
- Itau 528, URL https://www.itau.magnetic-declination.com/satellite/?s=528
  (cópia SECUNDÁRIA), arquivo já em main SHA256
  `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`.
- CelesTrak https://celestrak.org/columns/v04n03/ para sintaxe.
- NASA https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
  (citação C197 da matriz; **não reinspecionada nesta fatia**):
  dia 08/11 apenas. Não é sensor independente do mesmo rastreamento.
- 198,5261° é valor secundário documentado; 284,1520° permanece
  elemento legado NÃO autenticado e não deve alimentar simulações.
  Nenhuma prova de original NORAD 1963, sensor/frame, S00528 físico,
  45 pares primários, erro, hora/local terminal.
- Nenhuma nova restrição física admissível em Lean; Conde indeterminado.

## Falhas/tentativas e próximo passo
Não se tentou converter floats Parquet em linhas TLE nem contatar arquivos.
A validação exigida é GitHub Actions no HEAD da PR; status/URL devem ser
registrados no handoff após execução (não alegar CI ainda aqui).
Próxima fatia: transportar extrator numérico com SHA pinado, índice
`source_row`, 45 épocas e teste de não dependência da altitude ETL,
em PR pequena própria; evitar duplicatas da #14.

Branch/PR: ver PR aberto desta sessão na issue #13. Revisão por Gavião
retrospectiva caso merge seguro pelo autor.

## Falha intermediária e correção (mesma sessão)
No HEAD `33319837a6718e802cbb798124b2875ee47cc823`, o nosso workflow [#43210899314](https://github.com/franklinbaldo/conde-incident/actions/runs/43210899314) executou **10/10 testes PASS**, guardando o JSON artefato #13939854607, SHA-256 do ZIP `02cd08c256c81757a98628d40cd0bfebba84d81bf61ceeb984f9085e08ce6586`.
Mas a edição da matriz principal causou dois gates vermelhos por **Git blob fixado**: [#43210899133](https://github.com/franklinbaldo/conde-incident/actions/runs/43210899133) e [#43210899161](https://github.com/franklinbaldo/conde-incident/actions/runs/43210899161). A matriz original foi reposta *byte a byte*; esta entrada foi movida ao suplemento `research/tle_custody/evidence_matrix_C241-L1_2026-11-12.md`, vinculado pela integração. Não adulterar pin ou calcular novo hash para ocultar o bloqueio. Revalidar HEAD corrigido, inclusive os dois gates falhos, antes de merge.

## Integração sem rebase com main concorrente
Durante este trabalho, #87 entrou em main no SHA `006c7d08b64956aeeabed7162b5604bba77de85b`, trazendo workflow novo de conexões científicas cumulativas e arquivo `tests/test_cumulative_constraints.py`. O checkout anterior da branch não tinha o teste, causando [CI #43211235268](https://github.com/franklinbaldo/conde-incident/actions/runs/43211235268) **FAIL (0 testes descobertos)** por estar atrás da main, não por falha dos dez testes TLE. Integrada main por commit de merge **dois pais**, sem rebase, force-push ou alteração dos arquivos da ciência cumulativa. O CI no HEAD de merge deve ser observado antes de integrar PR.
