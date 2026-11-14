---
type: Guide
title: "C241-L65: errata visual da identificação 1962 Omega 1"
description: "Corrige prefixo transcrito no C241-L64 sem alterar o original histórico, as datas ou inferir identidade instrumental"
---

# C241-L65: corrigir o nome sem fabricar uma medição

A reinspection visual da [página impressa 15, página PDF 17](https://ntrs.nasa.gov/api/citations/19640003479) do *Satellite Situation Report* NASA/GSFC vol. 3 nº 24, publicado em 15/12/1963, mostra **`OMEGA 1`**, sem a letra `A` inicial que consta na transcrição do [C241-L64](nasa_ssr_terminal_control_308_C241-L64.md). Os vizinhos na coluna de objetos são `OMEGA 2`, `OMEGA 3` e, **depois**, `A BETA 1`. Todos pertencem à seção `1962 LAUNCHES (CONT'D)`. A linha `OMEGA 1` traz `US`, lançamento `18 JUN` e decaimento editorial `29-30 OCT 63`.

A distinção não é meramente ortográfica. A compilação [UN indexada por McDowell](https://planet4589.org/space/un/un_taba1.html) registra separadamente `1962 A Omega 1` como **Cosmos 9 (URSS; lançamento em 27/09/1962)**. Essa compilação é secundária para o presente teste, não prova primária de NORAD 308. Confundir as designações misturaria objetos de países e lançamentos diferentes.

**Proveniência:** NTRS 19640003479, PDF SHA-256 `d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f`, índice de página zero-based 16; verificação por imagem do fac-símile e comparação das linhas contíguas em 14/11/2026. O [JSON C241-L65](nasa_ssr_omega1_corrigendum_C241-L65.json) é uma correção **aditiva**, referenciando explicitamente o valor legado incorreto; o JSON C241-L64 e sua integridade histórica permanecem inalterados.

A leitura `OMEGA 1` é original quanto ao **rótulo impresso**, não quanto ao número NORAD: o boletim não imprime `308` nem `1962-024A`. A ligação ao FTV 2312/NORAD 308 permanece por catálogo secundário, assim como antes. As datas `29–30 OCT 63` não mudam; os resultados matemáticos condicionais de R61/R62 conservam as mesmas larguras, sem gerar observação independente, hora UTC, sigma, MCMC ou restrição sobre Conde.

O verificador [R63](../../tools/c241_ssr_omega_corrigendum_r63.py) exige a transcrição antiga intacta na evidência C241-L64 e a nova transcrição correta no adendo. Contraprovas rejeitam confusão com `A OMEGA 1`, troca de país/lançamento, promoção de identidade NORAD, sensor e σ. **Próxima evidência:** crosswalk primário que associe NORAD 308 à designação de 1962, e documento de decaimento com relógio/sensor/erro.
