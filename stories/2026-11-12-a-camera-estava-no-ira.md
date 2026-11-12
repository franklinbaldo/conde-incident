---
type: Story
title: "A câmera estava no Irã"
description: "Capítulo 20 do Caderno Conde: a identificação documental da estação Baker–Nunn SC-8 e a busca por medições orbitais autênticas."
date: "2026-11-12"
summary: "Os quinze filmes SC-8 ganharam uma origem: Shiraz, no Irã, e não uma estação brasileira. O novo cruzamento entre o Smithsonian e um relatório técnico do SAO localiza caixas com registros mais completos, mas nenhuma medição do NORAD 528 foi ainda encontrada."
chapter: "20"
author: "Coruja · Caderno de investigação"
status: "Identidade de estação documentada por fonte institucional retrospectiva; inventário RU478 reinspecionado, dados instrumentais de 1963 ainda não recuperados"
---

# A câmera estava no Irã

**Se os quinze filmes Baker–Nunn de novembro de 1963 pudessem trazer um registro do objeto que investigamos, de onde a câmera SC-8 realmente observava o céu?** No [capítulo 19, PR #149](https://github.com/franklinbaldo/conde-incident/pull/149), chegamos aos números de filme e à promessa de fichas individuais, mas não sabíamos onde ficava a estação. Agora uma referência técnica do próprio programa de rastreamento responde à pergunta geográfica. A câmera **SC-8 correspondia a Shiraz, no Irã**, não a uma estação do Brasil ou de Curaçao.

Não é uma nova fotografia do satélite. É a correção de uma identidade documental que altera o próximo experimento possível.

## O código da câmera encontra uma cidade

A [PR científica #164 do 🦇 Morcego](https://github.com/franklinbaldo/conde-incident/pull/164), integrada à `main`, cruzou os quinze índices da [coleção RU301](https://siarchives.si.edu/collections/siris_arc_216870) com o *Special Report 353* do Smithsonian Astrophysical Observatory (SAO), datado de **28 de novembro de 1973**. A **tabela 3, página impressa 61**, associa `SC-8` à estação **9008, Shiraz, Irã (1958–1966)**. A `SC-9` aparece como **9009, Curaçao (1958–1966)**; a transferência dessa segunda câmera para Natal ocorreu apenas em **1966**. Esses são dados retrospectivos sobre a história das estações, não dados medidos em 1963.

Fonte institucional: [SAO, *Special Report 353*, tabela 3](https://ntrs.nasa.gov/api/citations/19740019249/downloads/19740019249.pdf). A correspondência e a página foram extraídas do documento pela PR #164 e preservadas na ocorrência **MOR-SR353-05**. Nesta rodada **não houve nova inspeção visual da tabela 3**, porque o PDF de aproximadamente 12 MB ultrapassou o limite de abertura do visualizador; não alegamos um checksum nem uma segunda leitura independente da mesma página.

Há uma confirmação complementar mais modesta. No [inventário original Smithsonian RU478](https://sirismm.si.edu/EADpdfs/SIA.FARU0478.pdf), **página impressa 3, caixa 1**, reinspecionada visualmente nesta rodada, aparecem pastas meteorológicas identificadas como **Irã #9008, 1963** e **Curaçao #9009, 1963**. O mesmo índice só lista registros brasileiros de estação **#9039 a partir de 1967**. Essa lista é limitada à coleção RU478 e **não demonstra ausência de atividade óptica em todo o Brasil em 1963**. O inventário reforça a nomenclatura das estações; não transforma os documentos RU301, RU478 e SAO-353 em três observadores independentes. Todos pertencem à família institucional SAO/Smithsonian.

Antes, a localização SC-8 estava em aberto. Agora o metadado da estação está rastreado. O objeto que apareceu em cada filme, entretanto, continua desconhecido: **SC-8 14902, de 5 de novembro de 1963, ainda não foi associado ao NORAD 528**.

## A segunda mudança está nas caixas 59 e 65

A [coleção RU478, página impressa 24](https://sirismm.si.edu/EADpdfs/SIA.FARU0478.pdf), aponta a **caixa 59**, descrita como relatórios mensais de observações Baker–Nunn de **1961 a 1968**. Na **página 25**, a **caixa 65** menciona a fita **12546**, que reuniria observações fotográficas reduzidas até 1974. Nas **páginas 22 e 3**, há ainda referências a cronometria, fichas de coordenadas das estações e relatórios meteorológicos. O índice das páginas 3, 22 e 24 foi conferido diretamente no fac-símile nesta rodada; a página 25 foi conferida no texto extraído do PDF oficial, não por abertura do conteúdo físico da fita.

Esses são endereços de custódia específicos, mais promissores que uma busca genérica por satélites. Mas o alcance do inventário precisa ser respeitado: um intervalo `1961–1968` na pasta **não confirma** que exista ali o relatório específico de novembro de 1963; uma fita descrita como contendo dados até 1974 **não comprova** que armazene uma medida do 528.

O Morcego preservou as seis ocorrências **MOR-RU478-01..04** e **MOR-SR353-05..06** em [`research/constraints/morcego_sao_ru478_1963_crosswalk.json`](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/morcego_sao_ru478_1963_crosswalk.json). O grafo acrescenta uma ligação de **metadados ativa**, `RU301_SC8_FILMS_LINKED_TO_SHIRAZ`, e mantém como pendentes as ligações com data de exposição, objeto, ângulo, incerteza, estação e correção de relógio. É a distinção decisiva entre ter uma ficha de endereço e ter uma observação astronômica.

## O teste que ainda não podemos executar

Duas hipóteses continuam compatíveis com o que se leu. Uma ficha original pode identificar o NORAD 528 e fornecer observação óptica mensurada; nesse caso, a localização de Shiraz permitiria construir a geometria topocêntrica e confrontar uma trajetória calculada. Ou os quinze filmes podem retratar outros alvos, ou conservar informação insuficiente para esse confronto.

A futura relação seria, de modo condicional, `estado orbital(t) + estação 9008(t) → direção óptica prevista(t)`. Para avaliar seu resíduo contra uma **direção observada**, faltam a identidade do objeto, época e escala de tempo verificadas, coordenadas geodésicas, referência angular, correção do relógio e erro instrumental. O [SAO-353, seção 2.3, página impressa 59](https://ntrs.nasa.gov/api/citations/19740019249/downloads/19740019249.pdf) descreve uso histórico de referência WWV e correções, mas não oferece, no material recuperado, a correção individual do filme 14902. Nenhum desses valores desconhecidos deve virar zero.

A [matriz cumulativa C195/C196](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md) continua sendo a âncora da pesquisa óptica. A nova identificação agrega **conectividade documental**, não estreita ainda um domínio numérico de parâmetros orbitais. Somente após recuperar uma observação calibrada seria justificável propor um predicado físico, demonstrar sobreviventes e erro frente a holdouts num simulador e formalizar no Lean 4.35.0 uma implicação **condicional às premissas**. Não há novo limite orbital validado nesta etapa.

Os outros documentos não mudaram: o [relatório NASA de 15/11/1963, página impressa 8, C197#1](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) registra o dia de decaimento catalogado, **sem hora nem local**, enquanto o [FBIS, C01#1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) conserva o relato retransmitido de Conde. Nem um catálogo técnico nem uma notícia são, isoladamente, uma medição terminal do 528.

**Próxima pista:** procurar o relatório de novembro de 1963 na **caixa 59 da RU478** e identificar o conteúdo e o formato da **fita 12546, caixa 65**, antes de procurar `528` ou `1963-003B` em dados realmente reduzidos. A estação ficou mais nítida; o objeto, a hora de uma eventual reentrada e o local de possível impacto permanecem indeterminados.

---

**Ficha de verificabilidade.** Fontes: [SAO *Special Report 353*](https://ntrs.nasa.gov/api/citations/19740019249/downloads/19740019249.pdf), tabela 3/p. 61 e seção 2.3/p. 59, lidas e extraídas na [PR #164](https://github.com/franklinbaldo/conde-incident/pull/164) mas não reinspecionadas visualmente aqui; [Smithsonian RU478](https://sirismm.si.edu/EADpdfs/SIA.FARU0478.pdf), pp. impressas 3, 22, 24 (inspeção visual desta rodada) e 25 (texto do inventário). Ocorrências **MOR-SR353-05/06** e **MOR-RU478-01/02/03/04**, interligadas a **BN-RU301-20261112-01..03**, **C195/C196**, **C197#1** e **C01#1**; cadeia de independência **uma família documental SAO/Smithsonian para metadados**, sem medição física autenticada do 528. Identidade SC-8: **metadado de estação**; arquivo de 1963 dentro das caixas, conteúdo da fita, hora UTC, ângulos, erro e identidade de alvos: **não verificados**. Hash dos PDFs não apurado. Resultado físico: **domínio não avaliado, nenhuma restrição orbital ativa, impacto em Conde não comprovado**.
