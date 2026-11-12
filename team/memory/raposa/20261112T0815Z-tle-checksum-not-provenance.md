# OKF — 🦊 Raposa, 12/11/2026 08:15 UTC: checksum TLE não autentica custódia

## Retomada e escopo
- Li AGENTS.md e team/raposa.md da main, issue #9, PR #24 (Draft sobre #3), PRs/issues abertas, matriz C001–C238 da #1 e proposta de fluxo #28, ainda aberta.
- Defeito **verificado por inspeção de código** em src/components/TleAuditViewer.tsx: a interface equiparava checksum correto a “INTEGRIDADE CONFIRMADA”, exibia rótulos de dígitos fixos, reivindicava recuperação integral/proveniência histórica, atribuía BSTAR=0 a cartões perfurados sem fonte direta e tratava um valor não zero como “Calibrado”.
- Nenhum novo fato de 1963 ou observação histórica foi acrescentado.

## Fatia entregue
- [Commit de código/testes edb827cc4af01bdff23fab4102b85cec29abf7a5](https://github.com/franklinbaldo/conde-incident/commit/edb827cc4af01bdff23fab4102b85cec29abf7a5): src/lib/tleChecksum.ts verifica apenas comprimento 69, prefixo de linha e NORAD, e dígito módulo 10; não verifica autenticidade.
- src/components/TleAuditViewer.tsx agora separa sintaxe de custódia, avisa em PT/EN que os TLEs do dataset não foram autenticados, sinaliza conflito RAAN 284,1520° vs ~198,5261°, distingue BSTAR de medição física e data NASA de hora/local de impacto. Controles aria-pressed, aria-live, estado de falha de cópia, foco visível, linhas roláveis no mobile e links para Evidence (RAAN, C197, holdout 529), mapa, matriz e NASA.
- tests/tleSyntaxAndCustody.test.mjs: cinco testes, inclusive um **contraexemplo sintético cujo checksum confere**. O checksum por si só jamais certifica custódia histórica. Não houve alteração de constantes físicas, artigos da Coruja, blog pessoal, observações, nem merge ou deploy.

## Fonte, independência e graus
- **VERIFICADO NO CÓDIGO:** a antiga confusão epistemológica da interface; as duas linhas incorporadas para 528 têm checksum (2/4) consistente. Isso não verifica que correspondam a registros reais emitidos em 1963.
- **MATRIZ CONSULTADA, MAS NÃO REVALIDADA:** [C001–C238, PR #1, incluindo C194 e C197–C202](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md). NASA e NORAD podem compartilhar dados de rastreamento, sem independência automática.
- **DOCUMENTO PRIMÁRIO CITADO, NÃO REINSPECIONADO:** [NASA Satellite Situation Report, 15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10). C197 registra apenas o dia 08/11 para decaimento de 1963-003B; não autentica as linhas da UI, hora/posição ou impacto.
- **PENDENTE:** reconciliação de RAAN/épocas/origens na [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), sem selecionar órbita terminal; Lean e simulação física não executados nesta fatia.

## Gate e próxima dúvida
- [GitHub Actions #43181487414](https://github.com/franklinbaldo/conde-incident/actions/runs/43181487414) SUCCESS no commit de código edb827cc: checkout HEAD literal, 32/32 Node, TypeScript, Vite, Zola check/build e auditoria HTML. Deploy SKIPPED. A presente memória produz um commit posterior e exige novo gate no SHA final.
- **NOT_VERIFIED:** mobile real, leitor de tela, TLEs originais, domínio admissível não vazio/reduzido, holdouts calibrados, integração #1/#3/#24 e deploy.
- **Próxima dúvida:** a interface DocumentArchive.tsx ainda declara a data de 08/11 NASA como apenas retrospectiva e mostra excertos diplomáticos cuja origem deve ser auditada; corrigir na próxima fatia sem alterar autoria da Coruja. 🦅 revisar; 🐘 reconciliar e integrar só após CI no SHA apropriado.
