# Protocolo de repositórios pessoais e comunicação entre agentes

**Decisão do proprietário (12/11/2026).** Há duas camadas independentes:

1. **Workspace pessoal privado**: um repositório GitHub por animal, no usuário `franklinbaldo`, com nome em português, minúsculo e sem diacríticos no endereço. Exemplo: `franklinbaldo/polvo`; para 🦅 Gavião, o slug é `gaviao`. O animal mantém nele memórias duráveis OKF, skills, ferramentas, scripts, experiências e organização própria. Pode fazer commits/push diretamente no seu workspace sem PR, aprovação ou auditoria prévia de outros animais. Não precisa vincular cada experiência a uma issue de projeto. A privacidade desejada é **GitHub private**, não um diretório local sem hospedagem.
2. **Repositório de produto/projeto**: `franklinbaldo/conde-incident` (ou outros projetos futuros). Código destinado ao produto vai por PRs pequenas, CI no HEAD e merge do próprio autor quando seguro. O autor anota o número da PR de produto no seu diário privado; não despejar rascunhos pessoais no repositório do produto.

## Agentes e vagas

O cadastro declarativo de animais e slugs fica em [`config/agent-roster.json`](../config/agent-roster.json). Este arquivo registra a **configuração desejada**, não confirma criação de repositórios GitHub. Não usar nomes alternativos, sufixos ou repositórios públicos sem autorização.

Em 12/11/2026, a interface de automações retornou capacidade de **15 tarefas ativas**, com todas as vagas preenchidas (13 animais do Conde + investigação geral + outra rotina pessoal). Cinco animais foram adicionados: 🦎 Lagarto, 🦌 Cervo, 🐝 Abelha, 🦀 Caranguejo, 🦦 Lontra. Não pausar tarefas existentes para abrir uma vaga sem decisão específica do proprietário. Se a capacidade mudar, o Elefante poderá propor animais novos com funções realmente distintas e reavaliar o cadastro.

**Estado de provisionamento:** a tentativa automática de criar os repositórios GitHub privados pelo Jatobá foi bloqueada por configuração de segurança do acesso; portanto **NENHUM novo repositório é declarado criado por esta PR**. Quando provisionados, verificar via GitHub API: dono `franklinbaldo`, `private=true`, `has_issues=true` e acesso efetivo pelas ferramentas dos agentes. Se um nome estiver ocupado por repositório público, interromper e notificar, não converter para público. Não expor tokens, emails pessoais ou segredos em logs.

## Caixa de entrada via GitHub Issues

Se o 🐙 Polvo quiser falar com o 🦫 Castor, abre **uma issue em `franklinbaldo/castor`**, não na issue de implementação do Conde. O destinatário lê issues abertas do próprio repositório em cada sessão, responde, acompanha a demanda e fecha o fio quando resolvido. Outros animais podem abrir issues, comentar ou anexar pequenos relatórios nos workspaces dos colegas, mas não precisam fazer push neles. Formato sugerido:

```markdown
Título: [recado] 🐙 Polvo → 🦫 Castor: aplicar intervalo de RAAN
De: 🐙 Polvo
Para: 🦫 Castor
Projeto/PR: franklinbaldo/conde-incident#<número>
Categoria: colaboração | bloqueio | crítica | evidência | solicitação
Pedido: <ação concreta>
Contexto/fonte: <ID+ocorrência, URL/sha, unidade/erro>
Critério de resposta: <artefato ou decisão esperada>
```

A issue é a **mensagem/coordenação**; se resultar em código de produto, o destinatário cria ou atualiza PR no projeto. Mensagens e memórias pessoais não devem poluir o backlog de implementação; issues de projeto ficam para trabalho do projeto. Registrar ponte (URL da mensagem ↔ issue/PR de produto). Não copiar dados privados para issues públicas.

**Identidade:** automações usando a mesma conta GitHub aparecem como `franklinbaldo`; o campo `De:` é uma identificação operacional declarada, **não autenticação independente de quem escreveu**. Se for necessária autorização técnica separada por agente, criar identidades/apps distintos sob aprovação do proprietário.

## Memória e skills

Estrutura inicial sugerida por workspace:

```text
README.md
AGENTS.md
memory/YYYY-MM-DD/<tema>.md
.agents/skills/conde-<animal>/SKILL.md
tools/
experiments/
.github/ISSUE_TEMPLATE/message.md
.gitignore
```

O animal pode reorganizar livremente esse workspace; a própria skill é sua responsabilidade. Cada sessão termina com pequena memória OKF: fatos verificados, hipóteses, resultado negativo, decisões, links para ações no projeto, SHA, próximo passo. O workspace pessoal deve persistir **entre projetos**; evitar apagar ou reescrever história. Pode usar código, markdown, dados e ferramentas conforme necessário, sem PR na própria casa. Nunca comitar segredos, tokens nem informações pessoais de terceiros, mesmo sendo repo privado.

## Provisionamento e continuidade

Quando o acesso GitHub permitir, provisionar primeiro os nomes do cadastro, exigir **privacidade confirmada**, habilitar issues e bootstrap inicial; verificar individualmente o acesso por GitHub e Jatobá. Só então atualizar `workspace_status` no cadastro e rotinas com os caminhos reais. **Até lá**, os agentes mantêm o trabalho no repositório de projeto, e memórias privadas não devem ser transferidas a um repositório público por conveniência.

Elefante mantém o cadastro de funções, a distribuição de mensagens e a saúde das filas, sem monopolizar issues ou merges. Gavião segue com revisão **retrospectiva do código de projeto integrado**, sem impor revisão aos commits pessoais privados. Cafezinho diário permanece no projeto enquanto a equipe não decidir outro local.

## Bootstrap reproduzível, ainda sem execução

O script [`tools/provision_agent_workspaces.py`](../tools/provision_agent_workspaces.py) foi criado como **procedimento idempotente para um operador autorizado executar**, não como evidência de que os repositórios já existem. Sem argumentos, apenas imprime um plano JSON; **não usa rede, autenticação nem cria repositórios**:

```sh
python3 tools/provision_agent_workspaces.py
```

Quando o bloqueio de provisionamento for resolvido, o operador poderá disponibilizar `GH_TOKEN` ou `GITHUB_TOKEN` por mecanismo de segredo do ambiente e executar explicitamente:

```sh
python3 tools/provision_agent_workspaces.py --apply --confirm-owner franklinbaldo
```

É necessário token com permissão de criar repositórios privados da conta. O script recusa nomes duplicados, repositórios públicos preexistentes, dono divergente, autenticação de outra conta e falta de Issues. Não sobrescreve arquivos já existentes, permitindo reexecutar após interrupções. Cada repositório recebe README, contrato pessoal, sua skill já registrada no Conde, memória, ferramentas, experimentos, .gitignore e template de mensagem via issue. Ele verifica `private=true` e `has_issues=true` depois das gravações. Não remova a observação `PENDING_PROVISIONING` do cadastro antes de verificar os resultados no GitHub.

**Segurança operacional:** nunca forneça tokens pelo chat, em argumentos de CLI ou em arquivos versionados; o script os lê somente do ambiente de execução. O workspace privado continuará pertencendo à conta GitHub do usuário, não a uma identidade criptograficamente separada para cada animal.
