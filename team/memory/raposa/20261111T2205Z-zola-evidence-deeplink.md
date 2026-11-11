# OKF | 🦊 Raposa | 2026-11-11 18:05 America/Porto_Velho

## Observação e decisão
- `main`: AGENTS.md e team/raposa.md lidos integralmente; issue #9, PRs #1/#3/#10/#22 e matriz cumulativa C001–C238 da branch científica consultadas.
- A PR #3 mudou o leitor editorial para **Zola 0.22.1**, mantendo React apenas para o laboratório. O leitor React da PR #10 não deve ser mesclado de volta; a solução foi isolada em branch própria sobre a #3.
- Fonte factual: matriz em `research/evidence_matrix_C001-C238_2026-11-11.md` no SHA `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b` (C01–C03, C197–C202). É documento de pesquisa, não observação física.
- Fonte de código: `templates/*.html`, `static/css/site.css`, `src/App.tsx` e `src/components/Navigation.tsx` na PR #3, commit `c84cce85e51252f9e589a851950385aea008e951`.

## Fatia
- HTML editorial acessível com skip link, foco e estilos para telas pequenas; URL canônica e metadados OG individuais por Zola, sem prometer preview individual por hash.
- Fonte/matriz perto de cada capítulo, com classe epistemológica e link permanente para versão verificável; mapa experimental por `/lab/#/map`.
- Estado de aba React agora identificado no fragmento, restaurável via hashchange/Back/Forward; caminho inexistente mostra recusa explícita. Não cria a aba Evidence enquanto a PR #1 não estiver conciliada.
- Testes Node + auditoria do artefato Zola no workflow existente. Nenhum texto de Coruja ou núcleo orbital alterado.

## Grau de verificação e limites
- **VERIFIED por inspeção:** caminhos, código das branches e matriz referenciados acima.
- **PASS observado no HEAD de código** `ca5617647febea91949bd77db795bdeb44eba9c8`, PR #24: [GitHub Actions #43109823563](https://github.com/franklinbaldo/conde-incident/actions/runs/43109823563), job build SUCCESS; lint Bun, 4/4 testes Node de fragmentos, Vite, Zola 0.22.1 check/build e `scripts/check-site.mjs` PASS. Deploy SKIPPED em PR.
- A atualização desta memória cria um novo commit; **CI do SHA final deve ser observado novamente** antes de declarar a PR validada.
- **NOT_VERIFIED:** teclado/leitor de tela em navegador real, mobile real, integração final com aba Evidence da PR #1, deploy Pages, autenticidade de queda/órbita final.
- Próxima dúvida: depois de conciliar a PR #1, o laboratório deve expor uma rota de Evidence `#/research` com teste de Back/Forward e âncora direta do Caderno, sem duplicar a matriz no editorial.
