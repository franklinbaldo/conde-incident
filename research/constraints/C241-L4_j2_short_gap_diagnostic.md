# C241-L4: diagnóstico numérico J2 em pares secundários curtos de 528 e controle 529

**Pergunta falsificável (🐙 Polvo, issue #15).** Nos pares consecutivos de épocas com separação **até 24 horas**, a mudança circular de RAAN da série secundária de 1963 é mais compatível, em erro absoluto angular (graus), com (A) RAAN constante ou (B) proxy secular Kepler/J2 calculado *sem ajuste* nos elementos do primeiro registro? Existe também um controle elegível de 527?

## Custódia e independência

- **C241-L4:** Parquet secundário [oxzoid/space-track-tle-history rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. CSV determinístico de 123 linhas de 527/528/529 SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. Reexecução parte dos bytes pinados; não faz download de fonte sem verificar SHA.
- **C179#1:** mesmo grupo documental secundário, TLE 528 de 27/10/1963 com RAAN **198,5261°** e epoch de elementos 1963-10-27T14:40:16.132512Z (não época instrumental original). Par literal com checksums sintáticos versionado em `research/tle_custody/mirror_528_1963-10-27.tle`. RAAN **284,1520°** continua sem fonte e **não foi usado** no cálculo.
- **C197#1:** boletim oficial NASA de [15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), com **08/11/1963** como dia catalogado da reentrada, não hora nem RAAN terminal. Não fornece observação adicional aos pares desta tabela.
- Os três objetos vêm da **mesma família de espelho moderno**. O controle 529 é externo ao objeto-alvo do diagnóstico, mas **não** é teste instrumental independente; várias linhas de um Parquet não são sensores distintos.

## Operador físico pré-fixado (sem fit de parâmetros)

`n = 2π n_rev_dia / 86400` (rad/s); `a = (μ/n²)^(1/3)` (km); `dΩ/dt = -(3/2) J2 n [R_e/(a(1-e²))]² cos(i)` (rad/s). Constantes de C179: μ=398600,4418 km³/s²; R_e=6378,137 km; J2=0,00108262668. Para cada par consecutivo elegível, `ΔΩ_J2 = (dΩ/dt)_início Δt`, `ΔΩ_catalog = wrap180(Ω_fim-Ω_início)`, `resíduo = wrap180(ΔΩ_catalog - ΔΩ_J2)`; baseline: `ΔΩ_baseline=0°`. A tolerância de 24h seleciona amostras e **não** representa erro de medição. O modelo não é SGP4 nem conversão verificada de frame/elemento médio para estado osculante.

## Resultado reproduzido sobre o artefato real de C241-L4

| Objeto | Épocas únicas | Pares consecutivos até 24h | MAE RAAN constante (graus) | MAE proxy J2 (graus) |
|---|---:|---:|---:|---:|
| NORAD 527 | 20 | 0 | não avaliável | não avaliável |
| NORAD 528 | 45 | 3 | **0,450602** | **0,048824** |
| NORAD 529 (controle externo ao 528) | 54 | 3 | **0,322360** | **0,140853** |

Pares, usando índices de linha original do Parquet, não números de observadores: 528: `2973→2974`, `2976→2977`, `3004→3005`; 529: `3018→3019`, `3022→3023`, `3070→3071`. Os resíduos J2 (graus, ordem dos pares) são 528: **+0,126136; +0,018234; −0,002103**, 529: **+0,201204; +0,100260; +0,121096**. A métrica compara dois operadores pré-fixados sobre os mesmos dados secundários, **não mede erro contra verdade orbital**. Não há pares 527 próximos o bastante para este teste. Nenhuma estatística de desvio-padrão/sigma instrumental é inferida desses seis resíduos.

**Resultado negativo:** a melhora em MAE nesses seis intervalos **não** valida o histórico orbital, não identifica a origem de 284,1520°, não produz probabilidade, não identifica reentrada e não ajusta Θ. Os erros de J2 no 529 continuam **maiores que no 528**; não há motivo para tratar 529 como prova física independente. Os 44 intervalos do 528 incluem 32 lacunas superiores a 72h; não extrapolar este benchmark de pares curtos sobre as lacunas.

**Domínios admissíveis antes → depois:** sem predicado físico calibrado, zero restrições rígidas novas → zero, conjunto físico **inalterado e não avaliado numericamente**. Não se declarou testemunha de não-vazio de Θ. A nova informação é numérica e auditável, não nova restrição de impacto.

## Reprodução / próxima medição necessária

Executar o workflow `Polvo - C241-L4 J2 short-gap controls` no **SHA exato da PR**. Ele reconstrói o CSV a partir do Parquet verificado, executa o algoritmo `formal/scripts/audit_secondary_j2_raan.py`, os testes adversariais e `lake build` / auditoria de axiomas Lean 4.35.0. O JSON de saída retém valores sem arredondamento, unidades, epochs e índices de linha. A comparação não depende do site ou do blog.

Para converter um destes resíduos em predicado Lean que realmente limite Θ, faltam os pares TLE originais com **checksums de custódia, convenção de elementos/frame e época observacional**, erro/covariância de tracking e teste dinâmico calibrado em 527/528/529. Só então identificar intervalos de erro admissíveis, testemunha de não-vazio e mudanças no domínio. A inspeção de dados públicos pinados não substitui o acesso ao documento primário.
