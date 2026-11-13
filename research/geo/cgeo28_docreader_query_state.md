---
type: Guide
title: "CGEO-28: consulta preenchida no DocReader não comprova busca executada"
description: "Replay de três respostas GET oficiais e uma tentativa POST, sem promover ausência de resultado ou geometria"
---

# CGEO-28: estado inicial do leitor SGB e a armadilha do parâmetro `pesq`

**Questão:** o leitor de aerofotos SGB executa uma busca quando se abre `DocReader.aspx?bib=CPRM&pesq=termo`? A interface [oficial](https://acervo.sgb.gov.br/docreader/Pesquisa/acervo_digital.html) documentada em CGEO-27 oferece quatro coleções, mas a existência de um campo de pesquisa não atesta uma ocorrência arquivística do Projeto PETROBRAS 53 D de 1961, folha Esplanada MI-1850.

Em 13/11/2026, três requisições GET separadas ao **leitor oficial** com `pesq=Esplanada`, `pesq=53%20D` e `pesq=MI%201850` retornaram HTTP 200. Os três HTMLs tinham os termos respectivos no `input#PesquisarTxt`, mas o mesmo `span#PastaTxt` apontando ao **Projeto 1, Rondônia, MI 1392, Porto Velho, 001 a 146**, acompanhado de `/146`. Esses são os dados *da pasta aberta*, não um total de correspondências da pesquisa. As respostas são distintas em SHA256 e comprimento, todos registrados no manifesto.

Também foi feita uma tentativa POST com cookie, campos ocultos ASP.NET, `PesquisarTxt=Esplanada` e `__EVENTTARGET=PesquisarBtn`. Retornou HTTP 200 e conservou a pasta inicial, sem extrair uma lista de resultados identificável. Não foi demonstrada execução bem-sucedida da busca; **não se pode registrar zero ocorrências**. Não se conclui que o projeto esteja ausente do acervo, nem que exista em determinada coleção.

O catálogo DIDOTE 2003 continua apenas citado por transcrição web secundária (CGEO-26). O arquivo [JSON](cgeo28_docreader_query_state.json) registra URL exata, bytes e SHA256 das quatro respostas, mais três **excertos DOM reais** controlados por SHA, sem republicar as páginas completas. O verificador `python3 tools/cgeo28_docreader_query_state.py` faz replay offline dos excertos. Na presença de bytes originais adquiridos, o argumento `--source-dir` verifica integralmente os quatro corpos HTTP e sua relação com os excertos. Sete testes de falsificação impedem transformar interface em resultado, resultado negativo, fotograma datado, ponto ou limite.

**Próximo teste:** busca ASP.NET efetivamente confirmada com identificação de registro e caminho do arquivo; se o leitor não expuser o índice, obter da instituição a ficha ou o fotoíndice original com número do voo/faixa, fotograma, cobertura e data da tomada. Antes disso, `historical_center_geometry=null`, `event_position_1963=null`, `can_constrain_orbital_reentry=false`.
