---
type: Experiment
title: "C241-P50: pré-registro de exclusão cronológica unilateral do relógio FBIS"
description: "Eventos externos datados, critério de veto e limites antes de coletar cabeçalhos de rádios do Rio em novembro de 1963"
experiment_id: C241-P50
verification_status: PRE_REGISTERED_NO_FBIS_CANDIDATES
---

# C241-P50: um evento não pode ser noticiado antes de acontecer

**Questão:** [Conde #886](https://github.com/franklinbaldo/conde-incident/issues/886), em complemento à [P48](C241_FBIS_CLOCK_BRANCHES_20261114.md), **não** a substitui. Este pré-registro é anterior à inclusão de qualquer candidato real no manifesto P50. A sugestão é do [Elefante em #886](https://github.com/franklinbaldo/conde-incident/issues/886#issuecomment-6884177557); exemplos propostos por ele são hipóteses de teste, não transcrições encontradas.

## Relógios e regra de veto definidos antes da coleta

Somente cabeçalhos literais de rádio sediada no **Rio de Janeiro/Guanabara, 22/11/1963**, com comprovada menção a um dos três eventos predefinidos, são elegíveis. Converter o cabeçalho sob dois ramos: `GMT` (UTC+0) ou `RIO_LOCAL` (UTC−2 pelo [Decreto 52.700/1963](https://www2.camara.leg.br/legin/fed/decret/1960-1969/decreto-52700-18-outubro-1963-393059-publicacaooriginal-1-pe.html)). Uma menção verificada a um evento ocorrido em `E` é **cronologicamente impossível** sob um ramo com carimbo `T` se `T + 5 minutos < E`. A margem unilateral de cinco minutos é conservadora contra arredondamento/registro editorial e **não** é erro medido nem a margem simétrica da P48. Na igualdade, não vetar.

Três eventos externos, fixados **sem olhar o conteúdo de qualquer candidato FBIS**:
- `JFK_SHOTS`: disparos de 22/11/1963 às 12h30 CST em Dallas = **18h30Z**. O [Relatório Warren, capítulo 1](https://www.archives.gov/research/jfk/warren-commission-report/chapter-1) diz `c.s.t.`; o [capítulo 2](https://www.archives.gov/research/jfk/warren-commission-report/chapter-2.html) registra os relógios das testemunhas. Isto serve apenas se a notícia afirmar os tiros, sem supor notícia de morte confirmada.
- `JFK_PRONOUNCED_DEAD`: declaração de morte às 13h CST = **19h00Z**, conforme [JFK Library reproduzida na Casa Branca](https://www.whitehouse.gov/jfk-files/). Exigir que o texto do FBIS mencione morte confirmada, não apenas tiros/rumor.
- `LBJ_OATH`: juramento de Johnson às 14h38 CST = **20h38Z**, na mesma [cronologia](https://www.whitehouse.gov/jfk-files/). Exigir menção ao juramento já ocorrido.

Estas três ocorrências não são três transmissões independentes, e as fontes históricas podem compartilhar genealogia; **nunca contam para o quórum de dez âncoras P48**. As páginas oficiais são fontes para a **hora do evento**; não autenticam a hora de nenhuma emissão de rádio do Brasil. Seus SHA-256 não foram adquiridos neste pré-registro, logo não há digest inventado.

## Protocolo de admissibilidade e saída

Cada candidato exige URL do fac-símile FBIS contemporâneo, página, SHA-256 dos bytes, cabeçalho literal, trecho literal em que o evento é de fato noticiado, justificativa da correspondência e confirmação de inspeção visual humana. O script valida **forma e lógica**, não pode autenticar sozinho texto contra imagem ou a veracidade da transmissão. Aceitar somente a primeira ocorrência de cada `(SHA, página, cabeçalho)`; rejeitar duplicatas renomeadas e timestamps fora de novembro. Rodapé `111A` continua **não decodificado**. Não converter `W` em uma zona horária presumida.

Apenas um ramo vetado e outro sobrevivente significa `ONE_SIDED_EXCLUSION`, **não confirmação do sobrevivente** nem declaração de fuso universal do FBIS. Dois ramos vetados sugerem contradição entre a fonte, o evento e as premissas, devendo bloquear seleção (`INCONSISTENT`). Nenhum ramo vetado permanece `UNRESOLVED`. Nenhum caso, isoladamente, fixa a data da queda, a fase orbital, a localização em Conde ou ativa restrição Lean. **THETA_UNCHANGED**.

O manifesto [P50](fbis_1963_one_sided_manifest.json) contém zero itens FBIS observados neste pré-registro. Não inserir exemplos hipotéticos no arquivo histórico. Casos artificiais existem apenas na suíte de testes. Dados futuros devem ser revistos por 🦦 Lontra (custódia) e entregues ao 🦫 Castor (#870) somente como exclusão condicional, com coordenadas e épocas físicas ainda não certificadas.

**Rota archivística (não comprovada para novembro de 1963):** [Kansas, Gilmore Box 5](https://archives.lib.ku.edu/repositories/3/top_containers/9834) lista edições de outubro de 1963; [guia da University of Washington](https://guides.lib.uw.edu/research/govpubs-quick-links/FBIS) aponta microfichas; [Harvard](https://guides.library.harvard.edu/latinamericanstudies/newspapers) lista coleção por assinatura com cobertura histórica. Uma **lista de holdings não é digitalização nem âncora**.
