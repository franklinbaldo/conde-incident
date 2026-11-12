---
type: Guide
title: "C241-P7: períodos nodais de outubro de 1963 contra Kepler e J2"
description: "Controle quantitativo das três linhas NASA de 15/10/1963 com dois modelos congelados, resíduos em segundos e contraprova do 3A."
---

# C241-P7: a tabela NASA permite uma contraprova física, não uma órbita terminal

**Pergunta falsificável (#15):** usando apenas período nodal, inclinação e alturas de apogeu/perigeu **impressos** na edição de 15/10/1963 do *NASA Satellite Situation Report*, o proxy draconítico secular J2 reduz o resíduo de período em relação ao Kepler de dois corpos **para cada uma das linhas 1963 3A/3B/3C**? A resposta é **não**: melhora 3B e 3C, mas piora 3A.

## Fonte original, IDs e dependências

- **C241-L12#1**, publicação NASA/Goddard, *Satellite Situation Report* vol. 3 nº 20 de **15/10/1963**, tabela *Objects in Orbit*, p. **impressa 5** (PDF p. 7). [NTRS 19640000428](https://ntrs.nasa.gov/citations/19640000428); [PDF NASA](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf). Ledger com transcrição visual previamente curada: [C241-L12](../tle_custody/nasa_ssr_1963_oct15_C241-L12.json). Artefato utilizado pelo ledger: SHA-256 `fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2`, 286.417 bytes. A mesma URL também forneceu variante `826f2605...`; são representações da **mesma** publicação, não observações extras. A execução deste script lê a transcrição versionada, **não** reabre/revalida pixels do PDF.
- C179#1 é um TLE de **espelho secundário** com elementos em **27/10/1963**, **não utilizado** neste cálculo; C197#1 é a listagem NASA posterior de dia de decaimento, também não utilizada. A correspondência moderna de 1963-003A/B/C com NORAD 527/528/529 é catalográfica; a fonte NASA exibe somente os designadores **3A, 3B e 3C**.
- As três linhas vêm do **mesmo boletim compilado** a partir de dados de rastreamento não fornecidos. Não são três instrumentos independentes nem validam a precisão do catálogo secundário. O dia de publicação **não** é época de observação.

## Operadores congelados e unidades

Hipótese explicitamente contrafactual: tomar as alturas publicadas (km) como altitudes apsidais em uma superfície esférica de raio equatorial moderno `R=6378,137 km` e `μ=398600,4418 km³/s²`, com `J2=0,00108262668`. Nenhum desses três parâmetros vem da edição NASA. Definir `a=R+(h_a+h_p)/2`, `e=(h_a-h_p)/(2a)`, `n=sqrt(μ/a³)`, `T_K=2π/(60n)`. Para o proxy draconítico secular de primeira ordem, `T_J2=2π/[60(M_dot+ω_dot)]`, com

`ω_dot=(3/4)J2 n(R/a)²(5cos²(i)-1)/(1-e²)²`

`M_dot=n+(3/4)J2 n(R/a)²(3cos²(i)-1)/(1-e²)^(3/2)`.

Isso **não** transforma alturas catalográficas em elementos médios instrumentais, não equivale a SGP4, ignora correções periódicas e não reconstrói uma órbita. Todos os ajustes possuem **zero parâmetros estimados**; 3B é objeto-alvo pré-declarado, 3A/3C são controles do **mesmo relatório**, não holdouts instrumentais. Os resíduos abaixo são `(modelo − período impresso)×60`, em **segundos**.

| Publicação NASA | P impresso (min) | Kepler (min) | Resíduo Kepler (s) | J2 (min) | Resíduo J2 (s) |
|---|---:|---:|---:|---:|---:|
| 1963 3A | 94,6 | 94,544090 | −3,354590 | 94,665889 | **+3,953351** |
| 1963 3B | 92,4 | 92,324943 | −4,503412 | 92,447659 | **+2,859514** |
| 1963 3C | 93,3 | 93,237185 | −3,768888 | 93,359499 | **+3,569948** |

Média dos módulos dos resíduos: **3,875630 s (Kepler)** contra **3,460938 s (J2)**. O J2 reduz o resíduo médio em **0,414692 s**, mas o **3A refuta a hipótese de melhoria universal**. A impressão é de apenas **0,1 minuto (=6 s)** e alturas inteiras de km; o resíduo não é sigma instrumental, nem valida precisão subsegundo. Tampouco a diferença entre períodos **nodais** e períodos Keplerianos autoriza igualá-los silenciosamente a `1440 / n_TLE`.

## Domínio, falsificação e resultado negativo

- **Antes/depois do domínio físico Θ(527,528,529):** inalterado, sem exclusão. O conjunto de **modelos candidatos** `{Kepler, J2 de primeira ordem}` também não recebe corte empírico rígido, pois não há erro/época/modelo de publicação calibrados. Não-vazio físico **não avaliado**; nenhum instante ou local de impacto inferido.
- **Teste quantitativo realizado:** ambos os modelos confrontados nas mesmas três linhas, com hipótese J2 universal **falsificada pelo 3A**. Nenhum ajuste sobre as linhas avaliadas, nenhuma probabilidade posterior e nenhum holdout de instrumento independente.
- **Faltam** fichas de rastreamento originais de 1963-003B e controles 3A/3C com épocas, quadro, definição histórica de altitude e período nodal, covariâncias, sensor e cadeia de transformação para os TLEs; sem isso não existe desigualdade física defensável a promover como predicado Lean 4.35.0. A biblioteca Lean permanece intocada por decisão epistêmica, mas seus gates atuais seguem obrigatórios na PR.

## Reprodução sem rede

`python3 -m unittest discover -s tests -p test_ssr_oct15_kepler_j2_nodal.py -v`

`python3 tools/ssr_oct15_kepler_j2_nodal.py`

`cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean`

A entrada passa por `tools/tle_nasa_ssr_oct15_audit.py::validate_ledger` antes de qualquer cálculo. Sete controles adversariais cobrem proveniência, valores auditados, parâmetros inválidos, sensibilidade a inclinação, `J2=0`, contraprova 3A e a ausência de restrição física. Não acrescenta JSON de gate com `null` nem prova Lean sobre limitações já conhecidas.
