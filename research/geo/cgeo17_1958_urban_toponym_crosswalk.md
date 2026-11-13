---
type: Guide
title: "CGEO-17: topônimos urbanos de Conde nas fotos IBGE de 1958"
description: "Ligação temporal e não geométrica entre as ruas/praça fotografadas em 1958 e referências municipais atuais; veda retroprojeção a 1963."
---

# CGEO-17 — Centro de Conde, Bahia: nomes antes das coordenadas

A [custódia original IBGE 1958](ibge_1958_conde_photo_custody.json) (Lontra, [PR #334](https://github.com/franklinbaldo/conde-incident/pull/334)) autentica oito fotografias na *Enciclopédia dos Municípios Brasileiros*, volume XX, páginas impressas 186–188 (PDF 181–183). Não redistribuímos os recortes sem licença esclarecida. **1958 é o ano da publicação, não da tomada de cada fotografia.**

## Quatro âncoras diretamente legendadas

| Fonte de 1958 | Página impressa | O que realmente sabemos |
|---|---:|---|
| Praça Severiano Lima e igreja do **Senhor do Bonfim** | 186 | Dois marcos nomeados na mesma legenda; posição da câmera desconhecida |
| Rua Marechal Floriano | 188 | Rua nomeada na foto, sem comprimento/posição |
| Rua do Carro | 187 | Rua nomeada na foto, sem correspondência atual verificada |
| Prefeitura Municipal | 186 | Edifício municipal fotografado, mas sem endereço ou continuidade do imóvel |

Fonte: [fac-símile IBGE](https://biblioteca.ibge.gov.br/visualizacao/livros/liv27295_20.pdf#page=181), tamanho 72.579.243 bytes, SHA256 `440bd7eaa42c712c89e65111fbebb7b8f77430f76ecff2be0a96d4eacb11a741`, conferido pela Lontra. As fotos **não** comprovam onde ocorreu um evento em 1963.

## Referências posteriores, úteis sem equivalência presumida

- O [portal oficial da Prefeitura](https://www.conde.ba.gov.br/Site/SolicitacaoServico) informa endereço atual **Praça Altamirando Requião, 27, Centro**. Continuidade da instituição não prova continuidade do prédio de 1958.
- Registro comercial **secundário** de [2025](https://cnpj.biz/60456334000104) informa **Rua Marechal Floriano Peixoto, Centro**. A proximidade com a legenda de 1958 “Rua Marechal Floriano” é pista para investigar nomenclatura, **não** correspondência geométrica demonstrada.
- O [Diário Oficial municipal de 30/09/2022](https://www.conde.ba.gov.br/Handler.ashx?c=205&f=diario&m=0&query=836) informa **Praça Doutor Severino Vieira, Centro**. “Severino Vieira” **não é** a mesma grafia que “Severiano Lima”; não presumir mudança de nome ou identidade entre as praças.
- O [catálogo da Matriz de Nossa Senhora do Monte](https://commons.wikimedia.org/wiki/Category:Igreja_Matriz_de_Nossa_Senhora_do_Monte_(Conde)) a situa na **Praça 10 de Agosto**. A igreja do **Senhor do Bonfim** da legenda IBGE é outro titular; não atribuir essa fotografia à Matriz do Monte. Nem esta praça nem Altamirando Requião têm identidade demonstrada com a Praça Severiano Lima.

## Resultado operacional

[Contrato estruturado](cgeo17_1958_urban_toponym_crosswalk.json): âncoras vinculadas aos IDs fotográficos e páginas inspecionadas pela Lontra, endereços atuais com proveniência/época, arestas de candidato e proibições explícitas de colapsar homônimos. O grafo conserva dependência de CGEO-14/15/16 e de `C24`, **sem nova observação independente do objeto**. A geometria histórica, as câmeras, o CRS e o erro posicional ficam nulos, assim como `can_constrain_orbital_reentry=false`.

Próximo teste discriminante: obter planta urbana/aerofoto de aproximadamente 1950–1963 e atos de nomeação de logradouros, além de conferir textualmente a fonte da expressão “centro da cidade”. Em seguida, comparar marcos estáveis em vistas contemporâneas, deixando a data de cada feição separada. Uma correspondência de rua não prova impacto nem sobrevoo.
