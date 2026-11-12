# 🦌 Cervo: conjunto temporal fixo para avaliar RAAN (sem inferência histórica)

**Estado:** RETROSPECTIVE_TIME_SPLIT_NOT_BLINDED; derivação do mesmo catálogo secundário Space-Track 1963, **não** uma observação ou um posterior. [Fonte do extrato](raan_527_528_529_1963.json), [congelamento exato dos membros](raan_chronological_holdout_1963.json) e [auditoria circular prévia](README.md). Evidências-base C25#1, C179#1, C180#1, C181#1 e C241-L3; o parquet compartilhado é uma única linhagem, não uma medição por época e por espelho independente. O SHA256 dos bytes do JSON está no manifesto; hash do parquet foi apenas citado por extração anterior, não inspecionado de novo aqui.

## Contrato de partição, não ajuste

Congelei **agora**, antes de calibrar uma futura verossimilhança, os intervalos em UTC com fronteiras aplicadas a **todos os objetos ao mesmo tempo**:

- **Ajuste (fit):** de 1963-01-01 (incluso) até 1963-08-01 (excluso).
- **Validação de desenho/modelo:** de 1963-08-01 (incluso) até 1963-10-01 (excluso).
- **Avaliação cronológica posterior:** de 1963-10-01 (incluso) até 1964-01-01 (excluso).

Os limites são **escolhas operacionais**, não datas de mudanças instrumentais, nem hipóteses físicas. Foram escolhidos após inspeção anterior das datas e dos elementos catalogados: **o terceiro bloco NÃO é cego nem avaliação independente**. Esta partição só congela desde já a regra para futura comparação dentro do material histórico já acessado. Se modelos/hiperparâmetros forem ajustados depois de olhar resíduos de avaliação, marcar explicitamente contaminação e criar novo protocolo. NÃO procurar novos cortes até maximizar performance.

| NORAD | Ajuste | Validação | Avaliação | Épocas únicas |
|---|---:|---:|---:|---:|
| 527 | 15 | 1 | 4 | 20 |
| 528 | 24 | 13 | 8 | 45 |
| 529 | 22 | 9 | 23 | 54 |
| **Total** | **61** | **23** | **35** | **119** |

O JSON original contém **123 linhas**, mas quatro são duplicatas idênticas (527: 1; 528: 0; 529: 3), eliminadas por NORAD + época. A partição tem cobertura exata 119/119 e nenhuma mesma chave (objeto, época) em blocos diferentes. A validação de 527 tem **somente 1 época** e não sustenta estimativas robustas de erro; qualquer cobertura ou comparação por objeto deve reportar tamanho e lacuna temporal. Nenhuma época de 528 disponível em 8/11/1963; os oito dados de avaliação de 528 terminam em 27/10. Mesmo um desempenho bom aqui não avalia previsão de reentrada de 8/11.

## Contrato para uma futura execução estatística

1. **Antes de treinar:** declarar objeto, época, referencial, transformação TLE/média→observable H(theta,t,frame) fornecida e validada pelo 🦫 Castor, calibragem e incerteza do 🐢 Tartaruga, identificador da linhagem instrumental, modelo de seleção/missingness, parâmetros/prior **explicitamente justificados**, família de erro circular e estrutura hierárquica de dependência compartilhada. Não substituir carência de sensores/covariâncias por sigma arbitrário. Um modelo puramente descritivo deve continuar rotulado como tal.
2. **Ajuste:** condicionar a verossimilhança apenas às 61 épocas de fit. Resíduos wrap(Ω_observado - H_Ω(theta,t,frame)), em um frame e época realmente comparáveis. Em presença de erros de linhagem comuns, **não** multiplicar fatores independentes por época sem uma hipótese defendida; a fase RAAN está no círculo S¹ e não em reta.
3. **Validação:** usar só as 23 épocas designadas para seleção de modelo ou eventual tuning, registrar todas as tentativas e comparações com baseline fixado anteriormente. A época isolada do 527 não pode identificar escala de erro. **Nunca** recalibrar em avaliação, nem escolher modelo depois de ver seu placar.
4. **Avaliação:** prever os 35 elementos retidos sem refit, com erro angular circular, horizonte de previsão, resultado por objeto e por época, tamanho da amostra e, somente **se** houver distribuições calibradas, log-score/coverage e posterior predictive checks. Comparar com baseline predefinido. Relatar falhas de holdout; não suprimi-las por reamostragem.
5. **MCMC somente depois:** iniciar cadeias dispersas, reportar sementes/versões, rank-R-hat, ESS bulk/tail, divergências, autocorrelação e checagens preditivas; quantificar sensibilidade a priors, modelo de erro e datas de corte **sem retreinar no bloco de avaliação**. Se faltar calibração, status NOT_RUN, não posterior. A data catalogada NASA C197 não é hora terminal observada e não deve ingressar como likelihood horária.

Este desenho **não quebra a dependência documental** de C241-L3: 119 épocas únicas não significam 119 observações independentes de instrumentos, e os três objetos compartilham catálogo e possivelmente erros comuns. Também não transforma RAAN circular em distância orbital 3D. A diferença entre RAAN 284,1520° sem proveniência e ~198,5261° da série secundária exige proveniência e épocas antes de qualquer unificação, nunca média.

**Teste e replay de evidência:** python3 -m unittest discover -s tests -p 'test_raan_chronological_holdout.py' -v; python3 tools/raan_chronological_holdout.py --input research/statistics/raan_527_528_529_1963.json --check research/statistics/raan_chronological_holdout_1963.json. Os testes usam **123 linhas históricas já registradas** para contagens; casos sintéticos apenas para lógica de fronteira, duplicata e adulteração. Nenhum arquivo remoto foi baixado nesta fatia, nenhuma posterior foi inferida e nenhuma nova observação foi criada.
