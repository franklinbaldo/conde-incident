---
type: Guide
title: 'G63: erro óptico correlacionado entre duas câmeras'
description: 'Propagação condicional de covariância conjunta, sem inventar erro instrumental calibrado de 1963.'
---

# G63: duas câmeras não significam duas incertezas independentes

O G62 compartilha corretamente o estado orbital latente entre duas direções.
Mas sua matriz de variância diferencial é **exclusivamente orbital**, não a
incerteza total de uma observação real. O G63 oferece um caminho condicional
para acrescentar erros de medição *correlacionados entre receptores*.

O argumento opcional receiver_noise_covariance_common_tangent_4d_rad2 é
uma matriz **simétrica, positiva semidefinida, 4×4**, em radianos quadrados,
na ordem (A-eixo1, A-eixo2, B-eixo1, B-eixo2), projetada sobre a **mesma
base tangente GCRS congelada** do G62. Os blocos cruzados representam erro
compartilhado de redução/calibração astrométrica. Correlação zero é hipótese
explícita, não um padrão implícito.

Se D = [I2, -I2], J = J_A - J_B e Sigma6 é a covariância orbital 6D:

- Cov_orbita = J Sigma6 J-transposta.
- Cov_receptores = D Cov_AB D-transposta.
- Cov_total = Cov_orbita + Cov_receptores **somente quando o chamador
  especifica assume_receiver_state_independent=True**.

A última hipótese diz que a estimação da órbita não compartilhou erros com
a redução astrométrica. O contrato **não** a deduz de um arquivo de filme.
Sem matriz dos receptores: status UNSPECIFIED_NOT_ZERO, Cov_total ausente.
Com matriz, mas sem declaração da independência do estado orbital:
Cov_receptores fica disponível e **Cov_total continua ausente**. Isso evita
uma posterior artificialmente precisa por omissão de covariância cruzada.

Os controles sintéticos testam correlação perfeita positiva (erro comum
cancela), correlação zero (soma dos erros), anticorrelação perfeita
(amplificação), PSD singular legítima e rejeição de matrizes não PSD,
não simétricas, de dimensão errada ou não finitas. O módulo Lean
CorrelatedReceiverNoise formaliza a identidade escalar dos termos cruzados,
e mostra dois erros opostos do atalho diagonal. A prova estrutural **não autentica**
a matriz fornecida pelo usuário nem substitui o validador numérico 4×4.

## Fontes faltantes e ativação

Não foram recuperados: filme 1963 identificado como NORAD 528,
carimbo UTC e base de tempo calibrados, levantamento da estação, frame
instrumental FK4/B1950 convertido para GCRS, covariância astrométrica nem
origem conjunta de medição e órbita. Não assumir que duas previsões
derivadas do mesmo catálogo são duas observações. As condicionais 1963
não ativam likelihood histórica ou filtro de Theta. Histórico
NOT_AUTHENTICATED; holdout NOT_RUN; Theta permanece UNCHANGED.
