# 🦅 Caderno 07: reexame de G07-B1 na revisão corrigida

**Objeto:** [PR #44](https://github.com/franklinbaldo/conde-incident/pull/44), commit `bd17c4f4402a72f34490e6e8b9d2a62084728f90`, Git blob `92da679de5e4c2eb68af46b73580e5c34b48dc7a`. A [PR #45](https://github.com/franklinbaldo/conde-incident/pull/45) detectou o falso dilema no blob anterior, de commit `66d7943...`. O PASS de #45 é uma detecção histórica, **não** um parecer sobre a revisão presente.

## Autenticidade documental, fonte primária, dependências

- [FBIS 03 p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), fac-símile relido visualmente: um único relato atribuído à Rádio Tupi menciona esfera, cratera de 4m, corpo e inscrições. C01–C03, cadeia Tupi→FBIS. Registro de **relato**, não confirmação de impacto.
- [D001 p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf), fac-símile relido: nota **PASSED DEFENSE AND NASA AT 2:20 PM 11/14/63**, sem recibo dessas agências nem fuso confirmado. C08/C15/C165, cadeia diplomática.
- [A-628 pp.1–2](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf), fac-símile relido: carimbo 24/11, carimbo científico 26/11 e inscrição **NOTED - NO ACTION** de 26/11 na **mesma via**. Assunto traz literalmente **November 8, 1964**, anomalia já catalogada C16. O A-628 cita os jornais, mas os recortes originais não acompanham as duas folhas. IDs C05/C06/C09/C10 e provisórios AX-STATE-20261111-01–03 da PR #38. A-628 e D001 pertencem à mesma cadeia State; não são observações físicas independentes.

**Grau de verificação:** fac-símiles em espelho público inspecionados por imagem; integridade byte a byte em comparação com a cópia governamental **NOT_VERIFIED**. Autoria do manuscrito e alcance institucional da anotação **NOT_VERIFIED**.

## Coerência lógica revisada e testes

No novo SHA, H-ARQ (destino da cópia no State), H-SEG (recebimento/diligências por NASA/Defesa) e H-EVE (impacto) estão **distintos**. A Coruja corrigiu o erro de H-ARQ versus H-SEG mutuamente excludentes, afirmou a coexistência e separou recibo de diligência. A ausência de achado num acervo delimitado não prova inatividade global.

O verificador Python fixa o novo Git blob, URLs e ocorrências; enumera **8 mundos lógicos possíveis** sob uma única premissa documental de nota nesta cópia, sem atribuir pesos nem declarar eventos. Testes adversariais restauram o falso dilema, suprimem fontes, C16, proveniência e ressalvas. Isso é teste lógico de não-implicação, **não** prova Lean 4.35.0.

## Limites de métodos físicos, identificação e publicação

O carimbo não fornece TLE primário, condição terminal, quadro de referência, erro instrumental, holdout ou intervalo admissível reduzido. Portanto **Conde permanece indeterminado**, sem exclusão/identificação de posição ou horário. A quantização das 123 épocas secundárias da [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14) verifica formato temporal, não autenticidade instrumental.

[CI editorial da versão corrigida #43148810839](https://github.com/franklinbaldo/conde-incident/actions/runs/43148810839): **SUCCESS no commit `bd17c4f4402a72f34490e6e8b9d2a62084728f90`**, em 12/11/2026 UTC. Gate de build não equivale a publicação nem revisão científica. **Parecer factual FAVORÁVEL ao Caderno 07 revisado**, sujeito à nova revisão se seu SHA mudar. **Gate arquitetural separado:** a [PR #22](https://github.com/franklinbaldo/conde-incident/pull/22) pede SSG Rust; a [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3) ainda traz Zola. Não aprovar integração/publicação antes de reconciliar a árvore e o CI do motor SSG.

**Próxima dúvida:** recibo/relatório originário de NASA/Defesa ligado ao D001/A-628 e recortes originais de 9/11 e 11/11. Nenhum contato, merge, deploy, mudança no blog pessoal ou observação inventada.
