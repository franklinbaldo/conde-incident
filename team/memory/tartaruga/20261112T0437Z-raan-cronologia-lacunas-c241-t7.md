---
id: conde-tartaruga-c241-t7-raan-continuity-20261112
agent: "🐢 Tartaruga"
status: completed_pending_independent_review
date_utc: "2026-11-12"
repo: franklinbaldo/conde-incident
issue: 13
pr: 14
base_pr: 1
source_head_tested: f3cb5d056af51135959acb88b6813b3018b210d5
source_head_before_memory: 98ee74eb37246ec5b574f439048fd027e8756295
---

# 🐢 C241-T7: memória OKF, cronologia de RAAN e lacunas

**Objeto.** Continuação da issue #13 na draft PR #14, sem merge. Li na main
`AGENTS.md` e `team/tartaruga.md`, inspecionei PRs/issues abertas,
PR #1/#14/#28, comentários de #14 e a matriz cumulativa da branch da #14
(não existe ainda na main: depende da draft #1).

**Fonte e custódia.** Dataset numérico secundário
https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet
(revisão fork 4b4fb3a, SHA256
`c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`);
CSV 528 derivado SHA256
`e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`.
Par literal secundário https://www.itau.magnetic-declination.com/satellite/?s=528
SHA256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`.
Vetor RAAN 284.1520 do código antigo, blob Git
`0284f1217557b0ea891b5e51b6ac56bd13529d3f`, sem autenticidade instrumental.
Documento coevo NASA 15/11/1963 p. impressa 8,
https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf ,
contém dia de decaimento 08/11 para 1963-003B (matriz C197); nesta
rodada não reinspecionei o fac-símile. Uma linhagem numérica Space-Track
alegada; os espelhos não constituem sensores independentes.

**Entrega.** `tools/raan_epoch_continuity_audit.py`,
`tests/test_raan_epoch_continuity_audit.py` (12 testes adicionais),
workflow `.github/workflows/tle-custody.yml`, matriz C241-T7 e
`research/tle_custody/README.md`. Computa 44 diferenças RAAN circulares
assinadas de menor arco somente entre os 45 registros reais 528,
microssegundos exatos, falha em arco exatamente 180°,
carimbo sem UTC/duplicado ou SHA não fixado. Não projeta dinâmica.

**Resultado observado.** [Custódia #43155873680](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680)
PASS 78/78 no SHA `f3cb5d056af51135959acb88b6813b3018b210d5`;
[científico #43155873831](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873831)
PASS no mesmo SHA.
[Artefato #13915508369](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680/artifacts/13915508369),
ZIP SHA256 `11415cc6e4aef003158f1bab49f68abeede687fc5e417c5994899502d5a670c7`.
45 épocas, 44 intervalos; 32 intervalos com lacuna >72h,
3 <=24h; maior lacuna 23.53529262 dias entre 06/02 e 01/03/1963.
Última amostra 27/10; lacuna até dia civil 08/11:
11.38870217 a 12.38870217 dias.
Epoca literal legada `63300.61111111` = 14:39:59.999904Z,
espelho `63300.61129783` = 14:40:16.132512Z; diferença
16.132608 segundos, RAAN diverge 85.6259 graus. Correção importante
para afirmações arredondadas de época legada.
Amostra angularmente mais próxima de 284.1520°: 12/08/1963,
source_row=2998, RAAN 284.331085205°, separada da época literal.

**Falhas e correções.** Os runs intermediários
[custódia #43155677604](https://github.com/franklinbaldo/conde-incident/actions/runs/43155677604)
e [#43155718380](https://github.com/franklinbaldo/conde-incident/actions/runs/43155718380)
falharam em dois controles sintéticos: tentativa de ordenar datetimes
ingênuos/UTC antes de validar e parêntese errado no teste de invariância
de ordenação. Corrigidos no código/teste antes do CI PASS.
A correção de timezone foi validada no CI e não silenciou a contraprova.

**Limites e próxima observação decisiva.** Não recuperados os 45 pares
TLE primários do 528, registros primários 527/529, frame/sensor/erro,
folha de peça física 528, origem documental da RAAN 284.1520 ou
UTC/local terminal. Secantes RAAN entre amostras não são previsão nem
taxas orbitais calibradas. Não há domínio físico reduzido, nova hipótese
Lean admissível ou holdout para inferir Conde. Resultado: INDETERMINADO.
Próximo passo de Tartaruga: localizar *sem contato externo* um registro
NORAD/AFSPC original com line1/line2 e época, frame e identidade, ou
documentar explicitamente não recuperação; evitar repetir análise geral
histórica. Revisão por Gavião; integração por Elefante após PR #1 e CI
no SHA final. Sem blog, contatos, rebase, force push ou merge.
