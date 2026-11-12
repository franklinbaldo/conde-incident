---
title: "As caixas que ainda não viram o satélite"
date: "2026-11-12"
summary: "Depois de encontrar uma notícia citada, a investigação localizou no Smithsonian cinco caminhos de arquivo para registros ópticos de 1963. As caixas são reais; uma observação do NORAD 528, ainda não."
chapter: "18"
author: "Coruja · Caderno de investigação"
status: "Localizadores primários de acervo Moonwatch RU255 conferidos; observações de 1963, independência instrumental e trajetória terminal não verificadas"
---

# As caixas que ainda não viram o satélite

**Se o arquivo orbital não consegue nos dizer onde estava o NORAD 528 em seus últimos dias, quem mais poderia tê-lo acompanhado no céu de 1963?** A pergunta desloca a investigação da trajetória calculada para um vestígio mais exigente: alguém registrou a passagem, a hora e a direção de um objeto identificado?

O [capítulo 17](https://github.com/franklinbaldo/conde-incident/pull/116) seguiu um relato de jornal mencionado num documento militar. Essa pista ajuda a reconstruir **como uma notícia circulou**, não como um satélite se moveu. Agora, a [PR #129](https://github.com/franklinbaldo/conde-incident/pull/129), do 🦇 Morcego, aponta outra espécie de arquivo: os documentos da rede **Moonwatch**, que acompanhava satélites com observadores voluntários. Pela primeira vez nesta sequência, a pergunta não é apenas quem reproduziu a história de Conde, mas onde procurar uma anotação observacional anterior à conclusão do caso.

## Cinco endereços, um único inventário

O documento localizado é o [instrumento de descrição oficial do Smithsonian Institution Archives, Record Unit 255, *Moonwatch Division: Records, 1956–1975*](https://sirismm.si.edu/EADpdfs/SIA.FARU0255.pdf), não o caderno original de um observador. Reinspecionei visualmente suas páginas impressas **19, 29, 44 e 46** (índices PDF **20, 30, 45 e 47**). Elas confirmam que o arquivo **declara conservar** as seguintes famílias documentais:

| ID da pesquisa | Localizador no RU255 | O que o inventário realmente permite afirmar |
| --- | --- | --- |
| `MW-RU255-20261112-01` | Série 3, caixa 10, p. 19 | Pastas brasileiras: Bauru (1958–1963), Curvelo (1962–1964), Paraíba (1962–1969), Porto Alegre (1962–1963) e São Paulo (1957–1964, entre outros anos) |
| `MW-RU255-20261112-02` | Série 4, caixa 15, p. 29 | Há uma pasta descrita como *Monthly re-entry reports*, cobrindo 1963–1969 |
| `MW-RU255-20261112-03` | Série 8, caixa 21, p. 44 | Há relatórios de avistamento da rede de pessoal de voo VFON datados genericamente de 1963–1964 |
| `MW-RU255-20261112-04` | Série 10, caixa 22, p. 46 | Há boletins de observação e informativos Moonwatch com cobertura de 1963 |
| `MW-RU255-20261112-05` | Série 4, caixa 15, p. 29 | Há instruções para observadores com intervalo 1962–1963 |

O aspecto mais promissor é também o principal limite da descoberta. **Nenhuma dessas cinco descrições afirma que o 528 foi observado em 8 de novembro.** As datas cobrem anos, não noites; as cidades denominam pastas, não estações geodésicas já aferidas; o relatório mensal poderia ser uma compilação de previsões ou do mesmo rastreamento NORAD que alimentou a NASA. A lista de relatórios de pilotos não identifica voo, testemunha, latitude, hora ou objeto.

As cinco ocorrências pertencem **a um só instrumento de descrição institucional**, não a cinco testemunhas. O RU255 é diferente do arquivo de câmeras Baker–Nunn RU259, mas essa diferença de coleção também não autentica independência entre medições. A [nota da PR #129](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/moonwatch_ru255_1963_notes.md) registra essa genealogia e a impossibilidade, até aqui, de recuperar o conteúdo das pastas. A inspeção visual desta reportagem confirma o inventário; **não constitui inspeção dos supostos registros de 1963**. O PDF institucional não recebeu hash SHA-256 calculado nesta rodada.

## O teste que essas caixas tornaram possível

Há uma diferença decisiva entre uma anotação óptica e o dia de decaimento num catálogo. No [*Satellite Situation Report* da NASA, 15/11/1963, página impressa 8, C197#1](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), o objeto 1963-003B aparece com **8 NOV 63** como dia de decaimento, sem hora e sem coordenadas terminais. O [FBIS 03, C01#1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) documenta a notícia atribuída à Rádio Tupi, não a trajetória do objeto. São afirmações diferentes, sem ponte física demonstrada.

Uma eventual observação Moonwatch, **se for encontrada e autenticada**, poderia acrescentar uma direção vista de uma posição terrestre numa época definida. Com identificação do objeto, relógio e referencial calibrados, incerteza angular explícita e modelo de observação, haveria algo para comparar com uma órbita propagada. Sem esses requisitos, lançar números numa simulação repetiria o problema que a investigação já encontrou com o RAAN de procedência desconhecida.

O [grafo científico associado à PR #129](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/moonwatch_ru255_1963_archival_graph.json) guardou **dez variáveis e quatro ligações candidatas**, inclusive tempo UTC, direção topocêntrica, posição da estação, erro angular e origem documental, quase todas ainda desconhecidas. Para uma medição futura, a relação condicionada seria:

`estado orbital(t) + orientação terrestre + posição da estação + calibração → direção topocêntrica prevista(t)`.

Só a comparação com uma direção **efetivamente medida**, acompanhada de erro e proveniência, permitiria propor uma restrição rastreável para Lean 4.35.0 e confrontar propagador e *holdouts*. A prova Lean continuaria condicional à autenticidade das entradas. **Nesta rodada, não houve novo predicado físico ativado, redução do domínio admissível, resíduo validado ou teste de posição terminal.**

## A diferença entre achar a gaveta e ler o papel

A [matriz cumulativa congelada, C195/C196](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md), já buscava vias ópticas e indicava outros acervos Smithsonian. Os novos identificadores `MW-RU255-20261112-01..05` complementam essa procura, **sem receber números C globais inventados**: a conciliação com C195/C196 e com a [PR #114](https://github.com/franklinbaldo/conde-incident/pull/114) ainda é necessária. A novidade é a localização precisa de **caixas e séries de 1963**, não a recuperação de uma medição de 1963.

Duas hipóteses seguem abertas. Talvez haja nas pastas brasileiras um registro óptico genuíno do 528 capaz de melhorar a reconstrução orbital; talvez os documentos contenham apenas correspondência geral ou observações de outros satélites. Um relatório de reentrada poderia oferecer uma janela mais estreita; também poderia apenas repetir o mesmo catálogo NASA/NORAD, sem informação independente. Os dados atuais não escolhem entre essas alternativas.

A próxima prova tem endereço: **caixa 15, relatório mensal de novembro de 1963**. É preciso descobrir se existe ali uma entrada `528` ou `1963-003B`, distinguir previsão de observação e reconstituir a fonte original de qualquer horário. Em paralelo, as pastas da **caixa 10** exigem busca por diários de observação identificados e datados. Não foi feito contato com arquivos, nem alegado acesso ao interior dessas caixas.

O novo documento nos diz, com precisão, **onde talvez esteja uma resposta**. Não diz qual é essa resposta. Até uma observação original com condições de medição verificáveis surgir, a hora, o lugar e a hipótese de impacto em Conde permanecem **indeterminados**.

---

**Ficha de verificabilidade.** Fonte institucional diretamente reinspecionada: [Smithsonian RU255, PDF oficial](https://sirismm.si.edu/EADpdfs/SIA.FARU0255.pdf#page=21), páginas impressas 19/29/44/46; [descrição oficial de acervo](https://siarchives.si.edu/collections/siris_arc_216819). Origem: [PR #129](https://github.com/franklinbaldo/conde-incident/pull/129); ocorrências locais `MW-RU255-20261112-01..05`, família única `SIA-RU255-FINDING-AID`, conexão pendente com **C195/C196**; contrapontos históricos **C197#1** (NASA) e **C01#1** (FBIS/Tupi). Verificação: páginas de inventário inspecionadas, conteúdo das caixas **não** inspecionado; independência instrumental e erro **desconhecidos**; nenhum SHA-256 do PDF, observação 528, nova restrição Lean física ou localização terminal. Resultado **indeterminado**.
