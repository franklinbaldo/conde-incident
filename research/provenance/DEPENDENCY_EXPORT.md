---
type: Guide
title: Cadeias documentais explícitas para Lean e site
description: Contrato de exportação separado das citações históricas congeladas
---

# Dependências documentais, não multiplicação de testemunhas

O arquivo public/data/conde-declared-dependence.json é um **companheiro**
do feed canônico public/data/conde-source-citations.json. Cada vínculo deste
último é localizado pelo par exato snapshot_ref (contém hash do Git blob
da matriz e Cnn#ocorrência) e source_id. O companion acrescenta somente
as arestas explícitas e seus caminhos ancestrais, sem reescrever documentos
históricos nem as 241 ocorrências da matriz cumulativa.

O gerador tools/export_documentary_dependence.py valida previamente o grafo
e compara **byte a byte** o feed canônico vigente com o que deriva da fonte
curada. Se houver diferença, falha, em vez de derivar uma segunda fonte da
verdade. Atualize apenas o companion quando a custódia original não mudou.

As principais cadeias verificadas no corpus do repositório são:

- C01#1 → FBIS → Rádio Tupi, relação de transcrição, não duas testemunhas.
- C198#1 → NTRS → relatório NASA de 15/11/1963, ficha do mesmo documento,
  não instrumento adicional.
- C23#1 → CelesTrak → GFZ e NRC, agregação de séries ambientais,
  não medição orbital do NORAD 528.
- Addendum NARA-BB-CONDE-20261112-01 → telegrama USAIRA → referência a
  O Globo não inspecionado; o caminho documenta a citação, não a matéria.

Os objetos independence_groups apenas deduplicam obras e IDs de ocorrências
por **família conservadora**. Não informam contagem instrumental real, nem
a ausência de aresta indica independência. Todas as contagens de observações
físicas independentes permanecem nulas.

Cada entrada de citation_lineages inclui matrix_line e row_sha256 retirados
diretamente da matriz congelada. A integridade é checada contra o feed
canônico, não apenas pelo Cnn#ocorrência. Os mesmos campos estão no
contract_citation_crosswalk, inclusive para ocorrência UNMAPPED_NOT_CLEARED:
há linha documental, mas não há citação curada nem independência física
certificada. Isso permite que Polvo/site verifiquem o SHA-256 da linha mesmo
sem abrir o feed complementar e bloqueia mistura de versões da matriz
(como a colisão histórica C151 Lean/matriz).

contract_citation_crosswalk oferece ao Polvo e a outras ferramentas uma
junção verificável entre contrato, ocorrência qualificada, ID da fonte e seus
ancestrais declarados. Não há promoção automática para predicados físicos:
os estados dos contratos são preservados. Nenhuma medição, data-hora terminal,
localização de reentrada ou redução de domínio foi inferida por esta exportação.

Para reproduzir e validar:

    python3 -m unittest discover -s tests -p test_documentary_dependence.py -v
    python3 tools/export_documentary_dependence.py --check-site

Após alterar os dados curados, regenere o companion com

    python3 tools/export_documentary_dependence.py --write-site

O workflow dedicado no GitHub Actions verifica o SHA exato da PR.

## CGEO-10: ligação retrospectiva, separada da matriz congelada

A [ponte documental CGEO-10](../../public/data/conde-cgeo10-provenance.json)
é gerada por tools/export_cgeo10_provenance.py, conferindo os **dois
manifestos** independentes de auditoria de arquivos no repositório, que
referenciam o **mesmo ZIP IBGE**, e o contrato jurídico CGEO-09. Ela
identifica a ocorrência complementar
CGEO-10:CONDE-BA:2908606:SHP-2449, com URL oficial, SHA-256 do ZIP,
índice SHP/DBF, hash do registro de bytes e hash da geometria extraída.
Esses hashes possuem **escopos diferentes** e não devem ser igualados.

A cadeia exportada é: ZIP oficial IBGE → método de reconstrução da malha
anterior a 1991 → registro SHP/DBF Conde/BA → afirmação cartográfica
CGEO-10 → *proxy* nominal 1960 → **limite jurídico de 1963 pendente**,
também dependente de CGEO-09 → predicado Lean **condicional não promovido**
→ parâmetro latente de simulação (null). O ZIP de 1960 foi
retrospectivamente confeccionado com polígonos posteriores, não é uma
medição de 1960, nem a fronteira jurídica provada de 08/11/1963.
A consulta ao espelho Stanford/UTexas não acrescenta testemunha
independente. Nem a família documental IBGE nem o procedimento de
reconstrução constituem um novo sensor.

**Não existe ocorrência Cnn adicional na matriz C001–C238**, que
permanece 241 linhas com snapshot imutável. A ponte declara
CONNECTED_PENDING_CALIBRATION, lean_status=NOT_PROMOTED,
simulation_status=CANDIDATE_NOT_ACTIVATED, e quatro condições
faltantes: atos legais datados e alterações até 1963, limite original
georreferenciado com incerteza, compatibilidade de datum/frame/época e
posição independente de um evento. Coordenadas XY nativas
World_Polyconic não são latitude/longitude.

Reprodução offline, sem novos downloads nem alteração do domínio:

    python3 tools/export_cgeo10_provenance.py --check-site
    python3 -m unittest discover -s tests -p test_cgeo10_provenance.py -v

Para alterações justificadas na custódia original, regenere com
--write-site; o workflow documentary-lineage faz verificação
byte-a-byte do contrato publicado no SHA exato da PR.


## Índice de pontes documentais candidatas para Polvo e site

O companion [conde-scientific-bridges.json](../../public/data/conde-scientific-bridges.json)
faz a junção **validada byte a byte** de três feeds existentes: dependências
curadas da matriz, contexto NORAD do Morcego e cartografia retrospectiva CGEO-10.
Em vez de criar observações, registra nove vínculos rastreáveis:
uma ocorrência da transcrição Tupi/FBIS (C01#1), duas citações do **mesmo
trabalho NASA/NTRS** (C197#1 e C198#1), cinco ocorrências MOR-NOR
de **contexto sem rastreamento demonstrado do 528** e uma ocorrência
complementar CGEO-10, fora da matriz original. Preserva row_sha256 e
linha nas três ocorrências Cnn, o source_audit_sha256 dos cinco registros
NORAD e o SHA-256 de cada feed integral na raiz do export.

A exportação transporta afirmação documental -> hipótese -> premissa Lean
pendente -> parâmetro latente do simulador, sem ativação. O catálogo
NASA fornece somente um dia, não instante terminal (valor null);
as notícias de 1963 dos objetos 687/688 e os documentos originais de
**1964** referentes ao objeto 943 são controles negativos, não medições
528. A política de 1961 apenas torna *possível* a troca NASA/NORAD,
sem provar ancestralidade de uma medição particular. A fronteira
jurídica de 1963 permanece NOT_PROMOTED, sem Cnn inventado.

A junção não altera as 241 ocorrências da matriz nem soma sensores.
Zero restrições físicas ativadas e zero novas medições do 528.
A contagem de observações independentes permanece null (desconhecida),
não equivale a zero observado; nenhuma prova Lean nova é reivindicada.

    python3 tools/export_contextual_scientific_bridges.py --check-site
    python3 -m unittest discover -s tests -p test_contextual_scientific_bridges.py -v

Alterações nos arquivos de origem exigem recalcular os três feeds antes
de gerar o índice com --write-site. O workflow documental executa os
testes adversariais e a comparação byte a byte no HEAD da PR.
