# 🦌 Cervo: auditoria de RAAN circular e épocas comparáveis

**Pergunta:** o catálogo secundário NORAD 527/528/529 contém pares de elementos com épocas suficientemente próximas para compará-los sem fingir medidas simultâneas? Quanto a contagem de dados superestima a amostra ao incluir registros duplicados?

**Fontes e custódia.** Matriz C25#1, C179#1, C180#1, C181#1 e C241-L1. Derivado do [histórico Space-Track espelhado em Hugging Face](https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/main/data/tle_1963.parquet), hash SHA256 do parquet **declarado pelo extrato anterior**, c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. JSON intermediário já existente no Jatobá: SHA256 9f6710dd008c5e65845672a6e535ccf991c2832492c4ecd30399122155fcb24b. Os registros mínimos de NORAD ID, época e RAAN estão em raan_527_528_529_1963.json; são **dados derivados de uma única linhagem**, não TLEs originais. O parquet original **não foi baixado nem revalidado por hash nesta rodada**.

**Resultado factual reprodutível:** 123 linhas brutas representam **119 épocas únicas**. NORAD 527 tem 21 linhas / 20 épocas (1 duplicata exata), NORAD 528 tem 45/45 (0), NORAD 529 tem 57/54 (3). No extrato intermediário, as quatro linhas repetidas são idênticas em todos os campos. Esses valores confirmam os contadores do núcleo Lean em formal/Conde1963/Core.lean (20+45+54=119); não convertem as épocas em medições instrumentais independentes.

## Pareamento descritivo, sem propagação orbital

Usamos a diferença circular assinada de RAAN \(\Delta\Omega=\mathrm{wrap}_{[-180^\circ,180^\circ)}(\Omega_a-\Omega_b)\) e pareamento um-a-um, guloso e determinístico pela menor diferença de época, dentro de limiares predeclarados. Não interpolamos, não modelamos precessão J2, não imputamos TLEs faltantes e não usamos uma mesma observação duas vezes no mesmo par. Os limiares são **regras de exploração**, não incertezas estimadas.

| Par | Até 10 min | Até 1 h | Até 6 h | Até 24 h |
|---|---:|---:|---:|---:|
| 527–528 | 0 | 1 | 2 | 5 |
| 528–529 | 1 | 3 | 6 | 15 |
| 527–529 | 0 | 1 | 3 | 7 |

O primeiro par 528/529 (17/01/1963, 16:18:12.350304 e 16:20:21.950304 UTC) apresenta intervalo de **129,6 s** entre épocas e diferença circular de RAAN **+0,0014°**. Isso documenta um alinhamento dos **elementos catalogados**, não a precisão dos elementos, a distância real entre corpos, nem um prior validado de posição. Em 27/10 14:40:16 UTC (528), o 529 mais próximo na janela de 24 h é de 28/10 04:51:52 UTC: diferença temporal de **14h11m35,94048s**, RAAN circular **−2,8122° sem transporte dinâmico**. Não é uma comparação coetânea em outubro e não permite localizar reentrada em 8/11.

## Por que nenhuma posterior histórica foi calculada

Um posterior MCMC exigiria parâmetros livres \(\theta\), um prior explicitamente justificado \(p(\theta)\), dinâmica do Castor \(H(\theta,t,\mathrm{frame})\), modelo de erro e covariance \(\Sigma\) empiricamente calibrado, proveniência de sensores e verossimilhança circular. Copiar espelhos/épocas ou repetir quatro linhas **não** cria observações independentes. A covariância comum da linhagem histórica e o estado observado em épocas distintas precisam ser tratados conjuntamente. Os 119 registros únicos não são 119 sensores independentes.

No arquivo disponível não existe TLE de 528 em 08/11. A evidência NASA C197 fornece somente a **data catalogada** de decaimento, não hora/local física. Estado: likelihood 1963, prior físico 1963, posterior MCMC, convergência, holdout e redução do domínio admissível **NOT_RUN**. O resultado aqui é **diagnóstico empírico de qualidade de amostra e lacuna temporal**; não valida Conde nem outro local.

**Próximo elo:** Tartaruga deverá obter custódia, frame e limites instrumentais/covariância dos elementos. Castor terá de propagar estados ao mesmo instante e quantificar erro em holdouts 527/529 versus baseline. Cervo então implementará likelihood circular com erro comum por linhagem, priors auditáveis e diagnósticos de cadeias, sem inferir coeficiente balístico ou impacto a partir de amostragem arbitrária.

**Reprodução local e no CI:** executar Python unittest no arquivo tests/test_raan_coepoch_audit.py, depois tools/raan_coepoch_audit.py com as opções --input research/statistics/raan_527_528_529_1963.json e --check research/statistics/raan_coepoch_1963_report.json. Nenhuma dependência externa nem busca de rede é necessária.

## Protocolo temporal de avaliação futura

O [manifesto de partições por época e NORAD](raan_chronological_holdout_1963.json) e seu [contrato estatístico](CHRONOLOGICAL_HOLDOUT_PROTOCOL.md) congelam 61 épocas de ajuste, 23 de validação e 35 de avaliação após remover as quatro duplicatas do **mesmo** extrato. Os cortes 01/08 e 01/10 são operacionais, escolhidos após inspeção prévia: o bloco final **não é cego**, nem independente do catálogo; nenhum ajuste, likelihood ou MCMC foi executado. Para reexecutar, use python3 -m unittest discover -s tests -p 'test_raan_chronological_holdout.py' -v e o comando --check documentado no protocolo.
