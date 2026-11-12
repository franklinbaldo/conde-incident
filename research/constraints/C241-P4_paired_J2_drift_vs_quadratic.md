---
type: Guide
title: "C241-P4: J2 com deriva versus quadrático nas mesmas épocas"
description: "Falsificação pareada da extrapolação física C241-P3 com o controle empírico C241-T15; sem medição instrumental nova."
---

# C241-P4: o ganho P3 é específico ao J2 ou também à curvatura livre?

**Pergunta falsificável:** C241-P3, precessão secular J2 com inclinação, excentricidade e movimento médio extrapolados exclusivamente do FIT, supera o polinômio de grau 2 C241-T15, também treinado exclusivamente no FIT, quando ambos são avaliados **nas mesmas épocas** dos 527/528/529? Vitória universal é refutada se qualquer objeto tiver MAE maior. O quadrático ajusta três coeficientes e P3 ajusta três tendências de elementos antes do corte. Não se trata de sensores independentes.

**Proveniência e linhagem:** C25#1/C179#1/C180#1/C181#1, C241-P1#1, C241-P2#1, C241-P3#1 e C241-T15#1. [Parquet secundário oxzoid rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09; CSV derivado SHA-256 3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231. O [NASA SSR primário de 15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) documenta apenas o dia catalogado de reentrada, **não** qualquer RAAN ou sua precisão.

**Procedimento:** não ajustar nenhum parâmetro neste comparador. Reproduzir P3 e T15 no CI com os mesmos bytes CSV aferidos por hash e split congelado: FIT antes de 01/08/1963, validação ago–set, avaliação desde 01/10/1963. Exigir hash e época idênticos para cada um dos 35 alvos (527=4, 528=8, 529=23), recalcular MAE angular absoluto por objeto, diferença assinada MAE(P3) − MAE(quadrático), vitórias por época e conservar índices source_rows. Não escolher modelos com dados da avaliação e não juntar 529 como se fossem 23 sensores independentes.

**Valores já publicados em C241-P3 e C241-T15, ainda sujeitos a confronto pareado na CI desta PR:**

| NORAD | Holdouts | P3 MAE (graus) | Quadrático MAE (graus) | P3 menos quadrático (graus, arredondado) |
|---|---:|---:|---:|---:|
| 527 | 4 | 0,605430 | 0,075589 | +0,529841 (P3 pior) |
| 528 | 8 | 0,133510 | 0,683124 | −0,549614 (P3 melhor) |
| 529 | 23 | 0,477634 | 1,143077 | −0,665443 (P3 melhor) |

A comparação de erros assinados por época ocorre no artefato CI; os números acima são aproximados, derivados de outras PRs. Se identidade ou inventário divergir, falhar fechado. O 527 refuta a superioridade universal de P3. Os ganhos do 528/529 são **consistência interna do catálogo secundário**, não verificação independente de dinâmica orbital.

**Domínio físico e erros:** Theta antes = Theta depois; nenhum filtro físico ativado ou prova de não-vazio refeita. Os resíduos em graus medem diferença contra o espelho secundário, não erro instrumental ou localização. Faltam TLEs originais e rastreamento com épocas, quadros de referência, checksums, covariância e holdout independente. RAAN legado 284,1520° sem fonte permanece fora dos ajustes. Não acrescentar teoremas Lean sem restrição calibrada.

**Reprodução:** executar python3 -m unittest discover -s tests -p test_raan_p3_quadratic_pair.py -v. O workflow [.github/workflows/polvo-j2-frozen-long.yml](../../.github/workflows/polvo-j2-frozen-long.yml) baixa Parquet fixado, produz P3 e T15, compara via tools/raan_p3_quadratic_pair.py, arquiva JSON pareado e executa lake build e auditoria de axiomas Lean 4.35.0 no HEAD exato.
