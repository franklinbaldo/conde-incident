# OKF 🦅 Gavião — 12/11/2026 — revisão Caderno 12 / C241-T10

## O: observações e fontes verificadas
- Li `AGENTS.md` e `team/gaviao.md` na main, issue #16, PRs #3/#14/#22/#28/#59/#60/#61/#62 e matriz cumulativa no SHA `1934198e260b9dae8c056587cc7a16c777d58d25`.
- Inspeção visual direta: NASA 15/11/1963 p. impressa 8/PDF índice 9 `1963 3B / 8 NOV 63` (somente data catalogada); FBIS 03 p.1 `RADIO TUPI` (somente relato retransmitido). Links e gradação no `research/gaviao_ch12_review.md`.
- Pinado: código legado 528 Git blob SHA-1 `0284f1217557b0ea891b5e51b6ac56bd13529d3f`, **origem instrumental não verificada**; par secundário 528 SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`, **independência não estabelecida**. Um checksum TLE não prova uma medição.
- A PR #59 corrigiu G11-B1 com tabela de 18 alvos em 7–30 dias e limitação pós-hoc no SHA `2c2301e1c1b203fa39898a1d3f7d521be457ad1e`, CI #43183133331 SUCCESS. A nova #62 invoca C241-T10 sem fonte original NORAD.

## K: conhecimento, teste adversarial e limites
- Achado geométrico independente: para ambas inclinações 81,8615° e ΔRAAN=85,6259°, ângulo **condicional** entre normais de planos = **84,5612921°**, não `>85°`. A pergunta inicial da #62 confunde esses dois ângulos: **G12-B1 bloqueador editorial**. Ainda não existe referencial histórico autenticado para afirmar separação entre planos reais.
- Recalculei Δépoca=16,132608 s e taxas J2 proxy −1,17328099 / −1,17312407°/dia. O modelo estrito de defasagem temporal isolada não explica a discrepância, sem determinar qual registro está certo.
- Código próprio sem importar Tartaruga, testes adversariais e replay de duas revisões + hashes em workflow dedicado. CI precisa confirmar SHA final. Nenhum dado simulado foi apresentado como observação; não há restrição física Lean, domínio historicamente reduzido, propagação terminal, holdout posicional ou conclusão de impacto.
- Herança anterior: PR #60 no SHA `8105fad62bb13e71735f977b34cfed24a85b5c13`. Branch nova `gaviao/ch12-independent-plane-geometry-20261112` separada; não editar PR/branch da Coruja.

## F: falhas, próximos testes, handoff
- Faltam NORAD 528 original, instrumento, referencial, incertezas e identidade de peça. Data civil NASA ≠ hora e local; FBIS ≠ impacto. Não promover inferência condicional a verdade física.
- Solicitar alteração mínima na frase de abertura #62 para “valores de RAAN separados por 85,6259°” e CI no novo HEAD; reavaliar depois. #59 permite parecer editorial favorável em seu HEAD corrigido, com dependência Zola #3 × SSG #22 ainda pendente.
- Próxima dúvida: existe cadeia primária que relacione a RAAN legada 284,1520° a um catálogo/instrumento de outubro/1963? Testar explicitamente o referencial antes de inferir plano observado.
- Não houve merge, deploy, contatos externos, alteração do blog pessoal, rebase nem force-push.

## Gate de fechamento (PR #63)
- PR de auditoria independente: https://github.com/franklinbaldo/conde-incident/pull/63 (head anterior à inclusão desta nota `0be80ae136ca3d4900c7da568d7760e94573bf97`). [Actions #43185280933](https://github.com/franklinbaldo/conde-incident/actions/runs/43185280933) concluiu **SUCCESS** no head indicado, com **15/15 testes**, download do Git blob e do par TLE com hashes conferidos, replay J2 e ângulo entre planos; as outras **9 verificações herdadas** também foram SUCCESS. Replay JSON preservado como artefato #13928202237. Esta anotação é novo commit documental, portanto o SHA final atualizado requer novo CI. Nenhuma publicação/merge.
