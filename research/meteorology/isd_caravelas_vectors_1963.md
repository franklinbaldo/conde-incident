---
type: Guide
title: "Caravelas em 1963: vetor de vento de superfície e média escalar"
description: "Derivação reprodutível de componentes u/v a partir dos 72 registros horários NOAA/ISD, com incertezas e transferência territorial pendentes."
---

# Caravelas, 7–9 de novembro de 1963: vento vetorial não é velocidade escalar

**Delta de observável (13/11/2026).** O controle costeiro de superfície de Caravelas [NOAA/ISD, 834970-99999](https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz), já custodiado no [manifesto horário](isd_caravelas_19631107_09.json) e vinculado à [genealogia divergente de coordenadas](isd_caravelas_station_lineage_1963.md), informa velocidades e direções a cada hora UTC de 7 a 9/11/1963. A média **da velocidade escalar** não é a magnitude **do vetor médio**; para uso físico, componentes devem respeitar direção meteorológica **de onde** sopra o vento.

Para direção θ em graus a partir do norte e velocidade não negativa s em m/s, a convenção de componentes horizontais é `u = −s·sen(θ)` (positivo para leste) e `v = −s·cos(θ)` (positivo para norte). Em calmarias `s=0`, o código de direção não representa orientação física. A direção resultante é calculada somente quando a magnitude média não é zero. O fator `|média(u,v)| / média(s)` mede cancelamento vetorial no período, **não acurácia, erro instrumental, persistência demonstrada em outro local ou probabilidade**.

| Dia UTC | Média escalar (m/s) | u médio leste (m/s) | v médio norte (m/s) | Magnitude média (m/s) | Vento médio **de** (graus) | Fração resultante | Horas calmas |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07/11 | 3,367 | −2,709 | −1,702 | 3,199 | 57,9° | 0,950 | 0 |
| 08/11 | 3,367 | −2,334 | −2,382 | 3,335 | 44,4° | 0,990 | 3 |
| 09/11 | 3,775 | −2,372 | −2,812 | 3,679 | 40,1° | 0,975 | 1 |

Esses resultados são **derivados dos mesmos 72 registros retrospectivos NOAA**, não três fontes independentes. Os códigos digitais de qualidade ISD iguais a `1` não são desvio-padrão instrumental nem certificação de altura/exposição do sensor em 1963. A [posição codificada do próprio arquivo](isd_caravelas_station_lineage_1963.json) conflita com o catálogo retrospectivo em 2,136489 km, sem data instrumental autenticada. Logo, nem vetor médio nem direção resultante podem ser extrapolados para vento sobre Conde, altitude de reentrada ou trajetória do objeto.

O [grafo incremental](../constraints/isd_caravelas_vector_edges_1963.json) liga a derivação `speed/direction → u/v → média diária` à transferência espacial ainda **pendente**. As covariâncias, o `sigma` de medição, a função de transferência Caravelas→Conde e qualquer domínio de queda continuam **desconhecidos/nulos** (`CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION`). O valor negativo de `u` e `v` descreve transporte horizontal **para sudoeste em Caravelas** nos horários médios, não transporte do satélite ou da notícia de Conde.

## Verificação reproduzível

- `python3 tools/audit_isd_caravelas_vectors_1963.py --check` reproduz o JSON do recorte com hash SHA-256 `c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000` e compara com as médias originais já publicadas.
- `python3 -m unittest discover -s tests -p 'test_isd_caravelas_vectors_1963.py' -v` verifica sinais u/v, calmaria, 24 horas em cada dia, QC, datas e impossibilidade de promover a transferência a restrição numérica.
- O workflow existente `isd-caravelas-1963.yml` fixa o SHA do HEAD e, além dos testes vetoriais, compara novamente as 72 linhas com o arquivo GZIP NOAA anual integral; hash do arquivo original `c4a0b2f625e8febcd03c4b6ca6ac37b91c9d38423a2ccddd6f0cd7a7712e7e05`.

**Próximo teste físico:** recuperar medidas costeiras realmente independentes e contemporâneas na Bahia, bem como a ficha operacional do anemômetro, para estimar covariância e erro de transferência antes de alimentar o Castor.
