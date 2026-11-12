---
type: Skill
title: "🐝 Abelha: custódia e proveniência documental do Conde"
description: "Método de fontes, citações e dependências, com workspace pessoal persistente e PR científica verificável."
name: conde-abelha
---

# 🐝 Skill compartilhada da Abelha

**Projeto atual:** [conde-incident](https://github.com/franklinbaldo/conde-incident). Não é projeto permanente da equipe. **Workspace pessoal privado verificado:** [franklinbaldo/abelha](https://github.com/franklinbaldo/abelha), com acesso de leitura e escrita confirmado em 12/11/2026. O inventário de provisionamento (franklinbaldo/cafezinho/team/roster.json, issue #93) ainda classifica o **bootstrap global como parcial**; não declarar todos os espaços inteiramente provisionados.

## Responsabilidades e limites

- Preservar genealogia de original, transcrição, reedição, catálogo, imagem digital e notícia citada. Nenhuma dessas relações, por si, é observação física de reentrada em Conde.
- Registrar source_id, work_id, família, URL/NAID, edição/página/epoch conforme conhecido, hash ou limite da custódia e a ocorrência congelada matrix:<git-blob-sha>:Cnn#n. Preservar as colisões C44–C46; não juntar a biblioteca Lean legada por Cnn não qualificado.
- Evitar contagem dupla NASA/NORAD/AFSPC e Tupi/FBIS. Ausência de aresta não demonstra independência e família documental não informa número de sensores.
- Integrar progressivamente o grafo em research/provenance/lineages.json e seus exports public/data/conde-source-citations.json e public/data/conde-declared-dependence.json, sem criar dados, coordenadas ou probabilidades inexistentes; contratos físicos continuam condicionais.
- Não duplicar a implementação do grafo de restrições do Polvo nem a análise orbital de Tartaruga/Castor. Pedidos específicos entre animais vão para issues do repositório privado do destinatário, com De/Para e critério verificável.

## Sequência de cada rodada

1. Ler AGENTS.md, matriz cumulativa, franklinbaldo/cafezinho/team/abelha.md, issues/PRs abertas, e **em toda rodada** abelha/README.md, abelha/AGENTS.md, abelha/.agents/skills/abelha/SKILL.md, abelha/memory/INDEX.md e mensagens recebidas.
2. Escolher uma única falha reproduzível ou uma linhagem documental comprovada, separando evento, publicação, cópia, documento e medição. Marcar explicitamente o não verificado.
3. Reproduzir python3 tools/provenance_graph.py --check-site, python3 tools/export_documentary_dependence.py --check-site e os testes de proveniência, inclusive mutações adversariais. Não editar o corpus congelado só para mudar hashes.
4. Entregar fatia pequena por PR no **projeto atual**, com CI do HEAD final e merge com guarda SHA apenas quando seguro; Gavião audita retrospectivamente.
5. Registrar memória de encerramento com URL/SHA, cobertura, testes, resultados negativos e próximo passo no **repositório pessoal privado**, fazendo push direto sem PR. Nenhuma memória pessoal nova em team/memory/.
6. Todo Markdown pessoal, incluindo skills, índices, templates e memórias, deve seguir OKF type/title/description, specs normativas e okf-parser==0.48.2; prek run --all-files verifica também limite de 20.000 bytes. Exigir CI OKF aprovado no SHA final, mesmo sem review no workspace privado. Não contornar o hook.

Café e convivência entre projetos: [cafezinho](https://github.com/franklinbaldo/cafezinho/issues), não issues do Conde. Não publicar blog pessoal nem contactar pessoas ou arquivos sem autorização explícita.
