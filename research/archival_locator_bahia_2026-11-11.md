# Conde 1963 — localização dos recortes baianos e controle de acervos (11/11/2026)

**Escopo:** pesquisa documental independente. Não publicar no blog; não contatar instituições/pessoas. **Sem novo testemunho de 1963 encontrado nesta rodada.** A matriz principal C01–C238 está na pilha da PR #1; IDs `ARC-20261111-*` são locais, **não** números C livres. Conciliar por proveniência antes da integração.

## Pergunta falsificável

Há instituição identificável que declare possuir os dois títulos baianos citados pelo despacho A-628, e a retomada do serviço da Hemeroteca resolve o acesso aos fascículos de 9 e 11 de novembro de 1963?

**Resposta:** sim para existência de **coleções por título** no IGHB, não verificado para a **presença dos fascículos exatos** e não para consulta online daqui. O serviço BN declarou recuperação **gradual** em 23/10/2026, mas a tentativa de leitura do novo endereço devolveu 403. A busca aberta não recuperou os recortes.

## Matriz incremental de evidências (sem criar ID C global)

| ID local | Observação / documento | Proveniência | Independência / grau | Incerteza e conclusão |
|---|---|---|---|---|
| ARC-20261111-01 | Catálogo de períodos do Instituto Geográfico e Histórico da Bahia lista **Diário de Notícias (1875–1980)** e **Jornal da Bahia (1959–1994)** entre seus títulos; também *A Tarde* (1912–continua) e *Estado da Bahia* (1933–1969) | Fonte institucional direta: https://www.ighb.org.br/biblioteca, seção «Espaço da memória periódica» | **Primária para existência declarada de coleção institucional**, não primária para o evento de 1963. Independente dos documentos consulares, mas sem novo testemunho | **Não** comprova guarda de cada edição, integridade ou digitalização. A própria instituição recomenda confirmar os períodos efetivamente disponíveis. |
| ARC-20261111-02 | A Biblioteca Nacional anunciou em **23/10/2026** o restabelecimento da Hemeroteca em https://memoria.bn.gov.br/hdb/periodico.aspx, com recomposição gradual; acesso direto por esta sessão retornou **403 Forbidden** | Comunicado institucional de 23/10/2026: https://www.gov.br/bn/pt-br/central-de-conteudos/noticias/aos-usuarios-da-hemeroteca-digital-brasileira-3 | Primária para estado anunciado do serviço, **não** para conteúdo histórico | Sem acesso ao acervo nessa sessão. Ausência de resultado não é ausência da notícia no jornal. |
| ARC-20261111-03 | O próprio jornal *A Tarde* documentou em **29/01/2010** digitalização das edições de 1912–1955 e plano em execução para 1956–1999, incluindo 1963 | https://atarde.com.br/bahia/bahiasalvador/conteudo-digital-das-paginas-de-a-tarde-esta-disponivel-ao-publico-268589 | Primária para anúncio do projeto de digitalização em 2010; independente da série de jornais do caso | **Não prova** conclusão da fase 1956–1999 nem acesso remoto à edição de novembro de 1963. Possível via alternativa para imprensa independente dos Diários Associados. |
| ARC-20261111-04 | O A-628 de 20/11/1963 identifica precisamente os recortes baianos encaminhados **por mala diplomática em 14/11**: *Diario de Noticias*, **09/11**, e *Jornal da Bahia*, **11/11**, além de citar o telegrama consular **157** do dia 14 | Reprodução do fac-símile histórico: https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf, p. 1. Inspecionadas visualmente p. 1 e 2 nesta rodada; origem declarada Dept. of State/PURSUE, hospedagem espelhada sem comparação de hash oficial | Primária diplomática **para comunicação e envio declarados**, secundária **para as palavras dos jornais** e para o suposto incidente | Os recortes **não estão presentes** nas duas páginas do PDF inspecionado; sua remessa relatada não prova anexação física à cópia sobrevivente. Título inglês *The Airship that wasn't there* **não** restitui com certeza o título original português. |

## Genealogia, refutação tentada e próxima busca

- `Tupi (08/11) → FBIS (09/11)`: evidência de transmissão monitorada; não é testemunho presencial de queda.
- `Diário de Notícias, Salvador (09/11)`: menção via resumo no A-628; não ler como observação independente; em contexto anterior foi apontada relação empresarial Diários Associados com a Tupi, exigindo teste de circulação editorial.
- `Jornal da Bahia, Salvador (11/11)`: relato independente de **visita de repórter** descrito por A-628, mas o texto original e sua autoria não foram lidos. Uma visita independente pode corroborar a **busca negativa local**, não a queda.
- `Jornal do Brasil (09/11)`: já documentado na matriz C77–C83; não duplicar a descoberta.
- `A Tarde (07–12/11)`: alvo concorrente e editorialmente distinto, **nenhuma edição lida nesta rodada**.
- Hipótese H1: os recortes de 09 e 11/11 existem em acervo IGHB naquelas datas. **Teste:** obter registro de fascículo/data/página e fac-símile, não inferir de faixa nominal.
- Hipótese H2: o jornal 11/11 contém relato de testemunho local independente, com nomes/horas. **Teste:** ler texto integral. **Contraprova:** meramente reproduz rumor/Tupi, cita só ausência de testemunha; reduzir suposta independência.
- Hipótese H3: o *Diário de Notícias* precedeu a rádio e levou a notícia a Tupi. **Teste:** comprovar horário de fechamento/edição do periódico e agência intermediária; apenas datas de capa não bastam.
- Hipótese H4: o material meteorológico descrito no *Jornal do Brasil* corresponde a observação de balão real. **Teste:** registro de radiossondagem, série de vento, avistamento nominativo ou recuperação. A fala do secretário e a conjetura consular NÃO são observações físicas independentes.

## Restrições candidatas ao Lean (somente lógicas e condicionais)

1. `ColecaoCobrePeriodo(titulo, a, b)` **não implica** `ExemplarVerificado(titulo, data)`. O catalogo é apenas promessa arquivística de faixa nominal.
2. `DespachoCitaRecorte(titulo, data)` **não implica** `RecorteInspecionado(titulo, data)` nem `QuedaConfirmada`.
3. `FonteRepeteRelato(origem)` **não implica** observação independente.
4. Não foram obtidas observações `(tempo, posição, incerteza)` de trajetória ou impacto. **Domínio orbital admissível: inalterado**; nenhum corte de parâmetros ou probabilidade é autorizado. Delegar prova formal ao Polvo, sem reescrever sua pilha.

## Tentativas e controles negativos

- Busca por original digital de *Diário de Notícias* BA 09/11/1963 e *Jornal da Bahia* 11/11/1963 em índices web: nenhuma página autenticada ou documento íntegro encontrado.
- Reabertura BN anunciada em 23/10/2026 verificada; tentativa do **novo** endereço em 11/11/2026: HTTP 403. Diferente de rejeição do endereço antigo; pode ser restrição ao ambiente de consulta.
- Tentados PDFs do *Correio da Manhã* com nomes de fascículos próximos a 21656, mas sem verificação de edição/data; **não se atribuem** conteúdos ou resultados negativos a essas URLs inferidas.
- Na plataforma de catalogação da Biblioteca Nacional, há item homônimo *Jornal da Bahia* de **1853–1878** (https://acervo.bn.gov.br/sophia_web/acervo/detalhe/1112893), **não** confundir com jornal **1958–1994** do caso.

## Próximos testes com maior valor da informação

1. Consultar catálogos do IGHB e da Biblioteca Pública do Estado da Bahia para *fascículo individual*, não apenas intervalo do título: Diário de Notícias BA 09/11/1963 e Jornal da Bahia 11/11/1963; registrar cota, número de exemplar, páginas, lacunas, reprodução se disponível.
2. Consultar *A Tarde* 08–12/11/1963 via projeto História da Bahia (fase 1956–1999), procurando nomes de repórter, local, balão e declaração da Secretaria, sem atribuir ao periódico material ainda não visto.
3. Recuperar o **telegrama original Salvador n.º 157 (14/11)** e a **mala diplomática de recortes (14/11)**, preferindo trilhas do RG 59 apropriadas a 1963; A-628 p. 1 é apenas resumo/citação.
4. Novo acesso a Hemeroteca após recomposição gradual. Pesquisa por título, período e edição, seguida de captura de páginas, sem usar ausência em OCR como prova de silêncio.

**Sem contato externo, sem alteração de blog e sem mudança em dados orbitais ou formalização Lean nesta fatia.**
