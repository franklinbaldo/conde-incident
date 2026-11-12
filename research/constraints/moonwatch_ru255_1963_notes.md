# 🦇 Moonwatch 1963: brasileiro, reentradas e relatos visuais (RU255)

**Questão falsificável:** além das câmeras Baker–Nunn já inventariadas em RU259, existia em 1963 uma cadeia documental de observadores visuais e relatórios periódicos capaz, em princípio, de conter observações do NORAD 528, independentemente do noticiário de Conde?

**Resultado:** identifiquei no catálogo oficial Smithsonian **Record Unit 255** uma rede Moonwatch com documentação de observadores brasileiros e três séries contemporâneas de interesse. O catálogo foi conferido por fac-símile da própria instituição (PDF 48 páginas), **não** por cópias de artigos modernos. O conteúdo de 1963 dentro das pastas **não foi aberto**; portanto não há ainda observação comprovada do 528. O RU255 é um acervo diferente do RU259, mas ambos integram o Smithsonian, sem independência institucional garantida.

## Ocorrências locais e proveniência

Fonte única: [Smithsonian Institution Archives, RU255, *Moonwatch Division: Records, 1956–1975*, PDF institucional](https://sirismm.si.edu/EADpdfs/SIA.FARU0255.pdf), [registro institucional](https://siarchives.si.edu/collections/siris_arc_216819). Graus: **primária para descrição de acervo**, secundária para qualquer afirmação de atividade em uma noite específica; **não** documentação de sensor de 1963.

| Ocorrência | Localizador direto no catálogo | Evidência arquivística confirmada | O que NÃO prova |
| --- | --- | --- | --- |
| MW-RU255-20261112-01 | Série 3, caixa 10, página impressa 19 | Pastas de equipes/estações em **Bauru** (1958–1963), **Curvelo** (1962–1964), **Paraíba** (1962–1969, 1975), **Porto Alegre** (1962–1963), **São Paulo** (1957–1964, 1967–1968) | Não garante observação, escala operacional em novembro, coordenada exata ou radar |
| MW-RU255-20261112-02 | Série 4, caixa 15, p. 29 | *Monthly re-entry reports*, 1963–1969 | Não garante que o boletim de nov/1963 contenha 528, nem que sua fonte seja independente do NORAD |
| MW-RU255-20261112-03 | Série 8, caixa 21, p. 44 | *Sighting reports*, 1963–1964, da rede VFON de pessoal de voo | Não atesta observação aérea na Bahia, nem matrícula, rota, hora, direção ou objeto |
| MW-RU255-20261112-04 | Série 10, caixa 22, p. 46 | *Bulletin for Visual Observers of Satellites*, 1956–1963; *Moonwatch newsletters*, 1963 | Não garante fascículo de novembro nem citação do 528 |
| MW-RU255-20261112-05 | Série 4, caixa 15, p. 29 | *Instructions for observers*, 1962–1963 | O protocolo de tempo/redução angular ainda não foi lido |

**Identidade de observação:** cinco ocorrências locais, todas descendentes do mesmo PDF/instrumento de descrição Smithsonian, isto é, **uma família documental**, não cinco medições nem cinco confirmações independentes. Nenhum novo C-ID global foi inventado. Conciliação futura com C195/C196 e [PR #114](https://github.com/franklinbaldo/conde-incident/pull/114) antes de importação na matriz definitiva.

## Grafo acumulativo

Arquivo estruturado: [moonwatch_ru255_1963_archival_graph.json](./moonwatch_ru255_1963_archival_graph.json). Contém 10 variáveis e 4 relações documentais/observáveis potenciais, incluindo:
- `moonwatch_528_observation_exists = unknown`
- `moonwatch_528_observation_time_utc = unknown`
- `moonwatch_528_station_location = unknown`
- `moonwatch_528_topocentric_angles = unknown`
- `moonwatch_528_angular_error = unknown`

Operador **condicional futuro**, se surgirem medições com origem autenticada:
`(estado orbital(t), estação geodésica, orientação terrestre, calibração) -> direção topocêntrica prevista(t)`. Só então poderá gerar resíduo angular e predicado de admissibilidade rastreável no Lean. Não imputar valores nulos como zero ou como confirmação de passagem.

A coleção VFON merece genealogia independente: um relato original de piloto é potencialmente distinto de Tupi/FBIS, mas ainda assim poderia decorrer de notícia ou de identificação incorreta. O boletim de reentrada pode copiar rastreamento NORAD/NASA e por isso não se torna nova observação só por aparecer em outro acervo.

## Hipóteses e tentativas de falsificação

**H1:** Moonwatch no Brasil observou o 528 na semana de 8/11/1963. A série de correspondência é compatível, mas não confirma. **Teste:** documento de observação datado com identificação, UTC, estação e direção; falta leitura de pastas.

**H2:** relatório mensal contém posição ou janela horária do decaimento do 528. Não demonstrado. **Teste:** abrir relatório nov/1963, procurar 1963-003B/528 e a proveniência do número; informações compiladas não contam duas vezes.

**H3:** observador de voo registrou reentrada. Não demonstrado. **Teste:** pasta *Sighting reports 1963–1964*, comparar rota/tempo, afastar relato originado da notícia.

### Negativos e obstáculos

Consultas separadas de `Moonwatch newsletter November 1963`, `Moonwatch 1963 Conde Brazil`, `1963-003B optical tracking` e `Moonwatch Paraiba 1963` não localizaram fascículos ou logs primários do 528. O endpoint HTML do catálogo Smithsonian retornou *Request Rejected*; o PDF institucional permaneceu legível e foi conferido nas páginas acima. Tentativa de baixar bytes brutos para SHA256 falhou nesta sessão; **SHA256 do PDF não calculado** (URL e identificador preservados). Metadado de acervo não é observação telescópica.

**Próxima pergunta:** o relatório mensal relativo a novembro/1963 existe na caixa 15 e contém entrada identificável do 1963-003B? Em paralelo, verificar as pastas Moonwatch brasileiras na caixa 10 por data de observação; não contatar instituição sem permissão.

**Progresso:** conectividade documental ampliada, sem nova restrição física ativa nem conclusão sobre queda em Conde. Nenhuma publicação no blog, nem contato com terceiros.
