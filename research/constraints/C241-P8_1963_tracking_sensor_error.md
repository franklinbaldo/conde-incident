---
type: Guide
title: "C241-P8: redes de rastreamento de 1963 e limites de precisão instrumental"
description: "Fontes primárias NASA/NORAD sobre sensores, lugares e precisão nominal; teste necessário para erro orbital do 528."
---

# C241-P8: que instrumento observou o NORAD 528?

**Pergunta falsificável, issue #15:** as fontes históricas já recuperadas identificam
uma medição datada do objeto 1963-003B/NORAD 528, seu instrumento e a
covariância necessária para transformar RAAN ou elementos secundários em
restrição física? **Não.** As fontes documentam redes e capacidades, não uma
ficha de observação identificada do 528.

## Fontes e grau de acesso

| Fonte e data | Localizador e conteúdo diretamente verificável | Alcance |
|---|---|---|
| [Relatório dos EUA sobre atividades espaciais de 1961](https://www.nasa.gov/wp-content/uploads/2024/01/presrep1961.pdf), publicado janeiro/1962 | Cap. X, p. impressa **73** (PDF p. 75), Smithsonian: 12 câmeras Baker–Nunn, precisão **4 segundos de arco** e **2 ms** de tempo; fotometria/astrometria, redução, computação e comunicação. Página visualmente conferida. | Especificação de rede, **não** erro de medição do 528 em 1963. |
| [NORAD/CONAD, Historical Summary, July–December 1963](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/11.pdf), fac-símile contemporâneo divulgado pela National Security Archive | P. impressas **54–58** (PDF pp. 3–7): SAO possuía 12 câmeras, USAF quatro e Canadá uma; Cold Lake sob NORAD; Prince Albert Radar Laboratory; radar em Diyarbakir incorporado em 01/08/1963; radar FPS-44 de Trinidad contribuía parcialmente. Fac-símiles pp. 55 e 58 inspecionados. | Confirma capacidades e gestão em 1963, **não** que mediram 528. |
| [SRI, relatório para NASA/GSFC, contrato NAS 5-3974, N65-33857, 1965](https://ntrs.nasa.gov/api/citations/19650024256/downloads/19650024256.pdf) | Seção 3, p. impressa **82**, tabela textual: Minitrack **0,9 mrad**, refletores **0,3–0,6 mrad**, Baker–Nunn **14,5 µrad**; resíduos de ajuste semanal com Minitrack **0,126–1,63 mrad**, ópticos ~**14 µrad**. Página inferida da transcrição web; inspeção visual dessa página **não concluída** porque PDF de 10,6 MB não abriu no visualizador. | Especificações/relatos **de 1965**, posteriores ao evento; nem sigma 1963 nem erros do 528. |
| [NASA, história do sistema Vanguard](https://www.nasa.gov/history/sputnik/chapter9.html), cap. 9 | Minitrack media diferenças de fase de um transmissor embarcado para obter direção; rede fotográfica Smithsonian separada; estações incluíam Jupiter (FL), Organ Pass (NM), Haleakala (HI), Shiraz (Irã), Curaçao e Woomera (Austrália). | História da implantação, sem log específico do 528; Minitrack exigia sinal adequado da espaçonave. |
| [NASA, Satellite Situation Report de 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), C197#1/C198#1 | P. impressa **8**, dia de decaimento 08/11/1963 da designação 1963-003B. | Boletim compilado **não** identifica sensor, época de última medição, hora/local de impacto nem incerteza instrumental. |

**Custódia nesta rodada:** URLs, órgãos, datas e páginas preservados. Não houve
download binário autenticado nem cálculo de SHA-256 dos documentos desta
nota; não registrar hash fictício. A fonte NOAA/SAO secundária ou um
boletim compilado não equivale a uma observação radar independente.

## Unidades: não confundir resolução, residual e sigma

| Técnica e época documental | Valor publicado | Conversão de unidade | Não significa |
|---|---:|---:|---|
| Baker–Nunn, relatório de 1961 | 4″ angular; 0,002 s temporal | 19,3925 µrad; 2 ms | σ de posição da órbita 528 |
| Minitrack, relatório de 1965 | 0,9 mrad | 0,051566° (~3,094′) | precisão de radar passivo sobre 528 |
| Antenas parabólicas, relatório de 1965 | 0,3–0,6 mrad | 0,017189°–0,034377° | covariância de ajuste do 528 |
| Baker–Nunn, relatório de 1965 | 14,5 µrad | 2,991″ | a mesma medida identificada em 1961 |
| Resíduo de ajuste Minitrack em uma semana, relatório 1965 | 0,126–1,63 mrad | 0,00722°–0,09339° | erro máximo terminal ou limite de confiança |

O erro angular de uma câmera **não** vira automaticamente erro de posição
em km: depende de distância, orientação da linha de visada, geometria de
múltiplos instantes/estações, erros sistemáticos, relógio, modelo dinâmico
e covariâncias. Resíduo de ajuste não quantifica necessariamente viés
sistemático ou erro de extrapolação de semanas, sobretudo na reentrada.

O próprio NORAD declarou em 1963 a necessidade de uma análise da
**precisão requerida versus a oferecida** antes de integrar novas câmeras
à sua rede. Um documento posterior descreve incertezas de geodesia de
sensores, alcance de radares e modelo gravitacional no SPADATS da época:
[história USAF do programa](https://www.dafhistory.af.mil/Portals/16/documents/Airmen-at-War/Sturdevant-USAFspaceSurveillance1957-2007.pdf),
pp. 10–12. Não inferir independência NASA↔NORAD a partir do timbre.

## Condições para restrição física do 528 (handoff Castor/Tartaruga)

1. Recuperar **log original** de pelo menos uma passagem do 528: objeto,
   estação e código do sensor; data/escala temporal e época do registro;
   observáveis efetivos (ângulos, alcance, taxa de alcance) e unidades.
2. Recuperar posição geodésica/datum do sensor em 1963, calibração, modelo
   e quadro de referência, precisão por observável e erros sistemáticos;
   identificar reduções e transformações até elemento catalogado.
3. Determinar dependência entre sensores e entre boletins NASA, catálogo
   NORAD e espelho TLE C179#1. Congelar fit/holdouts 527/528/529 e
   confrontar modelo dinâmico e baseline com resíduos **em unidades**.
4. Só então promover um intervalo observado, com modelo de erro
   justificado, a predicado Lean e filtro numérico do Castor.

**Falta observação identificada:** (\mathrm{OBS}_{528} =
\{t, s, y, \Sigma_y, \mathrm{frame}, \mathrm{source}\}\) com log primário,
época, sensor e covariância. A pesquisa desta rodada **não** recuperou esse
conjunto. Erro orbital externo e holdouts instrumentais: **NOT_RUN**.
Domínio de parâmetros admissíveis físico **antes = depois**, sem exclusões
ou alegação de não-vazio novo; nenhuma hora, posição ou probabilidade
terminal calculadas. Não criar novo teorema Lean sem observável calibrado.

## Correção editorial distinta

A UI atual em `src/lib/constants.ts` inclui `OBS-02` com uma suposta
aquisição por radares Eglin/BMEWS em **17/01/1963 02:30 UTC** sem log
primário, e `OBS-04` como checagem SPADATS em julho sem medição.
**Não** usar esta nota para legitimar tais eventos ou promover números
do protótipo. A remoção do conteúdo exibido foi atribuída à 🦊 Raposa
na [issue #304](https://github.com/franklinbaldo/conde-incident/issues/304).
Preservar fontes e histórico de auditoria, mas não republicar hipóteses
sem suporte em forma de fato.
