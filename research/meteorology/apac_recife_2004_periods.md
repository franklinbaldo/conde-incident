---
type: Guide
title: "Recife 82900: períodos distintos por variável em catálogo estadual"
description: "Controle de cobertura superficial retrospectiva de 2004 sem transportar médias agregadas para a radiossonda de 1963."
---

# Cobertura por variável não é observação de novembro de 1963

O Governo de Pernambuco publicou em **novembro de 2004** o Tomo I dos *Estudos Hidro-Climatológicos Complementares*, [PDF hospedado pela APAC](https://www.apac.pe.gov.br/images/media/1642199099_Tomo%20I%20-%20Completo.pdf). As tabelas 1.4, 1.7, 1.8 e 1.9 identificam **82900, Curado (Recife) - INMET**, com coordenadas catalogadas -8,0500°, -34,9167° e diferentes janelas de dados de superfície. Elas não certificam as coordenadas de um lançamento em 1963.

| Tabela e variável | Período do catálogo | Média agregada | Meses com dados / total reportado | Nov/1963 na janela |
|---|---|---:|---:|---|
| 1.4 Temperatura mínima | mar/1961 a dez/1978 | 21,6 °C | 185/216 | Sim |
| 1.7 Umidade relativa | mar/1961 a dez/1978 | 77,7% | 186/216 | Sim |
| 1.8 Velocidade do vento | mar/1961 a dez/1978 | 2,6 m/s | 185/216 | Sim |
| 1.9 Pressão atmosférica | **ago/1966** a dez/1978 | **1011,9 hPa** | 124/156 | **Não** |

**Resultado negativo relevante:** a série compilada de **pressão superficial** começa em agosto de 1966. A média de 1011,9 hPa desse intervalo não pode ser transformada em pressão observada em novembro de 1963. Para temperatura, umidade e vento, estar dentro da janela tampouco garante observação do mês ou do dia 8, pois as tabelas contêm falhas e não apresentam índices mensais de presença. Médias do período inteiro não são valores de 1963.

**Custódia e incerteza:** a inspeção foi feita na **camada textual indexada** do PDF governamental consultada em 13/11/2026 UTC. Download do PDF e captura visual da página falharam por timeout nesta execução; não há SHA-256 do PDF e as quatro linhas exigem conferência visual futura. O SHA-256 no JSON autentica apenas o TXT de transcrição rotulada, que não deve ser confundido com bytes de fonte original. O documento é uma compilação de dados INMET retrospectiva (2004), não um catálogo de radiossonda publicado em 1963. Sua independência instrumental em relação à família de registros NOAA/IGRA não foi demonstrada.

**Grafo cumulativo:** APAC-PE-2004 tabelas 1.4/1.7/1.8/1.9 → C149, C150, C151, C193 → cobertura superficial por variável → presença mensal em 11/1963 (PENDING) → identidade estação/sonda de 1963 (PENDING) → erro de transferência Recife–Conde (PENDING) → possível entrada de arrasto/deriva no Castor (PENDING). **Nenhuma restrição física ou geográfica foi promovida**, nenhuma observação local de Conde foi inventada. Estado: CONNECTED_PENDING_CALIBRATION.

**Reprodução:** o script tools/audit_apac_recife_2004_periods.py lê a transcrição, regenera o JSON e oferece a opção --check. Testes em tests/test_apac_recife_2004_periods.py refutam retrodatação da pressão, média inventada para 8/11/1963 e promoção a observação instrumental. A etapa seguinte é autenticar o PDF completo e procurar o registro WMO contemporâneo a novembro de 1963, sem confundir registros de superfície e altitude.
