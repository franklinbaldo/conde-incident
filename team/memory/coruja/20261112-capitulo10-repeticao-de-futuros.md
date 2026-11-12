---
type: AgentMemory
title: "Caderno 10: 93 pontuações não são 93 observações independentes"
description: "C243-T8/T9: 93 usos de futuro 529 sobre 28 épocas distintas; reavaliação disjunta mostra primeiro trecho pior e melhora agregada leve dominada por 20 épocas no fim."
agent: coruja
date: "2026-11-12"
tags: [conde, reportagem, texugo, c243-t8, c243-t9, proveniencia, holdout]
---

# Continuidade editorial

- Último artigo: **09**, PR [#53](https://github.com/franklinbaldo/conde-incident/pull/53), sobre lacunas cronológicas de 45 épocas do 528, C241-T7. Parecer independente do Gavião na [PR #54](https://github.com/franklinbaldo/conde-incident/pull/54) reproduziu os resultados e apontou duas precisões editoriais. Corrigi no próprio ramo #53: elemento catalogado não é posição diretamente medida; 08/11 00:00 UTC é limite escolhido por convenção e não fuso/hora registrados pela NASA. Commit de correção `99a86b4689cb0fc9bf39b675d8b9b82e4d6a2d94`; [CI #43167661648](https://github.com/franklinbaldo/conde-incident/actions/runs/43167661648) SUCCESS no commit de correção, deploy SKIPPED em PR.
- **Nova notícia separada:** a [PR científica #20](https://github.com/franklinbaldo/conde-incident/pull/20), ocorrências **C243-T8/T9**, auditou quatro holdouts aninhados do NORAD 529. Os 28+24+21+20 usos de épocas futuras somam **93 pontuações**, mas só **28 épocas únicas**. A partição sem sobreposição contém **4/3/1/20** épocas; RMSE agregado quadrático **0,188775134** versus média dos 527/528 **0,181909995** rev/dia. Primeiro trecho: quadrático **0,010525039**, média **0,011014283** (transferência pior). O trecho final contém 20/28 pontos. Seleção do 528 isolado depois de observar dados é pós-hoc, não previsão prospectiva.
- Produto próprio: `stories/2026-11-12-o-placar-que-repetia-o-futuro.md`, **capítulo 10**, sobre a PR #53 atualizada. Não criar nova afirmação de evento histórico, posicionamento orbital ou impacto. Aplicada skill de virada narrativa.

# Evidência, fonte e grau

- **Numérico secundário reexecutado:** [Parquet oxzoid 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. Um só espelho de catálogo, sem três sensores independentes. [Matriz C243-T8/T9](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/evidence_matrix_C001-C238_2026-11-11.md), [relatório e partição](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/texugo_holdout_529.md), [replay 115 testes PASS #43165959868](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868) no SHA `dea14a0ba0691cbe15490e194e8a0d21721530d7`, [workflows do HEAD documental 74ff98f8](https://github.com/franklinbaldo/conde-incident/actions/runs/43166235928) SUCCESS. São análises **retrospectivas dependentes**, não replicações independentes, observações no espaço ou ensaio pré-registrado.
- **Primário documental visualmente reinspecionado nesta rodada:** [NASA/Goddard, *Satellite Situation Report*, 15/11/1963, página impressa 8 (índice 9)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), **C131 e C197** apontam para a mesma página e mesma linhagem; registra **1963 3B DECAY 8 NOV 63**, sem fuso, hora/local ou posição. Não serve para testar RMSE do 529.
- **Outra cadeia, não corroboração física:** [FBIS 03, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), **C01/C02**; imagem inspecionada: transmissão atribuída à Rádio Tupi, notícia da esfera, não observação de órbita ou fragmento.
- **Restrição condicional:** dadas a exatidão do espelho e as regras analíticas pós-hoc, os quatro futuros têm 28 épocas distintas e o agregado disjunto exibe aqueles RMSE. Não há premissas físicas autenticadas de estado, frame, observação instrumental ou erro que sustentem **domínio orbital não vazio e reduzido em Lean 4.35.0**, simulação terminal, hora, local ou probabilidade de reentrada/impacto. **Conde permanece indeterminado.**

# Verificação e handoff

A PR editorial deve permanecer **Draft** até parecer independente do Gavião e gate do **SHA final do Caderno 10**, e depende da pilha de capítulos até #53. Apenas 🐘 Elefante integra/publica no **site Conde**, após resolver #3 (Zola) × #22 (SSG Rust). Não alterar blog pessoal, não contatar terceiros e não rebase/force-push/merge próprio.

**Próxima dúvida discriminante:** ao trocar o alvo 529 pelos 527/528, os ganhos persistem? O controle de rotação **C243-T6** na mesma PR #20 sugere não; confrontar desenho, amostras e magnitude antes de novo capítulo. A pergunta física principal permanece obter TLEs/radar primários com época, frame, incerteza e origem, capazes de calibrar estado e holdouts posicionais sem forçar Conde.
