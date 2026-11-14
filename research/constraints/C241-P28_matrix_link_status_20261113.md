---
type: Guide
title: 'C241-P28: classificação integral das 241 ocorrências, sem falsa cobertura'
description: 'Inventário por ocorrência, conciliando citações curadas, dependências documentais e o índice SSG do Conde.'
---

# C241-P28 · Qual relacionamento existe para cada ocorrência histórica?

**Pergunta verificável:** as 241 ocorrências da matriz congelada estão representadas no inventário, distinguindo *citação curada* de *dependência científica documental* sem chamar ambas de observações independentes?

**Resposta reprodutível:** `tools/export_matrix_link_status.py --check-site` reconstrói os dois feeds científicos, valida os *bytes* dos shards do índice SSG contra o gerador independente e produz `public/data/conde-matrix-link-status.json`.

| Classe documental nos dois feeds auditados | Ocorrências |
| --- | ---: |
| Citação curada **e** dependência documental | 2: C151#1, C179#1 |
| Citação curada, sem dependência nesses dois feeds | 26 |
| Dependência documental, **não** citação curada do índice SSG | 2: C227#1, C228#1 |
| Sem relação qualificada **nesses dois feeds** | 211 |
| **Total único** | **241** |

O índice SSG possui 28 ocorrências com citações curadas e **213 sem citação curada**. Portanto, C227#1/C228#1 aparecem no conjunto de itens não curados do índice, embora possuam ligações documentais válidas no grafo científico. **Não remover esses dois da lista de lacunas de citações.** A auditoria oferece aos futuros consumidores ambas as dimensões, sem igualá-las. Outras pontes do projeto não estão abrangidas por este cruzamento; 211 não significa 211 evidências historicamente ausentes.

**Fonte de identidade:** blob Git `a7978c3a75a153b16ab70118a92c434bba674cb7`, `Cnn#ocorrência`, sem colapsar C44–C46. Fonte de ligações: `conde-source-citations.json` e `conde-observable-dependency-links.json`. Fonte dos estados do índice: shards reais gerados por `export_ssg_evidence_index.py`. Todos são reconstruídos e comparados antes da exportação; uma consulta textual solta não promove nenhum vínculo. C151/C179 aparecem em ambos os feeds, não como dois sensores independentes.

**Falsificações automatizadas:** índices truncados/extra, rótulos falsamente curados, vínculos por Cnn sem snapshot, colisão de ocorrências, datas de sensor/covariâncias inventadas, ativações e 50 contextos não qualificados artificialmente inseridos. A auditoria conserva o total e falha fechada.

**Efeito físico e Lean:** `delta_Θ=0`; nenhum evento instrumental, órbita, localização ou instante de queda é provado. A contribuição é uma interface de verificação entre evidência, grafo e consumidores futuros de Lean. **Não** acrescentar teoremas Lean sobre ausência documental ou índices.
