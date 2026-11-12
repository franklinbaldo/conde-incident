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


## Revisão da genealogia editorial — 12/11/2026 (novo controle de independência)

**Dúvida concreta:** a transmissão da **Rádio Tupi (Rio, 08/11/1963)** e as menções contemporâneas no **Diário de Notícias (Salvador, 09/11/1963)** e em **O Jornal (Rio, 07–12/11/1963)** devem contar como veículos/editorias institucionalmente independentes?

**Resultado:** não. Fontes histórico-institucionais da **Fundação Getulio Vargas (CPDOC)** e da **Biblioteca Nacional** estabelecem vínculo empresarial comum com o grupo **Diários Associados**, ativo antes e durante 1963. Isso é novo **controle comprovado de dependência societária**, não prova de compartilhamento textual, coordenação específica ou falsificação. A Agência Meridional existia como meio de redistribuição de notícias do grupo: **sua participação neste episódio é apenas hipótese a testar**. O *Jornal da Bahia* foi fundado e dirigido por João Falcão, conforme testemunho posterior do próprio fundador, de outra empresa, por isso é prioridade para testar **apuração editorial institucionalmente distinta**. Uma redação do mesmo conglomerado pode verificar fatos autonomamente; controle comum não equivale a cópia automática.

### Acréscimo à matriz incremental (IDs locais; conciliar com C01–C238 sem renumerar)

| ID | Registro diretamente verificado nesta sessão | Fonte, tipo e proveniência | Dependência e incerteza | Efeito científico |
| --- | --- | --- | --- | --- |
| GEN-DA-20261112-01 | A FGV/CPDOC relata aquisição da **Rádio Tupi do Rio em 1934**, do **Diário de Notícias de Salvador em 1943**, e de **O Jornal** em 1924 pelo grupo de Chateaubriand. O PDF discrimina esses veículos e a Agência Meridional em sua lista retrospectiva referente a 1968; o catálogo da BN confirma que o Diário integrou os Associados de 1943 até 1980. | FGV/CPDOC, Marieta de Morais Ferreira, verbete biográfico de Assis Chateaubriand, **páginas físicas PDF 1, 5–6 e 11–12** (facsímile conferido visualmente nas pp. 5, 6, 11 e 12): https://cpdoc.fgv.br/sites/default/files/verbetes/primeira-republica/CHATEAUBRIAND%2C%20Assis.pdf ; Biblioteca Nacional, histórico de Bruno Brasil (10/11/2015): https://bndigital.bn.gov.br/artigos/diario-de-noticias-salvador-1875/ ; catálogo de título BN registro 871386: https://acervo.bn.gov.br/sophia_web/acervo/detalhe/871386 | **Catálogo/historiografia institucional retrospectiva primária para histórico de custódia/afiliação, não observação original de Conde.** A lista de 1968 isoladamente não provaria 1963; as aquisições datadas e o registro contínuo da BN sustentam presença em 1963. Não se atribui identidade de redações ou textos sem fac-símiles de 1963. | **Confirmada dependência corporativa potencial** para Tupi, *Diário* BA, *O Jornal* RJ. Contagem de testemunhos NÃO é incrementada. |
| GEN-DA-20261112-02 | A FGV registra **Agência Meridional**, fundada em 1931 para redistribuir notícias na rede de Chateaubriand e a terceiros; sua existência na organização é identificada em lista retrospectiva de 1968. | Mesmo verbete FGV/CPDOC, passagens da fundação da agência e do elenco de 1968; análise historiográfica complementar UFF, *Agências de Notícias*: https://agenciasdenoticias.uff.br/2024/02/11/meridional/ | **Capacidade estrutural confirmada** de circulação interna; **nenhum despacho Meridional de 07–12/11/1963 sobre Conde foi encontrado**. Há divergências historiográficas sobre alcance da distribuição externa. Não atribuir notícia a essa agência sem carimbo/crédito/arquivo. | **Hipótese concorrente** H-MER: o rumor pode ter passado por agência interna antes da Tupi ou dos jornais. Não confirmado. |
| GEN-DA-20261112-03 | O **Jornal da Bahia** teve fundador/diretor **João Falcão** e começou a circular em 1958, organização distinta dos Associados. | Testemunho retrospectivo do **próprio fundador**, João Falcão, 02/10/2006: https://www.observatoriodaimprensa.com.br/armazem-literario/um-jornal-perseguido-por-acm/ ; Assembléia Legislativa BA (histórico institucional, 12/08/2011): https://www.al.ba.gov.br/midia-center/noticias/10926 | **Depoimento em primeira pessoa primário para sua participação editorial**, mas tardio e sem recorte de 1963; não equivale a testemunho presencial do incidente. Independência *societária* não prova que a reportagem 11/11 usou informação própria; requer cotejo original. | Priorização reforçada do fac-símile de **11/11/1963** para recuperar **autoria, origem editorial e observações próprias**. |
| GEN-DA-20261112-04 | A coleção cronológica 1963 da **Gazeta de Sergipe**, UFS/IHGS, possui índice com **5/11/1963** como último item da página 121–140 de 181; a página seguinte (offset=140) necessária para localizar 8–12/11 retornou **timeout** neste ambiente. | Índice institucional UFS: https://jornaisdesergipe.ufs.br/handle/123456789/24203/browse?etal=-1&null=&offset=120&order=ASC&rpp=20&sort_by=2&type=dateissued ; documentação institucional do projeto: https://bibliotecas.ufs.br/pagina/18277 | Primária para **índice de guarda**, não para conteúdo. Datas posteriores não confirmadas, conteúdo não lido. Teste de nova URL de offset 140 frustrado por timeout/erros. | **Resultado negativo de acesso apenas**; nenhum dado sobre objeto, balão ou rejeição foi produzido. |

### Grafo mínimo de dependência a verificar, sem transformar arestas plausíveis em fatos

- **Afiliação comprovada em 1963:** \`Diários Associados → {Rádio Tupi (Rio), O Jornal (Rio), Diário de Notícias (Salvador)}\`; não equivale a três informantes independentes.
- **Rede técnica existente, uso no caso não demonstrado:** \`Agência Meridional ?→ {Tupi, O Jornal, Diário de Notícias}\`. **\`?→\` indica hipótese**, não proveniência comprovada.
- **Cadeia documental da alegação, já conhecida:** \`Rádio Tupi → FBIS → NASC/Estado\`, sem nova testemunha da queda.
- **Fonte editorial institucionalmente distinta:** \`Jornal da Bahia (João Falcão) → notícia de 11/11 citada no A-628\`. **A apuração exata e dependências do texto permanecem abertas**; o A-628 é citação indireta da reportagem, não leitura do recorte.
- A negativa publicada no **Diário de Notícias** é **internamente interessante**: veículo do mesmo grupo da Tupi citou, segundo A-628, um **desmentido do Ministério da Aeronáutica**. Ainda não sabemos se o jornal entrevistou o Ministério diretamente ou reproduziu comunicado/agência. Não somar negação como testemunho ocular independente.

### Falsificações prioritárias e fluxo Lean

1. **H-MER (agência):** no original de 08–10/11 dos três veículos associados, procurar crédito Meridional/AM, número de despacho, horários de fechamento, datelines, sequência de erros/descrições idênticas. **Refuta o uso da Meridional** um crédito original inequívoco de outra agência/fonte e documentação editorial incompatível; ausência de crédito apenas deixa hipótese aberta.
2. **H-LOCAL (apuração negativa independente):** obter reportagem do *Jornal da Bahia* de 11/11 e telegramas de Conde; buscar nomes, horários, entrevistas e demonstração de observação local. **Não contar falas ministeriais retransmitidas como visita ao local.**
3. **H-SAME (cópia entre títulos associados):** cotejar fotografias/linhas dos recortes de *Diário de Notícias* 09/11, *O Jornal* 07–12/11 e roteiros Rádio Tupi para dependência textual. Sem fac-símile, a propriedade comum é **alerta de correlação**, não resultado do confronto de textos.
4. **Restrição candidata ao Lean 4.35.0, apenas lógica:** \`MesmoGrupo(a,b)\` **não implica** \`MesmoTexto(a,b)\`; \`MesmoGrupo(a,b)\` deve impedir o uso de \`IndependenciaInstitucionalComprovada(a,b)\` para aumentar peso probatório; isso não elimina uma apuração própria documentada em cada redação. **Nenhuma restrição (t, posição, velocidade, erro) nova**: domínio do NORAD 528 e testes físicos/holdouts permanecem inalterados. Formalização reservada aos agentes específicos.

**Resultado da rodada:** confirmou-se **estrutura de circulação potencial e dependência de propriedade**; não houve novo exemplar de 1963, testemunha ocular ou evidência física. **Sem contato externo, sem edição de blog e sem alteração de Lean, simulador ou dados orbitais.**


## 12/11/2026 — duplo sentido de «balão» no telegrama de 14/11

**Pergunta falsificável:** os termos «balão metálico tripulado» e «balão meteorológico», presentes na correspondência de novembro, constituem duas observações verificadas do mesmo objeto? **Resposta:** não. A distinção é lexical e documental; não há duas observações materiais.

### Evidências incrementais, sem renumerar C001–C238

| ID local | Fonte e conteúdo verificado | Natureza / dependência | Resultado e limite |
| --- | --- | --- | --- |
| GEN-DA-20261112-05 | Telegrama DOS-UAP-D001 de 14/11/1963, p.1: registra «LOCAL NEWSPAPER REPORT» sobre «LARGE METAL MANNED BALLOON» supostamente encontrado na «VICINITY SALVADOR» com ocupante morto e cratera de quatro metros. Fac-símile: https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf | Documento diplomático de época **diretamente lido em fac-símile**; porém o conteúdo da notícia é **citação indireta**. Não identifica título, edição, página ou repórter do alegado jornal. Espelho público, sem comparação de hash com original oficial. | **Confirmada** a expressão usada pelo adido e a existência de uma alusão a notícia impressa. **Não confirmada** a existência de um recorte afirmativo distinto nem observação do objeto. Procurar jornal anterior ao telefonema consular de 13/11. |
| GEN-DA-20261112-06 | EOP-UAP-D001/FBIS, captura da Rádio Tupi 08/11, chama a alegação «LARGE METAL SPHERE», localizada «CENTER OF THE CITY», com aberturas semelhantes a janelas e corpo. DOS-UAP-D001 de 14/11 chama o relato recebido de «BALLOON», «VICINITY SALVADOR» e não menciona janelas. Fontes: https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf e DOS-UAP-D001 acima. | **Comparação direta de dois documentos coetâneos**, não de duas testemunhas. O telegrama pode retraduzir ou reformular a cadeia de notícia da rádio; independência jornalística desconhecida. | **Confirmada divergência lexical e locativa no relato**, não transformação física do objeto ou lugar. Teste: cotejar os fascículos, título, crédito e textos antes de concluir filiação. |
| GEN-DA-20261112-07 | No DOS-UAP-D001, p.1, continuidade «PAGE TWO»: «AN OBJECT HAD BEEN SIGHTED ALOFT», tentativamente «WEATHER-TYPE BALLOON», mas «NO REPEAT NO SUCH OBJECT HAD BEEN FOUND AGROUND». No A-628 de 20/11, p.1, a resposta consular citada relata que o secretário de Segurança apenas especulara balão meteorológico, «but no such sighting verified». Fonte A-628: https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf | **Leitura direta de fac-símiles diplomáticos**, mas o A-628 reproduz telegrama consular 157 ainda não recuperado; dependência da mesma apuração telefônica. | **Confirmada a distinção de referentes no texto**: (a) rumor de objeto metálico tripulado supostamente caído e (b) notícia não verificada de algo no ar, classificado provisoriamente como balão de sondagem. Não foi verificado nenhum avistamento independente, lançamento ou recuperação. |

### Hipóteses rivais e critérios de falsificação

- **H-A, único rumor republicado:** a referência a jornal não identificado no telegrama pode ser recontagem do mesmo rumor da Tupi, com «sphere» retraduzido para «manned balloon». Um original citando Tupi ou repetindo ordem de pormenores favoreceria dependência, mas não excluiria apuração adicional.
- **H-B, relato jornalístico distinto:** um jornal baiano ou carioca publicou narrativa afirmativa diferente antes de 13/11. Testar pela página original, data da edição, horário de fechamento, crédito de agência, nomes e pormenores ausentes da Tupi; a mera descoberta de uma segunda página não confirmaria o impacto.
- **H-C, suposto evento atmosférico separado:** o avistamento aéreo mencionado em DOS-UAP-D001 pode ter origem diferente do rumor do objeto caído. Testar por testemunha identificada ou relatório contemporâneo de radiossondagem. O A-628 já ressalva não verificação do avistamento; portanto não existe base documental para igualá-los.

**Grafo provisório:** origem desconhecida → Tupi 08/11 → FBIS; fonte impressa não identificada (talvez dependente da Tupi) → referência de Simonpietri 14/11; avistamento aéreo alegado mas não verificado → conjectura de balão meteorológico → resposta consular resumida no A-628. **Não criar setas comprovadas** entre a fonte impressa e a Tupi ou entre os dois «balões».

### Busca e bloqueios

Consultados indexadores web com expressões exatas inglesas do telegrama e variantes portuguesas, associados a Conde, Salvador e novembro de 1963. Retornaram majoritariamente reproduções modernas da mesma liberação documental; **nenhum jornal original novo foi recuperado**. O portal UFBA de arquivos (https://www.arquivos.ufba.br/) indica coleções de recortes digitais, mas o alcance de 1963/Conde não foi demonstrado e a consulta direta sofreu timeout. As URLs da liberação oficial retornaram HTTP 403; os documentos foram inspecionados visualmente no espelho acima, **sem conferência de integridade por hash contra a matriz oficial**.

### Consequência científica

Restrições **lógicas candidatas** a eventual avaliação formal, sem substituir as atividades do agente Lean: citar jornal em telegrama não implica inspeção do jornal; alegar objeto metálico no solo não implica que seja o objeto incerto no ar; relato consular não verificado não constitui observação física. **Sem mudança do domínio de parâmetros do NORAD 528**, sem hora/local de reentrada nem trajetória terminal medida. A documentação NASA de 15/11 registra somente a data 08/11.

**Próximo alvo prioritário:** identificar a qual jornal Simonpietri se refere por «LOCAL NEWSPAPER REPORT», cotejando os originais de Jornal do Brasil 09/11, O Jornal 07–12/11, Diário de Notícias BA 09/11, Jornal da Bahia BA 11/11 e o telegrama Salvador 157 com os recortes do malote. Nenhum contato externo, alteração de blog, Lean ou simulador.


## 12/11/2026 — horário legal de 1963 e a ambiguidade do cabeçalho FBIS

**Pergunta concreta:** a marca «2330 8 NOV 63» da Rádio Tupi no FBIS significa necessariamente **23h30 no Rio de Janeiro (UTC−3)**, e a mesma hora em Conde? **Resposta: NÃO.** O Rio (Guanabara) estava em horário especial de verão em 08/11/1963; Bahia não estava. Além disso, o documento FBIS não declara expressamente a convenção (GMT ou horário local) aplicada a «2330». Qualquer hora absoluta antes de resolver essa ambiguidade será hipótese, não medição.

### Evidência incremental com IDs locais, sem colisão com C001–C238

| ID | Documento primário / observação | Proveniência e independência | Resultado e incerteza |
| --- | --- | --- | --- |
| GEN-DA-20261112-08 | **Decreto nº 52.700, de 18/10/1963**, art. 1º: desde 00h de 23/10/1963, relógios adiantados **60 minutos** apenas em São Paulo, Rio de Janeiro, Guanabara, Minas Gerais e Espírito Santo; **Bahia não consta**. Edição da Câmara registra DOU 21/10/1963, p. 8845. | Documento normativo federal **primário diretamente lido**, independente de Tupi/FBIS/DOS: https://www2.camara.leg.br/legin/fed/decret/1960-1969/decreto-52700-18-outubro-1963-393059-publicacaooriginal-1-pe.html . Ver também índice histórico do Observatório Nacional: https://www.gov.br/observatorio/pt-br/assuntos/areas-de-atuacao/tempo-e-frequencia/horario-de-verao | **Confirmado:** em 08/11, Rio/Guanabara (UTC−2 na base histórica IANA) estava uma hora adiantado sobre Bahia (UTC−3). É incorreto aplicar Rio UTC−3 à data. O texto digital do decreto contém inconsistência de mês no fecho («18 de maio»), mas o título, art. 1º e publicação oficial distinguem a norma de outubro. |
| GEN-DA-20261112-09 | **Decreto nº 53.071, de 03/12/1963**, art. 1º: estendeu a hora de verão a todo o território nacional **somente a partir de 09/12/1963**. | Documento normativo **primário**, Câmara, DOU 04/12/1963 p. 10162: https://www2.camara.leg.br/legin/fed/decret/1960-1969/decreto-53071-3-dezembro-1963-393258-publicacaooriginal-1-pe.html | **Confirmado:** a extensão nacional em dezembro não pode ser aplicada retrospectivamente a Conde em 08/11. |
| GEN-DA-20261112-10 | Fac-símile **EOP-UAP-D001**, p. 1, visualmente inspecionado: «RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 2330 8 NOV 63 W»; outra marca «9 NOV 111A RWS/GY». Não há indicação literal «GMT», «UTC» ou «local». | **Fonte contemporânea primária para a marca FBIS**, porém secundária para a emissão e alegação do incidente; deriva da Rádio Tupi: https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf . Hospedagem espelhada, integridade contra arquivo oficial não testada. | **Confirmado** apenas o teor do cabeçalho; **não resolvido** o fuso de «2330» ou a semântica temporal de «111A». É incorreto afirmar 23h30 local ou UTC sem fonte sobre a convenção do FBIS. |

### Reconstrução condicional e falsificação

Se **2330 do FBIS é UTC/GMT**, a hora local correspondente seria **21h30 no Rio** e **20h30 em Conde**, ambas em 08/11/1963. Se **2330 é a hora local da estação carioca**, corresponde a **01h30 UTC de 09/11** e **22h30 em Conde no dia 08/11**. Essas são **alternativas hipotéticas**, não dois horários observados.

Conversão reprodutível pela base IANA: Python datetime + zoneinfo, data 1963-11-08, zonas America/Sao_Paulo e America/Bahia: os respectivos deslocamentos são −02:00 e −03:00. O dispositivo legal de 1963 é a verificação histórica primária. A marca FBIS não fornece por si mesma um timestamp UTC.

**Teste de refutação pendente:** localizar manual editorial FBIS de 1962–1964, ou exemplares que declarem explicitamente a zona das horas de transmissão. Buscas por instruções de horário dos boletins FBIS nesta sessão não recuperaram norma operacional aplicável. A seguir confrontar hora de fechamento dos jornais de 09/11; sem isso, precedência entre Tupi e impressos dentro de 08–09/11 é incerta.

**Restrição lógica candidata ao Lean (não implementar nesta PR):** os dois deslocamentos legais são premissas documentadas condicionais, mas um número de hora em cabeçalho FBIS não implica instante universal sem convenção de fuso. **Não transformar** essas horas de transmissão em hora de reentrada/impacto. Não surgiu dado físico de órbita, de cratera ou de balão. **Domínio NORAD 528, simulador e holdouts inalterados.** Sem contatos ou alterações no blog.
