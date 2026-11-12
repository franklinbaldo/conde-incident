# 🦌 Cervo: identificabilidade circular e dependência de linhagem

**Objeto desta fatia:** prova algébrica condicional, não uma inferência orbital histórica. Referências documentais da matriz cumulativa: **C25#1, C179#1, C180#1, C181#1 e C241-L3**; os dados de RAAN vêm do mesmo extrato secundário [Space-Track espelhado](https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/main/data/tle_1963.parquet). O parquet original não foi novamente baixado e o SHA dos dados originais é uma atribuição da extração anterior. A origem dos sensores, o referencial histórico e as covariâncias permanecem desconhecidos. A partição congelada é retrospectiva, **não cega**.

## Modelo que demonstra o problema

Considere, **apenas como contraexemplo estrutural**, a família de observações angulares
Omega_j(t) = wrap(f_j(t; parâmetros dinâmicos) + phi_j + b + epsilon_j(t)),
com phi_j uma fase orbital livre de cada objeto 527, 528 e 529, e b um deslocamento angular comum hipotético de linhagem. O operador físico f_j pertence ao Castor e **não** foi ajustado ou executado aqui. Erros epsilon_j(t) e b **não foram observados**, estimados nem demonstrados existentes.

Para qualquer rotação angular a, a transformação simultânea
phi_527, phi_528, phi_529 -> phi_527+a, phi_528+a, phi_529+a
e b -> b-a deixa TODAS as previsões circulares idênticas. Portanto, na parametrização com fase livre e offset comum, **os quatro parâmetros não podem ser identificados separadamente por essas observações**, mesmo com infinitas épocas. O jacobiano de localização simplificado possui colunas [indicador_527, indicador_528, indicador_529, constante_1], de posto 3 em vez de 4 e direção nula (1,1,1,-1). Essa é uma igualdade algébrica exata, independente de prior, ruído, orbitalidade ou época. Uma prior própria poderia induzir uma distribuição para a diferença, mas não forneceria identificação pelos dados.

O manifesto usa 61 épocas únicas de ajuste, 23 de validação e 35 de avaliação (123 linhas, quatro duplicatas removidas). O **posto 3** em cada bloco vem apenas do desenho hipotético e dos três objetos presentes, e **não** é posto da dinâmica real (que não foi executada).

## Cenários de correlação, com escopo rigorosamente limitado

Sob um segundo modelo **ilustrativo diferente**, suponha que n resíduos já corretamente transportados sejam medidas **homoscedásticas de UMA mesma média escalar conhecida quanto ao referencial/âncora**, com correlação equicomum rho não negativa. Então Var(média) / (sigma²/n) = 1+(n-1)rho e o número de réplicas de mesma informação da média é n_eff = n/[1+(n-1)rho]. O relatório computa isso por objeto e, separadamente, para o total de cada bloco *caso todas as épocas fossem resíduos de uma única média*. Não se deve somar por objeto ou aplicar esses números diretamente a parâmetros orbitais, tendências temporais, sensores desconhecidos ou resíduos circulares próximos à descontinuidade. Para angularidade, essa conta é apenas uma aproximação local em espaço tangente com ruído pequeno. **Isso não é ESS de MCMC.**

Os valores rho = 0, 1/10, 1/2 e 9/10 são cenários de estresse **escolhidos**, não priors, estimates de correlação histórica nem limites. Como ilustração, 61 réplicas teriam n_eff=61 na hipótese de independência; com correlação comum 1/10 teriam 61/7 ≈ 8,714; com 1/2 teriam 61/31 ≈ 1,968. Não atribuir nenhuma dessas probabilidades ou precisões ao incidente.

**Progresso:** conexão nova entre a estrutura hipotética de erros de C241-L3 e uma não-identificação explícita de fase versus viés comum; não há redução de domínio admissível nem conclusão sobre RAAN histórica 284,1520° versus 198,5261°. Tais ângulos têm proveniências e épocas conflitantes, não foram conciliados.

**Desbloqueio:** 🐢 Tartaruga: custódia de sensor, frame, cadeia de processamento e referência angular independente; 🦫 Castor: transporte físico validado entre épocas e conversão de estados em observáveis de catálogo, com erros numéricos; 🦌 Cervo: quando houver essas condições, comparar hipóteses de erro realmente justificadas, priors nomeadas e holdout, antes de qualquer MCMC ou posterior histórica.

## Reprodução e testes

Execute python3 tools/raan_lineage_identifiability.py --input research/statistics/raan_527_528_529_1963.json --split research/statistics/raan_chronological_holdout_1963.json --check research/statistics/raan_lineage_identifiability_1963.json e python3 -m unittest discover -s tests -p test_raan_lineage_identifiability.py -v. O comando usa aritmética racional exata para o posto e os cenários e verifica o SHA, a partição congelada e a semântica da linhagem; CI executa a suíte Python no SHA final da PR. Os casos de controle são sintéticos e **não criam novas observações**.
