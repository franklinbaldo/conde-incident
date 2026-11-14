---
type: Guide
title: Conde — arquitetura de experiência orientada a provas
description: Proposta testável de navegação, superfícies e design system para SSG e laboratório.
---

# Conde: do portal de menus ao dossiê navegável

**Status:** proposta de direção, não migração aprovada. **Responsável:** 🦇 Morcego. **Data:** 2026-11-14.

## Evidência que motiva a mudança

Inspeção do repositório em 14/11: `templates/index.html`, `page.html`, `post.html` e `template.html` repetem nove destinos na navegação; `src/App.tsx` mantém oito rotas hash com cabeçalho e linguagem visual próprios. `pages.yml` une os artefatos SSG Rust 0.0.75 e Vite/React. São **duas superfícies** com um projeto científico, não um defeito automaticamente comprovado.

HTTP 200 do Pages foi confirmado em `/`, `/stories/`, `/cronologia/`, `/evidencias/`, `/hipoteses/`, `/mapa/`, `/simulacoes/`, `/metodo/` e `/lab/` no mesmo dia. Esse exame não demonstra desempenho, contraste computado ou uso com leitor de tela. A auditoria-mãe é [#339](https://github.com/franklinbaldo/conde-incident/issues/339) e o ledger de defeitos é [#495](https://github.com/franklinbaldo/conde-incident/issues/495).

## Tese de produto

A unidade primária de navegação deve ser **uma pergunta histórica verificável**, não a tecnologia de apresentação nem o número de ferramentas. Toda conclusão visível deve permitir percorrer, quando aplicável, `afirmação → registro documental → objeto/época → dependências → hipótese → experimento`. A origem deve ser recuperável no retorno sem perder localização.

### Três camadas, um só caso

1. **Entender**: capa com pergunta, estado documental, três entradas narrativas e um próximo passo. Narrativa é leitura linear; não exibir controles técnicos na primeira dobra.
2. **Verificar**: cronologia de acontecimentos/registro/publicação explicitamente distintos; fichas de afirmação ligadas a fontes e páginas/fragmentos; provas e lacunas; fontes negativas com escopo.
3. **Experimentar**: cenários condicionais e instrumentos no laboratório, cada um acessado por uma pergunta/afirmação específica. Resultados não reclassificam hipótese como fato observado.

A navegação primária proposta é **O caso / Histórias / Fontes / Explorar**. `Explorar` contém mapa, cronologia, hipóteses, simulações e método com links existentes; ferramentas permanecem contextuais. Não remover URLs antigas: criar alias ou redirects/canonicals apenas após teste. Este agrupamento reduz escolhas simultâneas sem esconder o arquivo.

## Arquétipos de páginas e contrato mínimo

| Arquétipo | Tarefa principal | Acima da primeira dobra | Próxima ação | Fonte da verdade |
| --- | --- | --- | --- | --- |
| Capa do caso | entender o problema sem saber órbitas | pergunta, resumo prudente, estado, três caminhos | ler uma história | `Page`, `Story` |
| História | acompanhar a apuração | título, data de publicação, 1 pergunta, trilha do capítulo | abrir afirmação citada | `Story` + IDs |
| Afirmação/ficha | verificar um enunciado | enunciado, classe epistêmica, fonte específica, dependências | ver original/fragmento | `Evidence` / `Source` |
| Cronologia | distinguir quando algo ocorreu de quando foi relatado | filtro por tipo de data + legenda | abrir evento/fonte | `Page`, `Evidence` |
| Hipótese | confrontar alternativas | enunciado condicional, premissas, poder de falsificação | abrir teste ou contraprova | `Hypothesis` / `Constraint` |
| Instrumento | experimentar sem confundir com prova | pergunta, entrada, limites, estado de cálculo | exportar e consultar premissas | `Experiment` |

**Regra transversal:** não inferir grau de certeza numérico de fontes não calibradas. As classes `documentado`, `alegado`, `inferido`, `simulado` e `não resolvido` descrevem o tipo de conhecimento, não uma pontuação estatística. Metadados devem derivar dos OKF canônicos; nenhum rótulo de interface pode superar o conteúdo originário.

## Design system (tokens candidatos, ainda não adotados)

- **Tipografia:** 16–18px corpo editorial; linha de 60–75 caracteres no desktop; títulos fluidos com quebra de palavras longas; tabelas com alternativa listável em telas estreitas.
- **Superfícies:** fundo claro neutro para leitura, tinta escura, acento único para ação, cor secundária para o método; não usar cores como único indicador de status.
- **Espaçamento:** escala 4/8/12/16/24/32/48; margens de 16px no mobile e linha editorial de no máximo 72ch.
- **Componentes:** cabeçalho único, breadcrumbs, cartão de afirmação, trilha fonte→alegação, nota de limites, link para original antes de PDF, saída de simulação com parâmetros visíveis, rodapé de custódia.
- **Acessibilidade:** landmarks, skip link, foco visível, alvos móveis confortáveis, reflow de 320px e 200% de texto, sem perda de informação, alternativas SVG/tabela, `aria-live` apenas para mensagens curtas.

Tokens finais precisam ser medidos contra CSS servido, screenshots e fluxo real, não copiados cegamente desta proposta. [Protótipo estático](casefile-prototype.html): apenas composição e links, sem dados novos nem JS.

## Arquitetura técnica preferida e alternativas

**Preferência sujeita a POC: SSG Rust + ilhas de interação por ferramenta**. OKF é a origem canônica; o build gera HTML e JSON versionados, CSS/tokens compartilhados e manifestos de links. O laboratório continua funcional em React enquanto houver cálculos/reproduções não migrados. Módulos JS nativos ou Rust/WASM só substituem trechos quando a mesma entrada produz resultados equivalentes dentro das tolerâncias científicas.

- **A, híbrido aprimorado:** menor risco de perda científica; mantém duas toolchains e duplica shell se não houver contrato de design compartilhado.
- **B, SSG puro + JS mínimo:** ótimo para narrativa, fontes, índices e mapas estáticos; não presumir que substitui Monte Carlo, slider orbital ou exportação.
- **C, SSG + módulos WASM isolados:** isolamento calculável e sem backend, mas aumenta complexidade de build e pode prejudicar carregamento; usar só mediante benchmark e paridade.

**Decisão adiada:** não eliminar TypeScript/React/`satellite.js` nem alterar formulações físicas com base apenas em estética ou peso presumido de bundle. `express` e `@google/genai` em `package.json` não provam servidor ativo no Pages.

## POC vertical que decide, em vez de reescrever tudo

Escolher uma afirmação **já documentada** com ID canônico (não fabricar um caso), e executar:

1. Capa → história → cartão de afirmação → fac-símile/página ou fonte negativa qualificada.
2. Cartão → hipótese explicitamente condicional → instrumento do laboratório com parâmetros e limites.
3. Instrumento → volta ao cartão/história, com URL compartilhável e foco restaurado.
4. Confirmar conteúdo idêntico nos dois shells e ausência de rótulo epistêmico contraditório.

Medir no mesmo ambiente e mesmo SHA: bytes de JS por rota (comprimidos e brutos), CSS, LCP/CLS/INP quando houver instrumentação válida, navegação em 320/375/768/1440, sem JS, teclado, leitor de tela, zoom nativo 200%, tempo CI, cold cache e offline para conteúdo estático. Declarar `NOT_RUN` para tudo que não tenha sido medido.

## Sequência de implementação, com donos e rollback

1. **Morcego**: validar protótipos e cinco jornadas com leitores; propor tokens/cabeçalho único sem tocar em dados. Este PR contém só direção/protótipo/regressão de contrato.
2. **Raposa**: integrar uma fatia de shell compartilhado primeiro no SSG; manter menu móvel da PR #860 independente e evitar sobreposição.
3. **Abelha/Lagarto**: expor relações derivadas do OKF como manifestos estáticos com IDs e proveniência, sem inventar arestas.
4. **Coruja e Gavião**: examinar a microcópia e a distinção de fato, notícia e hipótese.
5. **Elefante**: avaliar POC A/B/C, métricas e aceitar um ADR; depois planejar migração página por página. Rollback: preservar shell anterior e todos os links `/lab/#/...` até equivalência.

**Gate de adoção:** protótipo revisado; cinco jornadas reproduzidas; roteamento e acessibilidade no Pages; auditoria sem JS; zero perda de ID/URL/fonte; paridade numérica de instrumentos quando houver substituição; CI e publicação no HEAD final. Uma POC reprovada não autoriza retirar o laboratório existente.
