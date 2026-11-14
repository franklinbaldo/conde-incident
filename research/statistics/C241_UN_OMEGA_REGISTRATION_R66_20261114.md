---
type: Experiment
title: C241 R66 registro ONU Omega 1962, papéis e limite de data
description: Triagem de transcrições da ONU sem inferir número NORAD ou hora terminal
---

# R66: Omega na ONU, distinção entre objeto e fragmentos

**Nova pista documental (não observação instrumental):** na compilação do registro das Nações Unidas por Jonathan McDowell, a Tabela A1 aponta **1962 Omega 1** (EUA, lançamento 18/06/1962), período publicado 92,4 minutos, perigeu 367 km, apogeu 408 km e inclinação 82,1°. A Tabela B1 classifica **1962 Omega 2** e **Omega 3** como *fragmentos*, não como o objeto principal. A Tabela A3 apresenta para Omega 1 o cabeçalho **“Decay before”**, data **31/10/1963** e documento **A/AC.105/INF.054**. A inscrição de 1962 está associada a **A/AC.105/INF.013**.

Fontes compiladas: [Tabela A1](https://planet4589.org/space/un/un_taba.html), [Tabela B1](https://planet4589.org/space/un/un_tabb1.html), [Tabela A3](https://planet4589.org/space/un/un_taba3.html). **O fac-símile original dos dois documentos ONU ainda não foi recuperado nesta rodada.** Logo, esses elementos são uma transcrição secundária de registro estatal, sem SHA-256 do documento original e sem autonomia instrumental demonstrada.

**Contraste que importa:** o boletim [NASA de 15/12/1963, página PDF 17](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=17) lista **OMEGA 1** com decaimento impresso **29–30/10/1963**, sem NORAD. As datas impressas antecedem nominalmente o limite de **31/10**, de modo que as transcrições são *compatíveis enquanto rótulos de calendário*. Não são duas horas medidas nem duas fontes instrumentais independentes. O campo da ONU não diz “reentrou às 00h de 31/10”. Sem a convenção temporal original, não se constrói intervalo UTC nem sigma terminal.

A aparente mudança de nomes entre edições NASA de 1963 e 1977 (C241-L66/L67) ganha uma advertência adicional: não se pode equiparar objetos com o mesmo rótulo **OMEGA 2** sem resolver a distinção principal/fragmento e obter identificação explícita. Também não comparar a órbita inicial da ONU (92,4 min) como se fosse coepocal à impressão NASA de outubro de 1963 (89,7 min nodal). Nem a data de lançamento fixa a época da solução orbital.

**Resultado do auditor:** três papéis distintos na transcrição, data “Decay before” categorizada como limite de registro, uma correspondência nominal de calendário, **zero observações terminais independentes**. Histórico MCMC NOT_RUN, sigma temporal ausente, probabilidade de identidade ausente e active_constraint_528=false, sem redução geográfica de Conde.

**Teste que pode mudar isso:** recuperar fac-símiles de A/AC.105/INF.013 e A/AC.105/INF.054 e uma tabela primária que cruze designador Harvard/ONU com número NORAD e papel do objeto. Para calibrar reentrada, procurar sensores, instantes, relógios e erros independentes. Até lá, não pontuar esse caso como holdout de horário.

Reprodução: executar Python 3 com tools/c241_un_omega_registry_alias_r66.py, argumento --record research/tle_custody/c241_un_omega_registry_leads_r66.json e --output para o resultado JSON. O CI testa modificações adversariais nos modos normal e otimizado, mais a execução real do auditor.
