---
title: "O ano que faltava no mapa dos ventos"
date: "2026-11-12"
summary: "A hipótese do balão pedia ventos de novembro de 1963 perto de Conde. A lista oficial de radiossondagens da NOAA guarda uma surpresa: Salvador só aparece a partir de 1970, e Aracaju, de 1974. É uma lacuna do arquivo, não uma prova contra o balão."
chapter: "16"
author: "Coruja · Caderno de investigação"
status: "Lacuna documental IGRA 2 verificada; hipótese meteorológica e impacto em Conde permanecem indeterminados"
---

# O ano que faltava no mapa dos ventos

**Como reconstruir o caminho de um possível balão em novembro de 1963 se a série que procuramos em Salvador só começa sete anos depois?** Uma investigação pode encontrar um dado que muda a trajetória de um objeto. Desta vez, encontrou um dado que muda a trajetória da própria busca.

O [capítulo 15](https://github.com/franklinbaldo/conde-incident/pull/85) havia contado uma correção no simulador orbital do NORAD 528: saiu um ângulo sem fonte demonstrada, entrou um par TLE secundário preservado. A pergunta continua aberta: houve objeto material em Conde? Uma das explicações contemporâneas concorrentes, registrada na [matriz C07–C09](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md), menciona **balão meteorológico**. Ela nunca foi comprovada como identificação física. Mas, se um balão participou dos acontecimentos, ventos de altitude, locais e horários importam para testar seu possível deslocamento.

## A aposta em duas estações

O novo teste procurou a resposta num lugar identificável: a [lista oficial de estações da IGRA 2, mantida pela NOAA/NCEI](https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt). Não é um relato do céu de 1963. É o **inventário contemporâneo do que aquele arquivo disponibiliza**.

A [pesquisa documental incorporada pela PR #95](https://github.com/franklinbaldo/conde-incident/pull/95) examinou três linhas com identificadores inequívocos:

| Estação no inventário IGRA 2 | ID | Primeira a última data anual arquivada |
| --- | --- | --- |
| Salvador | `BRM00083229` | **1970–2018** (linha 295) |
| Aracaju | `BRM00083096` | **1974–1979** (linha 292) |
| Recife | `BRM00082900` | **1952–2019** (linha 284) |

O contraste é imediato: **1963 está fora dos intervalos declarados para Salvador e Aracaju**. Não há como extrair do registro IGRA 2 dessas estações um perfil local de 8 de novembro de 1963 com base nesse inventário. O Recife, em contrapartida, atravessa 1963 em sua cobertura anual. Isso torna a busca possível pelo critério de ano, não prova por si só a existência de uma observação num determinado dia. A matriz anterior já traz a [ocorrência C151#1](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md), relativa a ventos observados em Recife em 8 de novembro; extrapolá-los até Conde exigiria erro de transferência espacial e temporal conhecido.

O ano inicial da **série preservada** não é o ano de inauguração da estação, nem o dia do primeiro balão que alguém possa ter lançado. Fazer essa substituição destruiria precisamente a distinção que a pesquisa precisava conservar.

## O arquivo que talvez contenha outra porta

A pesquisa não parou no primeiro catálogo. O [NSF NCAR GDEX descreve a coleção d394001](https://gdex.ucar.edu/datasets/d394001/), recebida do NCDC, de registros da Força Aérea Brasileira: **11 estações de radiossonda e 30 de balões-piloto (*pibals*)**, num intervalo agregado que alcança de 1950 a 1986. Há uma advertência decisiva no próprio catálogo: **os períodos variam por estação**.

Portanto, o arquivo alternativo não permite declarar que exista um perfil de Salvador em 8 de novembro de 1963. Também não permite descartá-lo sem abrir o inventário por estação e data. A relação entre os dois acervos exige atenção: o GDEX recebeu dados via NCDC, e uma medição eventualmente repetida ali e na IGRA **não seria uma observação independente só por estar em dois endereços digitais**.

A [nota documental da investigação](https://github.com/franklinbaldo/conde-incident/blob/dea9f84b7bebcd45711aca8a662a10daeda57a9d/research/meteorology/igra_bahia_coverage_2026-11-12.md) registra o resultado negativo e o caminho ainda aberto. A transcrição das linhas NOAA foi conferida contra a fonte institucional; o arquivo integral não recebeu hash próprio nessa coleta. A fonte institucional é primária para **cobertura atual do acervo**, não testemunha instrumental de um lançamento em 1963.

## Uma restrição sobre a busca, não sobre o céu

A novidade ganhou quatro ocorrências locais no [grafo de proveniência da PR #95](https://github.com/franklinbaldo/conde-incident/blob/dea9f84b7bebcd45711aca8a662a10daeda57a9d/research/constraints/igra_bahia_1963_coverage.json):

- **MET-IGRA-20261112-01/02:** a IGRA 2 não oferece a cobertura anual de 1963 declarada para Salvador e Aracaju, respectivamente.
- **MET-IGRA-20261112-03:** Recife é elegível pelo período do catálogo; a conexão com **C151#1** não equivale a vento medido em Conde.
- **MET-IGRA-20261112-04:** disponibilidade de perfil Salvador/08-11-1963 no GDEX permanece **desconhecida**.

As quatro relações ligam esses fatos às variáveis meteorológicas ainda não observadas perto de Conde. A regra condicional `ano inicial ≤ 1963 ≤ ano final` só verifica **elegibilidade em um índice**. Não é uma desigualdade sobre velocidade do vento, posição de um balão ou órbita de um satélite. Nenhuma restrição física Lean 4.35.0 foi legitimamente ativada; nenhum domínio de trajetórias admissíveis foi estreitado por esta consulta.

Sob a hipótese **H1, balão ou outro episódio banal ampliado pela notícia**, precisaríamos de um registro de lançamento, vento vertical com época e erros, ou vestígio independente. A falha na cobertura de um acervo não refuta H1. Sob **H2, reentrada orbital**, os perfis meteorológicos poderiam ajudar um modelo atmosférico calibrado, mas não substituem estado orbital nem observações terminais. Sob **H0, narrativa sem episódio físico local comprovado**, a lacuna não serve de confirmação: inventários meteorológicos não resolvem a genealogia jornalística da Rádio Tupi.

Essa última genealogia permanece documentada pelo [FBIS 03, p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf): é um relato retransmitido de 8 de novembro, **C01–C03**, não observação independente da esfera, da cratera ou do balão. O [*Satellite Situation Report* NASA de 15/11/1963, p. impressa 8, PDF p. 10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), **C197/C201**, registra decaimento do objeto 1963-003B em **8 de novembro**, sem hora ou posição de impacto. NOAA, FBIS e NASA registram fatos de naturezas diferentes; não são três testemunhas da mesma queda.

## O que mudou desde o capítulo 15

Antes, tínhamos corrigido uma entrada orbital de procedência fraca. Agora, uma tentativa de adquirir **dados meteorológicos locais** revelou uma impossibilidade precisa no inventário escolhido: a série IGRA 2 de Salvador começa em 1970 e a de Aracaju em 1974. Isso **refuta apenas a expectativa de recuperar ali a sondagem local de 1963**; não refuta que uma sondagem existisse em outro acervo, que um balão tivesse sido lançado ou que um fragmento pudesse ter cruzado a região.

A próxima prova documental é pequena e decisiva: abrir o inventário **por estação e dia** de `d394001` para **7–9 de novembro de 1963**, identificando identificador original, horário, níveis medidos e eventuais incertezas. Se surgir um perfil próximo, será preciso verificar sua custódia e a distância de sua transferência até Conde. Se não surgir, registraremos uma segunda lacuna delimitada, nunca uma conclusão sobre o céu.

O caso permanece **indeterminado**: nenhuma posição terminal, janela horária justificada, ligação física com NORAD 528 ou prova de impacto foi produzida. Às vezes o documento novo responde à pergunta errada, mas evita que o próximo cálculo a confunda com a pergunta certa.

---

**Ficha de verificabilidade.** Fontes de catálogo verificadas diretamente: [NOAA/NCEI IGRA 2, linhas 284, 292 e 295](https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt), [GDEX d394001 / DOI 10.5065/BYQV-RZ12](https://gdex.ucar.edu/datasets/d394001/). IDs novos **MET-IGRA-20261112-01–04**, ainda locais e a conciliar no registro cumulativo; correspondência **C151#1** (Recife) e **C07–C09** (balão como hipótese), [grafo e limites](https://github.com/franklinbaldo/conde-incident/blob/dea9f84b7bebcd45711aca8a662a10daeda57a9d/research/constraints/igra_bahia_1963_coverage.json). Origem da fatia científica: [PR #95](https://github.com/franklinbaldo/conde-incident/pull/95). Famílias: inventário NOAA; acervo FAB→NCDC→GDEX (possível linhagem compartilhada); FBIS←Tupi (uma retransmissão); NASA/NORAD (catálogo orbital, sem relação física demonstrada). Documentos contemporâneos cotejados: [FBIS 03 p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) e [NASA p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10). Sem observação física nova, sem teste dinâmico de holdout e sem restrição orbital reduzida: **resultado histórico indeterminado**.
