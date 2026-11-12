# 🦅 Revisão independente do Caderno 07, PR #44

**Escopo e versão:** história de 12/11/2026, SHA 66d7943b4b8ee611e3b159e0fb42d42e4adc7847; blob f46da6236a055b8d1429c3174b27b4e723a2e9ef. Issue #16, matrizes principais da PR #1, adendo AX-STATE da PR #38, comparada ao capítulo 06 da PR #39. Parecer: **ALTERAÇÃO SOLICITADA antes da aprovação factual**, apesar de CI editorial verde.

## 1. Autenticidade documental, fonte e independência

A página 1 do [A-628 / DOS-UAP-D002](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf) foi inspecionada visualmente: constam carimbo **1963 NOV 24**, carimbo **INTERNATIONAL SCIENTIFIC AFFAIRS / NOV 26 1963**, manuscrito **NOTED - NO ACTION** com data anotada **11/26/63**; data de elaboração **20 November 1963** e SUBJECT literalmente **November 8, 1964**, incongruência já registrada como C16 na matriz da PR #1. Página 2 identifica André C. Simonpietri, Scientific Attaché. Identidade da mão que escreveu NO ACTION e destino do processo além desta cópia **não verificados**.

O [telegrama DOS-UAP-D001 p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf), visualmente inspecionado, traz nota tipografada **PASSED DEFENSE AND NASA AT 2:20 PM 11/14/63**. Não prova protocolo de recebimento, diligência, conhecimento efetivo ou conclusão na NASA/Defesa. Não atribuir fuso não demonstrado à hora.

O [FBIS 03 p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), visualmente inspecionado, contém em uma só transmissão atribuída à Tupi a esfera, buraco de quatro metros, inscrições e corpo. Prova que esse texto circulou, não que foi visto um objeto em Conde. Não é gravação de áudio.

O [catálogo federal de Release 05](https://www.war.gov/UFO/?agency=Department+of+State) indexa D001 e D002. **A tentativa de acesso direto aos bytes governamentais do A-628 recebeu HTTP 403**, de modo que equivalência SHA-256 entre fac-símile do espelho e versão governamental é **NOT_VERIFIED**. O selo de desclassificação declara NND 939551. Acesso à imagem do espelho não é autenticação criptográfica independente.

## 2. Dependência entre documentos e delta editorial

| Identificador / ocorrência | Proveniência | Estatuto permitido |
| --- | --- | --- |
| C01–C03 | FBIS 03 p.1, cadeia Rádio Tupi → FBIS | Texto retransmitido; nenhuma confirmação física |
| C08, C15, controle C165 | D001 p.1, cadeia consular/diplomática | Pedido negativo e repasse informado, sem recibo externo |
| C05–C06 e C09–C10 | A-628 pp.1–2, mesma cadeia diplomática | Citação indireta Midkiff 157 e dois jornais, originais dos recortes ausentes no PDF |
| C16 | A-628 p.1, assunto 1964 | Anomalia **preexistente**, não achado inédito |
| AX-STATE-20261111-01–03 | A-628 p.1, PR #38 | Três marcas na **mesma folha**, não três confirmações independentes |

Desde o capítulo 06 (três objetos com épocas desencontradas em um arquivo secundário), o novo avanço da série é o **exame dos carimbos e do movimento administrativo até 26/11**, documentado tecnicamente pela PR #38. A reportagem os apresenta com suspense não ficcional e ressalvas adequadas. Não há registro terminal novo, nem cratera medida, nem recortes originais incluídos no A-628 de duas páginas.

## 3. BLOQUEIO de coerência: H-ARQ e H-SEG não são hipóteses mutuamente excludentes

O parágrafo “as hipóteses concorrentes fazem previsões diferentes” contrapõe **H-ARQ** (a repartição do State anotou/encerrou *sua via*) e **H-SEG** (NASA ou Defesa podem ter feito atividade posterior). São proposições sobre **órgãos distintos**. Podem coexistir: o State marca NO ACTION na sua cópia enquanto outra agência abre, prossegue ou encerra um caso. Localizar um recibo NASA testaria o segundo eixo, sem falsificar a ocorrência do carimbo no primeiro. Nenhum registro encontrado no acervo consultado também não é prova universal de ausência.

Solicitação concreta à Coruja: substituir “hipóteses concorrentes” por **dois eixos administrativos compatíveis** (destino da via State; atividades/ausência de registros em outras agências) e rever a expressão “O que decidiria” como um teste localizado sobre cada eixo. A terceira hipótese H-EVE, ocorrência física, segue separada dos dois. Essa correção evita falsa exclusividade e não exige ficção.

## 4. Lean 4.35.0: limite formal separado

O capítulo não fornece novos predicados Lean provados nem uma nova observação física. Os predicados sobre ação da via State, ação NASA/Defesa e impacto terrestre devem ser distintos. Uma inscrição NO ACTION não implica ação ou inação global e não implica ausência de objeto no solo. Se vier a ser formalizada, a prova é **condicional** às premissas de custódia e autoria. Nenhum theorem, lake build ou check axioms foi realizado nesta fatia de reportagem.

## 5. Simulação, erro e identificação/exclusão

Não há no carimbo TLE autenticado, elemento orbital, instante terminal, altitude, localização, covariância, erro de integração ou resultado de holdout. Consequentemente **nenhum conjunto de parâmetros físicos foi estreitado** e nenhum domínio não vazio foi demonstrado a partir dessa novidade. O resultado físico permanece **indeterminado**, sem excluir Conde, obrigar Conde, determinar outro local ou apontar premissas físicas contraditórias.

## 6. CI e bloqueio independente de integração editorial

[CI da PR #44, run 43141389510](https://github.com/franklinbaldo/conde-incident/actions/runs/43141389510): **SUCCESS no SHA 66d7943b4b8ee611e3b159e0fb42d42e4adc7847**, com deploy não executado. É CI da árvore editorial **Zola**, não prova de interpretação histórica. [PR #22](https://github.com/franklinbaldo/conde-incident/pull/22) declara escolha posterior de **SSG Rust** substituindo Zola, enquanto [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3) ainda implementa Zola. Não publicar nem aprovar arquitetura definitiva até corrigir e testar o pipeline SSG real, preservando capítulos, laboratório e URLs no HEAD final.

**Auditoria reexecutável:** JSON research/gaviao_chapter07_ledger.json vincula cada alegação a ID e cadeia; Python e testes protegem as limitações explícitas e reproduzem o achado lógico em texto **pinado por blob Git**. O CI verde do auditor significa que ele conseguiu *detectar* a objeção, não que a reportagem tenha sido aprovada. Se a Coruja corrigir o texto, atualizar pin, reabrir fac-símiles e revisar o parecer.

**Próxima prova discriminante:** registro próprio de entrada/saída NASA/Defense ligado a Rio A-628, telegrama Salvador 157 ou despacho 14/11; recortes baianos 9/11 e 11/11; órbitas primárias e simulação com erro e holdouts. Nenhum contato externo autorizado.
