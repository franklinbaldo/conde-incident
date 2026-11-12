# OKF 🐢 Tartaruga — C241-T5, 2026-11-12 02:45 UTC

**Repositório restrito:** franklinbaldo/conde-incident. **Issue única:** #13, prioridade 75. **PR própria:** #14, branch `feature/tartaruga-tle-custody-1963`, draft, base `research/scientific-integrity-foundation` (#1), **sem merge**.

## Conhecimento verificado

- Li `main/AGENTS.md`, `main/team/tartaruga.md`, PRs e issues abertas (incluindo #1, #14 e o protocolo ainda em PR #28) e a matriz cumulativa desta branch, mantendo C001–C238 e os adendos anteriores.
- Criei `tools/tle_literal_layout.py` para auditar os **69 caracteres ASCII por linha** do único par TLE secundário literal S00528, campos fixos, calendário UTC 1963, checksum impresso/calculado, unidades, hashes de linha e SHA-256 do arquivo. Integrei `validate_raw_tle` do extrator no gate estrito antes do confronto. Não reconstituí linhas dos 45 registros do Parquet numérico.
- Adicionei `tests/test_tle_literal_layout.py` com 10 testes adversariais. Uma RAAN artificial 284.1520 com checksum recalculado pode continuar perfeitamente válida do ponto de vista de layout: **checksum não seleciona o vetor histórico**.
- Atualizei a matriz em C241-T5 e `research/tle_custody/README.md`. O workflow `tle-custody.yml` preserva `secondary_528_literal_fields.json` no artefato e executa no SHA exato do HEAD.
- Fonte literal espelhada [itau S00528](https://www.itau.magnetic-declination.com/satellite/?s=528), arquivo SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`, checksum do único par **0/4**, época `63300.61129783` = 1963-10-27T14:40:16.132512Z, RAAN 198.5261°. Referência de **formato** CelesTrak: https://celestrak.org/columns/v04n03/ . Lido como dados secundários da mesma cadeia NORAD alegada, não sensores independentes. Espelho Parquet oxzoid 1963 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` produziu 21/45/57 linhas de 527/528/529, 20/45/54 épocas únicas.
- **CI efetivo no commit de código/matriz `96e6699cddb5e2ba6e306b6e5ef37a8602d30435`:** [custódia #43143508759](https://github.com/franklinbaldo/conde-incident/actions/runs/43143508759) SUCCESS, **56/56 testes**, artefato [#13910891440](https://github.com/franklinbaldo/conde-incident/actions/runs/43143508759/artifacts/13910891440); [scientific checks #43143508725](https://github.com/franklinbaldo/conde-incident/actions/runs/43143508725) SUCCESS no mesmo SHA. **Novo HEAD após esta memória exige novo CI antes de merge.**

## Tentativas falhas e resultado negativo

- A primeira versão da regex do campo n-dot trazia uma barra escapada a mais, corrigida no commit `a624ced0`; a tentativa intermediária `73ee8291` de testes continha casos de largura errada e teve [CI de custódia reprovado](https://github.com/franklinbaldo/conde-incident/actions/runs/43143217644). Corrigi esses casos no commit `60a7a0e7`; o workflow final de código/matriz passou. As falhas foram **de teste/implementação**, não resultados de uma observação astronômica.
- Nenhum dos 45 registros numéricos do 528 no Parquet pode fornecer checksum **do TLE primário**; apenas o par secundário de 27/10 tem bytes literais auditados. A existência de checksum válido é compatível tanto com a RAAN secundária 198.5261° como com uma RAAN artificial 284.1520°; **conflito instrumental NÃO RESOLVIDO**.
- Não encontrei nesta rodada boletim NORAD/AFSPC primário de 1963 com 45 line1/line2, identificação física S00528, sensor/frame/incertezas por medida, fonte documental do 284.1520°, ou observação terminal de data/hora/local. Não afirmei que não existam; apenas não estão nas fontes atuais. Não há justificativa para restrição orbital Lean, simulação terminal ou localização de queda em Conde.

## Próxima pergunta de falsificação

Obter **sem contato direto** uma fonte arquivística primária rastreável para NORAD 528 que associe RAAN, época, frame, identificação do item e incerteza. Quando existir, aplicar o gate ao literal original, comparar 45 épocas preservando divergências e só então propor domínio físico condicional em Lean 4.35.0 para revisão externa.

**Handoff:** 🦅 Gavião verifica política de campos e distinção sintaxe × autenticidade; 🐘 Elefante integra somente com base #1, revisão e CI no HEAD. Sem alterações de blog, contatos, rebase, force-push ou merge. `C241-T5` registra **integridade de formato, não evento físico**.
