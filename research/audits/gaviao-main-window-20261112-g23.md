---
type: Guide
title: "G23: 15 integrações first-parent, publicidade não atestada e contraprova HTML"
description: "Auditoria científica e editorial SHA-a-SHA de Conde, de c9523ba0 a 07e9a820, com limites de CI, J2 e proveniência."
---

# 🦅 G23: auditoria retrospectiva, primeira família de SHA por merge

**Janela fechada e reproduzível:** [GitHub compare](https://github.com/franklinbaldo/conde-incident/compare/c9523ba0e65dd0002323d3ede1bbb60bc762a618...07e9a820aa769c2e5fc643511badb9c9449f8271) de `c9523ba0e65dd0002323d3ede1bbb60bc762a618` até `07e9a820aa769c2e5fc643511badb9c9449f8271`; [manifesto JSON](./gaviao-main-window-20261112-g23.json) inclui cada SHA completo, pai, PR, HEAD autoral, arquivos e CI. `git rev-list --first-parent --reverse` e `git rev-list --count` retornaram **15 commits**, todos com um pai na cadeia e vinculados a PRs GitHub: **15 squash merges, zero merges com dois pais, zero commits diretos**, sem commits laterais omitidos. A busca de PRs fechadas não integradas não retornou resultados na consulta realizada; isso não prova ausência histórica fora da consulta.

**Ordem do histórico:** #200, #203, #205, #204, #206, #207, #208, #210, #209, #211, #212, #214, #215, #216, #198. A #204, que estava fora do corte G22, foi incluída. O merge #198 introduziu um novo Caderno SSG Rust com arquivos `stories/*.md`, mas o fato editorial de existir página HTTP 200 **não autentica os bytes contra o artefato de deploy**.

## Auditoria separada por eixo

**Documental e fontes:** #203 traz texto de divisa de 1944/1953, sem extrapolação automática a Conde em 1963; #208 preserva malha IBGE 1960 com custódia, não mapa primário daquele ano. #205 oferece 81 linhas pressão/temperatura/altura da *mesma* estação Recife (3 perfis), sem hora real de soltura nem transferência validada a Conde. #210 fixa identidade da célula NASA e #214 conecta política GSFC–NORAD 1962 a um grafo administrativo, não a rastreio NORAD 528 autenticado. #207 amarra identidade de linha/hash no crosswalk, não cria independência entre observações. Os PDFs e originais instrumentais não foram novamente autenticados por download independente nesta rodada.

**Lean, hipóteses e método numérico:** #206 adiciona prioridade circular von Mises ao viés de RAAN, mas nenhum prior externo foi medido. #209 congela J2 antes da avaliação, testa 35 épocas catalográficas tardias e encontra vantagem J2 em 528/529, desvantagem em 527. O corpus é um espelho secundário compartilhado, não um holdout de sensor independente. #211 requer covariância cartesiana 3x3 explícita, sem apresentar uma covariância instrumental original. Essas PRs não provam nova restrição Lean, domínio físico `Θ` não vazio e reduzido, localização/horário nem resultado de impacto. Nenhum `#print axioms` ou compilação Lean 4.35.0 independente foi executado localmente; gates autorais foram consultados pelos HEADs completos.

**Software/editorial:** #200 e #216 deslocam equipe e memórias pessoais ao cafezinho/casas privadas e apagam duplicações antigas; revisão científica continua no projeto. #215 rotula corretamente inversões como simulações. A história #198 distingue NASA (data de decaimento) de FBIS (circulação de relato), menciona dependência de redes jornalísticas e não atribui horário ou coordenadas. Não há confirmação física da esfera, cratera ou conexão causal. Material de redação não é evidência independente.

**Pages/CI:** #212 endurece identificadores de run/attempt/deployment/status, reconsulta a metainformação depois de ler HTTPS e responde `LIVE_CONTENT_PRESENT_UNATTESTED`, não `VERIFIED_PUBLICATION`. O CLI recusa atestação plena sem digest. A falha **G23-F1** herdada da #204 não é de digest: `elements()` ainda encontrava `href="/..."` ou `src="/..."` **dentro do texto de um atributo diferente**, em um `<a>`, `<link>` ou `<script>` real. Teste adversarial demonstra falsa presença de navegação/asset apesar de não haver o atributo próprio; correção substitui regex por varredura dos nomes/valores, com caso positivo. Isso evita confundir controles de HTTPS com prova de publicação.

**Workflows PR consultados:** 14 dos 15 HEADs têm apenas sucessos nos resultados retornados. O HEAD da **#207** tinha **14 SUCCESS + 1 CANCELLED (Publish Conde site)**, não todos verdes. Não classificamos esse estado como 15/15 nem confundimos CI autoral com validação pós-merge. Testes científicos Python locais no clone exato `07e9a820aa`: oito suítes selecionadas, **69/69 PASS** (8+6+10+11+7+13+7+7); os testes JavaScript locais não foram executados no Jatobá por limite RSS de Node e são exigidos no CI da PR, no SHA real.

## Conclusão e próximos testes

**Conde: INDETERMINATE.** Sem coordenada, hora observada, probabilidade, trajetória terminal autenticada ou prova de que qualquer objeto atingiu solo. Pendem rastreios originais de 527/528/529 com época/referencial/incerteza/estação e comparação independente de holdout para restringir `Θ`. Revalidar digest do artefato versus os bytes HTTPS antes de atribuir status de publicação autenticada. Nenhuma modificação no blog pessoal, contato com arquivos ou rebase/force-push.
