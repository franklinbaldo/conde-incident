# 🦅 Parecer independente do Caderno Conde: capítulos 01–04

Data: 11/11/2026. Issue #16. Registro executável: [ledger JSON](./gaviao_editorial_source_audit_2026-11-11.json). Escopo: reportagens #3, #12, #26 e #31 e origem documental #29. A matriz C001–C238 continua na PR #1, não na main. Não atribuímos novo ID C devido às colisões C240/C241 (#27). Os IDs GAV são apenas achados desta revisão, não evidências adicionais de impacto.

## Autenticidade e leitura realmente realizadas

**FBIS 03**: abri a [cópia fac-similar](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) e conferi a página 1. A alegação da esfera, cratera de quatro metros, corpo, vestes e inscrições está NO MESMO registro do relato atribuído à Rádio Tupi. O carimbo 2330 8 NOV 63 W não comprova fuso nem instante da suposta queda. Isso atesta circulação da notícia e não a materialidade de seus detalhes. Cadeia jornalística Tupi→FBIS, uma só.

**NASA**: abri o [Satellite Situation Report de 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), página impressa 8, que equivale ao índice PDF zero-based 9. A página em imagem, rotacionada, mostra 1963 3B / 8 NOV 63 na lista de objetos decaídos. Não informa coordenadas, hora, queda de destroços ou local de impacto. NASA e catálogos NORAD derivados não são automaticamente medições independentes.

**Hale, 29/05/1963**: a [imagem EOP-UAP-D002](https://media.ondisclosure.org/web/official-uap/pursue/release-07/EOP-UAP-D002-Memo_on_Interagency_Coordination_for_the_Recovery_of_Foreign_Materiel-May_1963.pdf) contém selo NND 968063, data, destinatário Welsh, título sobre Frutkin e relato de conversa de 28/05 e reuniões do ano anterior. O termo cover é uma posição atribuída a Frutkin por Hale a respeito da NASA e órgãos de defesa. A página não documenta recolhimento de fragmentos no Brasil e não menciona Conde. A autenticidade da cópia desclassificada foi inspecionada **na imagem disponível**, mas a cadeia de custódia do arquivo institucional não foi reconstituída. Hashes de PDF citados na #31 não foram recalculados por esta revisão.

**Dossiê USG-UAP-D002 de 72 páginas**: a [transcrição OCR pública](https://uapledger.com/documents/release-7-usg-uap-d002) oferece localizador LBJ Library, Charles E. Johnson, caixa 018, e descreve reunião de 06/11, memorando de 15/11 e diretrizes em rascunho. **Não li as páginas 15, 18–19 visualmente**: o original institucional apresentou HTTP 403 e o arquivo espelhado de aproximadamente 38,6 MB excedeu o limite do leitor. Portanto datas específicas deste volume, versões, anotações e ausência de menções no OCR continuam PROVISÓRIAS. O agregador não é testemunha independente.

## Matérias, novidades e revisão de prosa

| PR/capítulo e SHA | Avanço desde o capítulo anterior | Parecer e limite |
| --- | --- | --- |
| #3 / 01, c84cce85e51252f9e589a851950385aea008e951 | Registros distintos NASA dia de decaimento e notícia Tupi/FBIS; antigo exagero de detalhes acrescentados foi corrigido | **Favorável à fatia isolada**. Já possui parecer Gavião no mesmo HEAD. Build Zola e laboratório SUCCESS, run 43105157197; deploy SKIPPED. |
| #12 / 02, e23e1b7ec748171d5f3874e477406188de50ad6b | Modelo experimental posição/velocidade, J2, arrasto condicional e sete testes sintéticos da #5 | **Favorável ao texto com dependência da #5**. Não há validação histórica de trajetória nem redução de latitude/longitude. Build SUCCESS, run 43111796883. |
| #26 / 03, 28d93dda4c78f03ce4b044e9c43f4bab360d782f | Quatro holdouts temporais no NORAD 529, incluindo derrota em 31/08 | **Favorável à apresentação cautelosa, condicionado à #14/#20**. Valores RMSE transcritos da #20, não reexecutados nesta revisão. Build SUCCESS, run 43112714474. |
| #31 / 04, dbcd85794cc680b4ff169cea67fcb81564782d60 | Nova cronologia administrativa de maio comprovada em fac-símile, sem nexo físico com a notícia de novembro | **Favorável ao capítulo com ressalva OCR e upstream #29**. Build SUCCESS, run 43119947594. Conferência das pp. 15/18/19 ainda necessária. |

Os quatro capítulos contêm perguntas e mudanças reais de objeto da investigação, sem inventar personagens, cenas, falas ou fonte independente adicional. A novidade de maio é documental, não orbital. Uma reunião ocorrida antes de 8/11 não poderia ser causada por notícia transmitida depois, **condicional à autenticidade e datas**; isso não exclui providência posterior específica relativa a Conde.

## Quatro juízos separados

**Documentos:** três fac-símiles inspecionados diretamente e um dossiê apenas em OCR; dois documentos que passam por agências americanas não significam duas confirmações de uma suposta queda. A origem do número 528 e o relato material permanecem cadeias diferentes.

**Lean 4.35.0:** as novas fontes administrativas não fornecem desigualdades posicionais, medidas físicas ou parâmetros suficientes para justificar restrição de órbita ou demonstrar Theta não vazio e menor. Nenhuma prova nova compilada nesta revisão. Um teorema de cronologia seria condicional às datas, sem conclusão sobre o solo. ZIP Lean original e axiomas anteriores não reexecutados.

**Numérico:** os valores de RMSE do capítulo 03 provêm da execução relatada na #20: em rev/dia, 0,210299→0,211762; 0,216540→0,214537; 0,223016→0,219896; 0,223237→0,215117. Os quatro conjuntos futuros se sobrepõem; não são quatro experimentos instrumentais independentes. O simulador r/v, SGP4 e holdout físico calibrado NÃO foram executados nesta revisão.

**Conclusões:** permanece indeterminada a ligação entre decaimento e suposto acontecimento. Nem excluir Conde, nem exigi-lo, nem identificar lugar alternativo, hora, coordenadas, probabilidade ou impacto é permitido por estes dados. A data de decaimento NASA não é observação de impacto.

## Garantias automatizadas e bloqueios de integração

O JSON fixa fonte, localização, modo de inspeção, status de hash, dependência e SHA dos capítulos. O script check-editorial-source-audit.mjs recusa promover OCR a fac-símile verificado, duplicar IDs, inflar independência, inverter causalidade temporal ou declarar impacto/posição com estes dados. Dez testes de regressão falham intencionalmente em mutações dos registros. **Esses testes aferem coerência do registro; não verificam verdade histórica nem reproduzem simulação**.

A ordem editorial pendente é #3 → #12 → #26 → #31, com reconciliação científica da #1/#5/#14/#20 e origem #29. O merge poderá alterar HEAD/base: executar CI no SHA conciliado. A configuração Pages e deployment real são NOT_VERIFIED; builds de PR não publicam. Sem merge pelo Gavião, alteração do blog pessoal, contatos com pessoas ou arquivos, rebase ou force-push.

**Próxima dúvida verificável:** a leitura visual das pp. 1/15/18–19 de USG-UAP-D002 confirma as datas e versões exibidas por OCR? Existe ofício, recibo ou rastreio da esfera **especificamente em Conde**? Sem essa ponte, os arquivos de política geral não justificam hipótese física nova.
