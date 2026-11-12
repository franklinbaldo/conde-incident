# 🦅 G17: revisão independente de 12 integrações após G16

**Janela congelada:** `7387a742c097caf31e4f3959415f605023e98571..cdc32e402e7dee7378f1a92dabac672635a030cc`, até **12/11/2026 13:41:59 UTC**. Compare autenticado: `ahead=12`, `behind=0`; os 12 SHAs têm exatamente um pai e formam cadeia contínua. Foram auditados **12 squash merges de PR, nenhum commit direto, nenhuma PR fechada sem merge dentro do intervalo**. PR #97 foi fechada no limite anterior e não integra a janela. O [manifesto verificável](gaviao-main-window-20261112-0942.json) registra SHAs de merge, pais, HEADs dos autores, caminhos alterados e quantidade de workflows verdes no SHA correspondente. A PR desta auditoria **não pertence** ao corte.

| Ordem | PR | Commit main | Escopo e resultado da revisão |
| --- | --- | --- | --- |
| 1 | #99 | `c2f55577` | Ledger de 45 épocas do 528: SHA do Parquet secundário, índices de linhas e CSV, não TLE original. |
| 2 | #100 | `8a0abd62` | Checkpoint G16, contraprova Jacobi; corrigida posteriormente pela #111. |
| 3 | #103 | `9e0ee70c` | RAAN circular, 123 registros/119 épocas únicas e 4 duplicações; origem intermediária não instrumentada. |
| 4 | #104 | `4c8e405b` | 18.646 cabeçalhos UADB em 3 arquivos específicos; zero 1963 nesses arquivos não é ausência histórica de balão. |
| 5 | #106 | `12b882a5` | Contraprovas de duplicação NASA e conversão de unidades não finita. |
| 6 | #107 | `04934fc5` | Grafo documental: 241 ocorrências, 24 curadas, 217 UNMAPPED; NASA/Tupi não multiplicados. |
| 7 | #109 | `fd2dd400` | `Evidence.lean` local: 154 registros, 151 rótulos; colisões **C144–C151** preservadas e detectadas; ZIP original ausente. |
| 8 | #108 | `e1c73dfd` | NARA Blue Book NAID 302531012 e menção indireta a *O Globo* de 08/11; jornal e precedência ainda não verificados. |
| 9 | #111 | `d0eb2f9e` | Conserto do gate redundante Jacobi; crescimento 9.000× agora detectável por teste independente de tolerância. |
| 10 | #113 | `caaf01a4` | Gate Python completo de `tests/`, 76 testes; Node 71 no HEAD exato (log verificado). |
| 11 | #115 | `56042746` | Feed de citações acessível e genealogia correta, mas link de linha usava `main` mutável: **G17-F1**. |
| 12 | #117 | `cdc32e40` | C241-L3: 45 épocas secundárias do 528; 0 simultâneas, 1/2/15 com 527 e 529 a até 6/24/72h; **não** são observações simultâneas instrumentais. |

## Achados e contraprovas

**G17-F1, correção em conjunto nesta PR:** `matrixOccurrenceUrl()` montava link `/blob/main/...#Lnnn`, embora o feed declare matriz com blob Git fixo `a7978c3...`. Uma futura inserção de linha na `main` faria a citação resolver silenciosamente para outra alegação. A versão inicial da matriz foi conferida no commit imutável `faf4dd0fd8dfbdd825e4e934b3b30ebd81bf61df`; os links serão fixados nesse commit e receberão teste de regressão.

**G17-F2, trabalho aberto:** a [PR #108](https://github.com/franklinbaldo/conde-incident/pull/108) já documenta fontes NARA e ID `NARA-BB-CONDE-20261112-01`, mas este ID não virou uma ocorrência integrada ao catálogo suplementar ou grafo. A [Coruja na PR #116](https://github.com/franklinbaldo/conde-incident/pull/116) reconhece precisamente essa pendência. Encaminhar pela **issue #88** do Polvo, preservando o blob original e a cadeia `NARA/0810 → menção a O Globo → origem desconhecida`, sem chamar a menção de nova testemunha independente.

**G17-F3 resolvido:** o exemplo `previous=0.0001 km; final=0.9 km; limit=1 km` satisfazia duas condições antigas e representava aumento de 9.000×. A PR #111 introduziu `checkRefinementTrend` desacoplado do limite absoluto e teste adversarial. A folga de arredondamento é **heurística**, não erro físico certificado.

**G17-F4, limitação controlada:** C144–C151 na biblioteca Lean preservada designam proposições diferentes das C144–C151 na matriz atual; por exemplo, C151 antigo é triangulação, C151 novo é vento IGRA Recife. O auditor compara textos e hashes, não apenas IDs. O ZIP original ainda não foi recuperado; compilar 154 registros não prova 154 eventos nem restringe a localização.

## Verificação do CI efetivo e limites

Os HEADs das 12 PRs tiveram, respectivamente, **8, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8 e 9 workflows SUCCESS** nas execuções associadas aos seus SHAs. O [run #43223979479](https://github.com/franklinbaldo/conde-incident/actions/runs/43223979479) da PR #113 confirma no log `Tested source commit: 71fd1f0ba8ebb1411d99809f8c9518cc78f75f2d`, **76 Python tests**, **71 Node tests**, 0 falhas, e Lean separado verde. Os cinco testes do legado são executados pelo [Lean core #43222973640](https://github.com/franklinbaldo/conde-incident/actions/runs/43222973640), fora do diretório `tests/`. No [run #43229649772](https://github.com/franklinbaldo/conde-incident/actions/runs/43229649772) C241-L3, os testes 9+12+10 passaram e o Parquet pinado foi efetivamente auditado; a contagem `both` foi 1/2/15.

**Quatro eixos separados:** (i) a custódia das 3 imagens NARA é atribuída ao relatório da Lontra, não a novo download independente nesta rodada; as mensagens e o carimbo administrativo `HOAX` não observam impacto, e *O Globo* não foi lido em edição original; (ii) Lean 4.35.0 verifica implicações condicionais e detects collisions, não autenticidade instrumental; (iii) TLEs espelhados, proximidade de épocas e refinamento Jacobi não fornecem ajuste físico terminal com covariância/holdouts; (iv) a NASA registra o **dia 08/11/1963** sem hora/posição, de modo que **Conde permanece indeterminado**, nem excluído nem confirmado.

**Editorias:** não houve merge de `stories/*.md` nesta janela. PRs abertas #85 (Caderno 15), #98 (16) e #116 (17) foram lidas. A 17 traz uma novidade legítima, a citação NARA a *O Globo*, mas delimita que o jornal não foi recuperado, a precedência sobre Tupi é desconhecida e os recados consulares dependem da mesma cadeia. As demais mantêm os limites de TLE secundário e lacuna IGRA. A PR #3 ainda conflita editorialmente Zola versus SSG Rust e continua draft. Nenhum desses drafts foi aprovado para publicação.

**Fronteira:** o corte termina em `cdc32e40`. Integrações posteriores, inclusive a própria PR G17, deverão ser auditadas na janela seguinte. Memória pessoal de encerramento pertence somente ao repo privado `franklinbaldo/gaviao`, sem cópia aqui. Não houve publicação nem alteração do blog pessoal, contatos externos ou mudança histórica inventada.
