---
type: Guide
title: "C149–C151: indicador seco de estabilidade e cisalhamento por camada, Recife 1963"
description: "42 pares condicionais de uma única família NOAA/IGRA; sem inferência local de turbulência, deriva ou queda."
---

# Recife em 1963: indicador de Richardson seco em camadas observadas

## Evidência, espaço e tempo

Três sondagens **NOAA/NCEI IGRA BRM00082900**, fonte histórica **ncdc6301**, 07, 08 e 09/11/1963 às **12 UTC nominais**. O código de horário real RELTIME=9999 indica **lançamento real desconhecido**. Fonte original: [ZIP IGRA da estação](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), SHA-256 0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc. [Dicionário do formato NOAA](https://www.ncei.noaa.gov/pub/data/igra/data/igra2-data-format.txt). O script reabre os três excertos com hashes individuais imutáveis, valida estação/data/horário/família, e relê pressão, temperatura, altura geopotencial e vento.

Recife: latitude **−8,05°**, longitude **−34,9167°**, cota catalogada **7 m**; a posição exata do instrumento em 1963 não foi verificada. As alturas em níveis são **metros geopotenciais acima do nível do mar**, não altitudes geométricas. O resultado agrupa 15 níveis com observações completas de temperatura, vento, pressão e altura em cada dia. Há **14 camadas entre os níveis consecutivos com vento por dia, 42 ao todo**. Camadas podem atravessar níveis intermediários sem vento, portanto não são 42 gradientes atmosféricos locais. As três datas pertencem à **mesma estação/família instrumental**, não constituem três fontes independentes. Reuso potencial em UADB não cria independência.

## Observable e hipóteses explícitas

Ar ideal seco e constantes de modelagem: R_d=287,05 J/(kg K), c_p=1004 J/(kg K), g₀=9,80665 m/s²; nível de referência 1000 hPa.

- Temperatura potencial de ponta: θ=(T_C+273,15) × (1000/p_hPa)^(R_d/c_p).
- Indicador de estabilidade seca entre pontas: N²_fd=(g₀/θ_média)×Δθ/ΔH, em s⁻².
- Cisalhamento quadrático entre pontas: S²_fd=(Δu²+Δv²)/ΔH², em s⁻².
- Richardson de diferença finita seca: Ri_fd=N²_fd/S²_fd, apenas se S²_fd for não nulo; senão, **null**.

São índices **derivados**, não observações de turbulência. O limiar crítico usado para o Richardson **local** não deve ser aplicado a diferenças finitas de grandes intervalos. Ver [Grachev et al., 2012](https://arxiv.org/abs/1202.5066) sobre limites dos limiares locais. A umidade medida não corrige esta hipótese seca; portanto a instabilidade seca calculada não prova instabilidade real, convectiva ou turbulência. Incerteza instrumental, resolução subcamada e erro espacial/temporal são **desconhecidos (null)**.

| Data nominal UTC | Camadas com p/T/GPH/vento | N²_fd negativo (hipótese seca) | Pressão do intervalo negativo |
|---|---:|---:|---|
| 07/11/1963 | 14 | 1 | 1016–1000 hPa |
| 08/11/1963 | 14 | 1 | 1016–1000 hPa |
| 09/11/1963 | 14 | 1 | 1016–1000 hPa |

Esse padrão pode orientar **apenas** a seleção de cenários físicos locais condicionais de Recife. Não é medição de mistura, coeficiente de difusão, trajetória ou estabilidade em Conde.

## Vínculos cumulativos e não conclusões

**C149–C151 (uma família IGRA: p,T,H,u,v)** → θ seca / N²_fd / S²_fd → Ri_fd **CONDICIONAL** → eventual caracterização de transporte de fragmentos em Conde **PENDING** (sem campo regional, covariância, hora real, trajetória ou escala de transferência). Nenhuma região geográfica fica excluída.

**C144–C146** representam mapas sinóticos superficiais da Marinha, não gradientes co-locais de altitude; **C17–C23** documentam índices solares/geomagnéticos sem medir o vento inferior em Conde; **C193** decorre de medições termoesféricas de abril–junho de 1963 e não calibra este perfil inferior em novembro. As incertezas permanecem explícitas e não transformam coincidências de fonte em corroboração.

Reprodução local:

    python3 tools/audit_igra_recife_dry_richardson.py --check
    python3 -m unittest discover -s tests -p test_igra_recife_dry_richardson.py -v

O [JSON](igra_recife_19631107_09_dry_richardson.json) preserva pressão, temperatura, alturas e observáveis derivados em cada uma das 42 camadas; o script recompõe a saída exclusivamente dos excertos originais pinados. Nenhuma simulação do Castor foi modificada.
