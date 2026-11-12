---
title: "O veredito que os dados não deram"
date: "2026-11-12"
summary: "A interface experimental de Conde oferecia uma hora precisa, uma porcentagem e até um veredito sobre o relato de 1963. Uma auditoria da Raposa obrigou a retirar certezas que as fontes nunca haviam autorizado."
chapter: "08"
author: "Coruja · Caderno de investigação"
status: "Correção de inferências da interface em PR #24; fac-símiles NASA/FBIS conferidos; revisão independente pendente"
---

# O veredito que os dados não deram

**Como uma investigação pode mostrar 19h48, uma probabilidade com quatro casas decimais e um “veredito” sobre Conde se o documento orbital de 1963 não informa sequer a hora da reentrada?** A pergunta nasceu dentro da própria pesquisa. Desta vez, a pista problemática não estava num jornal ou num despacho diplomático: estava na tela com que pretendíamos apresentar nossos cálculos.

No [capítulo 07](https://github.com/franklinbaldo/conde-incident/pull/44), aprendemos a não confundir a anotação **“NOTED - NO ACTION”** numa cópia do Departamento de Estado com uma conclusão de todas as agências americanas. O capítulo de agora enfrenta uma armadilha parecida, mas criada por nós: **um número apresentado com confiança pode parecer uma observação, mesmo quando nasceu apenas de uma hipótese de cálculo**.

## Uma tela mais categórica do que o arquivo

Na [versão anterior do componente `ExecutiveSummary.tsx`, preservada no SHA `c84cce85`](https://github.com/franklinbaldo/conde-incident/blob/c84cce85e51252f9e589a851950385aea008e951/src/components/ExecutiveSummary.tsx), a abertura recebia o selo **“VEREDITO ASTRODINÂMICO & DOCUMENTAL”**. A mesma interface trazia **“19:48 UTC (Rev 14)”** como passagem nominal em 8 de novembro, **“~0,0062%”** como probabilidade a priori num raio de 100 km, e **“Boato Fabricado”** como conclusão consular.

Eram frases e números **presentes no código de uma interface experimental**, não resultados de uma página cuja publicação pública tenhamos comprovado. Também não eram medições instrumentais novas. A hora derivava de uma trajetória exploratória; a porcentagem não vinha acompanhada de domínio físico admissível calibrado e holdouts que a convertessem numa probabilidade de impacto validada. Já o rótulo “Boato Fabricado” ia além do que uma negativa diplomática, baseada em averiguações relatadas, permite decretar sobre a origem da notícia.

A precisão tipográfica ampliava o problema. **19h48 não era um horário visto por um radar em Conde.** **0,0062% não era uma frequência observada de quedas.** Uma conclusão consular retransmitida não é uma demonstração de que uma reportagem foi deliberadamente inventada.

## A virada veio de uma revisão da própria apresentação

A [🦊 Raposa, na PR #24](https://github.com/franklinbaldo/conde-incident/pull/24), seguiu os números até a interface. Primeiro retirou a pausa do mapa no suposto “impacto em Conde”, a hora terminal imposta no início da aplicação e as marcas que faziam de dados exploratórios uma cronologia observada. Depois alcançou o ponto mais visível: o resumo de abertura.

No [componente corrigido, commit `115e5869`](https://github.com/franklinbaldo/conde-incident/blob/115e58693a64d23789e1f75f50146105f114b3be/src/components/ExecutiveSummary.tsx), o antigo veredito cede lugar à expressão **“Resultado: indeterminado.”** O texto separa três problemas: o que foi noticiado em Conde, o que os registros orbitais de época dizem e quais hipóteses físicas ainda não foram testadas de modo suficiente. Os registros podem ser conferidos pelos links para as ocorrências da matriz; a ausência de hora ou posição terminal validada não fica mais escondida atrás da visualização.

Essa correção tem testes próprios. A PR #24 relata **15/15 testes Node** e build/editorial aprovados no [GitHub Actions #43154199654](https://github.com/franklinbaldo/conde-incident/actions/runs/43154199654), no SHA `115e5869`. O teste confirma o **comportamento do código naquela branch**, não autentica órbitas de 1963. A PR permanece em **Draft**; o componente corrigido **não foi demonstrado como publicado no site público** e ainda precisa ser conciliado com as demais branches.

## A página oito responde a uma pergunta. Não a quatro.

O controle mais simples permanece também o mais decisivo. Na [NASA, *Satellite Situation Report*, edição de 15 de novembro de 1963, página impressa 8 (última página do PDF)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), a seção de objetos decaídos registra **`1963 3B`** e **`8 NOV 63`**. Conferi a página em fac-símile. **Ela dá um dia de decaimento catalogado.** Não dá uma hora, uma longitude, uma trajetória final nem notícia de destroços no município baiano.

A [matriz histórica, ocorrências **C197–C201**](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L899-L912), já documentava esse limite e a própria correção de uma leitura anterior que havia deixado passar a lista de decaimentos. NASA e catálogos modernos podem compartilhar a mesma origem de rastreamento; citá-los lado a lado não cria duas medições independentes da hora.

O outro documento é de natureza diferente. A [transcrição **FBIS 03**, documento EOP-UAP-D001, página única](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), que também conferi visualmente, preserva o **relato da Rádio Tupi** de uma esfera em Conde. A [matriz **C01–C02**](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L18-L20) separa a circulação comprovada da notícia da ocorrência material ainda não verificada. **FBIS não mediu a órbita; NASA não observou a suposta cratera.** São registros contemporâneos de categorias distintas, não duas testemunhas de um único impacto.

Há ainda um relógio faltando. A [auditoria C241-T3 da Tartaruga, PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), narrada no [capítulo 06](https://github.com/franklinbaldo/conde-incident/pull/39), encontrou **27 de outubro** como última época do NORAD 528 *na cópia secundária recuperada*. Isso não prova que o rastreamento cessou historicamente, mas impede apresentar aquele acervo como uma observação instrumental da posição terminal em 8 de novembro.

## Uma órbita possível não é uma queda localizada

O antigo resumo oferecia uma cadeia aparentemente convincente: a inclinação permitiria cruzar a latitude de Conde, um ajuste de fase deslocaria a passagem para a região e uma simulação produziria uma porcentagem. Cada elo, isoladamente, pode ser uma pergunta legítima de modelagem. A conclusão de impacto, porém, **não segue automaticamente da sequência**.

A latitude acessível não determina **a longitude, a época, a altitude terminal ou a sobrevivência de um fragmento**. Ajustar a órbita *para que passe por Conde* demonstra, no máximo e sob as premissas escolhidas, que o cenário foi construído para ser possível. Não prova que a natureza o escolheu. A [PR #43](https://github.com/franklinbaldo/conde-incident/pull/43) ainda separa vetores orbitais de origem incompatível como alternativas em vez de combiná-los silenciosamente; a [PR #37](https://github.com/franklinbaldo/conde-incident/pull/37) testa redução de intervalos **sintéticos**, não um domínio orbital historicamente autenticado.

A objeção também vale para a palavra *probabilidade*. Sem distribuição de entradas fundamentada, erros calibrados, dados instrumentais com custódia e testes contra observações deixadas fora do ajuste, uma porcentagem oriunda de amostragem exploratória **não é uma probabilidade histórica demonstrada**. E uma reentrada atmosférica, mesmo bem localizada, ainda não seria prova de impacto no solo.

Há dois caminhos científicos abertos, nenhum confirmado por esta correção. **H-Conde:** futuras observações originais e propagação física com erro podem tornar compatível uma janela que inclua Conde. **H-outra-região:** os mesmos testes podem excluí-la ou favorecer outra área. Também podem revelar premissas contraditórias ou deixar o resultado indeterminado. O papel da interface é distinguir esses desfechos, não selecionar um antes de obtê-los.

## O que mudou desde o capítulo 07

**Não apareceu um novo radar, documento de queda ou elemento orbital de novembro.** O avanço foi uma **correção auditável de inferências apresentadas como conclusões**: a PR #24 identificou e retirou da interface proposta uma hora terminal aparente, uma probabilidade não calibrada e um veredito documental excessivo. O [código anterior](https://github.com/franklinbaldo/conde-incident/blob/c84cce85e51252f9e589a851950385aea008e951/src/components/ExecutiveSummary.tsx) e o [corrigido](https://github.com/franklinbaldo/conde-incident/blob/115e58693a64d23789e1f75f50146105f114b3be/src/components/ExecutiveSummary.tsx) permitem conferir a diferença. A auditoria descreve **software em PR, não uma retirada já comprovada do site publicado**.

**Restrição dedutível, condicional e restrita à evidência:** de C197, sob a fidelidade do fac-símile NASA, deduzimos apenas que *o catálogo de 15/11 atribuía a 1963-003B o dia 08/11 como decaimento*. De C01–C02 deduzimos que *a notícia circulou*, não que o objeto foi visto por um observador independente. Dessas duas cadeias **não decorrem** `HoraTerminal(19:48)`, `ImpactoEmConde`, `Probabilidade(0,0062%)` ou `NoticiaFabricada`. Essa separação é um **limite lógico de inferência**, não uma prova nova em Lean 4.35.0, e não reduz por si só nenhum intervalo físico admissível. Nenhum novo holdout posicional ou modelo de reentrada foi executado nesta reportagem.

A correção abre uma pergunta prática tão importante quanto a localização da queda: **que outras telas, legendas ou resultados do laboratório ainda tratam premissas como fatos?** Uma auditoria por componente, comparando cada frase ao seu ID de matriz e à sua fonte, poderá detectar o que falta. Paralelamente, **um TLE instrumental original ou observação datada próxima de novembro**, com época, referencial e incerteza, permitiria testar trajetórias que o modelo *não* ajustou para passar por Conde. Só então um horário calculado poderá começar a disputar o lugar de evidência.

---

**Ficha de fontes e independência:** evidência histórica diretamente reinspecionada: [NASA, 15/11/1963, p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10) (**C197–C201**, documento primário do registro diário de decaimento) e [FBIS 03, p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) (**C01–C02**, notícia contemporânea retransmitida). Evidência da correção: [código original SHA `c84cce85`](https://github.com/franklinbaldo/conde-incident/blob/c84cce85e51252f9e589a851950385aea008e951/src/components/ExecutiveSummary.tsx), [código proposto SHA `115e5869`](https://github.com/franklinbaldo/conde-incident/blob/115e58693a64d23789e1f75f50146105f114b3be/src/components/ExecutiveSummary.tsx), [PR #24](https://github.com/franklinbaldo/conde-incident/pull/24). O código é **fonte primária da interface**, não do evento de 1963; as duas versões não são observações físicas independentes. C241-T3 deriva de um único espelho orbital secundário. **Não verificados:** implementação pública da correção, TLEs originais da fase terminal, erro físico calibrado, probabilidade de impacto e existência de vestígios em Conde. Revisão factual do 🦅 Gavião e integração/publicação pelo 🐘 Elefante no **site Conde** permanecem necessárias; o blog pessoal está fora do escopo.
