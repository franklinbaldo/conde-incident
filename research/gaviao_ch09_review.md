# 🦅 Revisão independente Caderno 09 / C241-T7

**Objeto exato:** [PR #53](https://github.com/franklinbaldo/conde-incident/pull/53), HEAD `77f7faad20d839863e1b3650ebe63f8dae9801f8`, blob da reportagem `abefabf2dbf942bafd56ca83da25e1506f9e3e65`. Retomada da issue #16 e da PR de auditoria #51, sem editar o texto da Coruja.

## Quatro eixos de auditoria

**Autenticidade:** reinspecionados visualmente [NASA Satellite Situation Report, 15/11/1963, p. impressa 8, PDF p. 10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), linha `1963 3B` com `8 NOV 63` na lista de decaídos, sem hora/posição, e [FBIS 03, p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), transmissão atribuída à Rádio Tupi, não comprovação de esfera ou cratera. C197–C202 são uma cadeia NASA; C01–C02 uma cadeia Tupi/FBIS. Essas cadeias não medem uma mesma trajetória terminal.

**Numerics:** C241-T7 consta na [matriz cumulativa pinada da Tartaruga](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/research/evidence_matrix_C001-C238_2026-11-11.md), sobre a matriz C001–C238 da PR #1. [Script T7](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/tools/raan_epoch_continuity_audit.py) e [CI original #43155873680](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680) verificados em `f3cb5d056af51135959acb88b6813b3018b210d5` (SUCCESS). Fonte é um **único espelho numérico secundário** [oxzoid, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, não 45 boletins instrumentais independentes. O rechecador aqui não importa o algoritmo T7: lê Parquet bruto com SHA, indexa, ordena e calcula diferenças inteiras UTC; contraprovas para duplicatas, offsets, contagem, limiares 24/72 h, RAAN e alterações do arquivo; 18 testes sintéticos executáveis. A confirmação independente dos dados reais exige o CI **deste** SHA.

**Lean 4.35.0:** inferência admissível é condicional aos registros: 45 épocas do espelho implicam 44 lacunas de calendário, não predicados orbitais autenticados. Sem referencial/erro primário, domínio físico não vazio e reduzido, calibração, holdout posicional e prova Lean de impacto continuam **NOT_VERIFIED/NOT_RUN**.

**Exclusão ou identificação:** nenhuma medida terminal conhecida. Os 32 intervalos >72h e máximo 23,53529262 dias descrevem a cobertura **deste espelho**, não cobertura instrumental de 1963. A data NASA não permite fixar fuso, hora ou posição; os extremos 11,38870217–12,38870217 dias são diferenças relativas às meias-noites **convencionais UTC** de 08 e 09/11. Não são janela física de reentrada. Conde permanece **indeterminado**.

## Ressalvas editoriais de precisão

1. A frase «nova posição orbital catalogada» é tecnicamente imprecisa: registros de elementos orbitais por época não são medições diretas de posição. Recomendar «novo conjunto de elementos orbitais catalogados».
2. Explicitar que a comparação de calendário com 08/11 adota UTC por **convenção matemática**, já que a hora e o fuso do evento real não constam do relatório NASA.
3. CI editorial da PR #53 não prova autenticidade instrumental, nem publicação em main; a pilha #3 (Zola) versus #22 (SSG Rust) requer conciliação antes da integração.

**Parecer:** factual e metodologicamente cauteloso, sujeito a essas precisões e ao CI independente no HEAD. Nenhuma afirmação física de queda autorizada. Revisor não faz merge nem publica; GitHub não aceita autoaprovação da mesma conta.
