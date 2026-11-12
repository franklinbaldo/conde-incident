# 🦇 Baker–Nunn RU301: filmes datados próximos à notícia de Conde (novembro/1963)

## Pergunta e método

Havia **identificadores originais de fotografias instrumentais** numa fonte de arquivo próxima a 8/11/1963, em vez de somente nomes de pastas? Pesquisei diretamente o **Smithsonian Institution Archives, Record Unit 301: Baker-Nunn Films, 1955–1969**, um conjunto distinto das unidades RU255/RU259 já registradas no projeto.

**Fonte primária institucional para a descrição do acervo, não para a órbita:** [PDF oficial EAD SIA.FARU0301](https://sirismm.si.edu/EADpdfs/SIA.FARU0301.pdf), [catálogo institucional RU301](https://siarchives.si.edu/collections/siris_arc_216870). Fac-símile visualmente verificado em 12/11/2026 nas páginas PDF **2, 7 e 35** (impressas 1, 6 e 34). O catálogo afirma que a coleção contém filmes Baker–Nunn selecionados por estação e ano, acompanhados de fichas de dados. **Não há razão para presumir cobertura exaustiva de cada dia ou de todos os satélites.**

## Três ocorrências arquivísticas novas

| ID provisório | Endereço interno | O que foi efetivamente visto |
| --- | --- | --- |
| `BN-RU301-20261112-01` | PDF p. 2, impressa 1 | Descrição institucional das películas Baker–Nunn e suas **fichas de dados individuais** |
| `BN-RU301-20261112-02` | Caixa 2, PDF p. 7, impressa 6 | Dez entradas da estação codificada **SC-8**, 1–5/11/1963: n.º 14881, 14882, 14883, 14886, 14887, 14892, 14894, 14896, 14897, 14902 |
| `BN-RU301-20261112-03` | Caixa 17, PDF p. 35, impressa 34 | Mais cinco entradas SC-8: n.º 14884, 14885, 14898, 14899 e 14900 |

O inventário público fornece **15 identificadores de filmes na janela 1–5/11/1963**. É uma novidade instrumental concreta: o próximo passo não é só procurar um relatório genérico, mas localizar a **ficha associada a cada número de observação** e a correspondência **SC-8 ↔ estação física**, depois aferir objeto, UTC, dados de direção e erros. Esses são identificadores de registros de acervo, **não números NORAD**, e o inventário não identifica alvo.

**Resultado negativo delimitado:** não há entrada explicitamente datada de 8/11/1963 no *inventário consultado*. Isso **não significa** que não ocorreram observações naquela noite em SC-8, nas outras estações ou no sistema NORAD. Uma seleção de filmes não representa o log completo. Nenhuma ficha ou película física foi aberta nesta rodada. O acesso à página de catálogo permite localizar, mas não expõe as medições para download.

**Custódia e dependência:** RU301 é conjunto institucional próprio, mas pertence à mesma organização SAO dos instrumentos RU255/RU259. Três ocorrências no mesmo catálogo não são três testemunhas independentes; as 15 entradas tampouco comprovam 15 imagens de NORAD 528. O PDF oficial teve o texto pesquisável e as páginas indicadas renderizadas; uma tentativa separada de baixar os bytes para SHA256 falhou por DNS neste ambiente, por isso `sha256=null` é explícito no contrato JSON. O SHA do **arquivo Git** pode ser auditado pelo GitHub depois do commit, não confundido com SHA256 do PDF externo.

## Conectividade cumulativa sem inventar restrições

O [grafo documental RU301](./baker_nunn_ru301_1963_film_index.json) registra 15 IDs `RU301:SC8:{n}`, datas de **catálogo**, variáveis latentes de estação, identificação do objeto, hora da exposição, enquadramento e erro angular. Três arestas preservam o caminho `filme indexado → ficha original → observação específica → operador angular`, com status `CONNECTED_PENDING_AUTHENTIC_528_MEASUREMENT`.

Predição condicional para o futuro, se uma ficha realmente identificar o 528:

`(estado_528(t), geodésia_SC8, orientação_Terra(t), UTC_exposição, calibração) → direção_topocêntrica_prevista`

Apenas uma direção **medida** com tolerância justificável pode gerar resíduo e restrição no domínio do 528. A data de inventário, sem hora ou satélite, não fornece passagem, local de impacto ou estreitamento físico. Este trabalho preserva as conexões para as próximas observações; **não é trabalho formal Lean** e não duplica a custódia TLE da Tartaruga.

## Hipóteses rivais e tentativa de falsificação

**H1:** alguma ficha das quinze contém 1963-003B/NORAD 528. Continua sem teste por falta do item original. Inspecionar alvo e hora na ficha é decisivo.

**H2:** não há observações de 528 em 8/11 porque RU301 não lista filme desse dia. **Rejeitada como inferência válida:** o catálogo cobre uma amostra selecionada, não o censo completo. Não se conclui ausência de observação.

**H3:** a datação/calibração de SC-8 pode servir de referência para outros registros óticos históricos. Continua condicional à leitura de ao menos uma ficha de dados e da documentação do identificador de estação.

**Prioridade seguinte:** pesquisar índices públicos de fichas SC-8 **14902** e vizinhas; mapear SC-8 a uma estação com fonte primária; procurar logs completos de 6–9/11 em RU259/RU263 sem atribuir fotos anteriores a 528.

**Restrições de trabalho:** nenhum documento do blog alterado, nenhuma instituição ou pessoa contatada; nenhuma coordenada, probabilidade ou sensor inventado. Não há redução numérica ainda avaliável, mas 15 relações de filme para observáveis potenciais permanecem acessíveis e testáveis.
