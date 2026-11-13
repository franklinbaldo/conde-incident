---
type: Guide
title: "Caravelas: série horária de superfície em novembro de 1963"
description: "72 observações NOAA/ISD preservadas byte a byte, com controle de qualidade e ligação pendente à atmosfera de Conde."
---

# Caravelas, 7–9 de novembro de 1963: um controle meteorológico costeiro distinto

**Achado:** há **72 linhas horárias efetivas**, com horários UTC de `00:00` a `23:00` em **cada** um dos dias 7, 8 e 9/11/1963, na estação de superfície **Caravelas (USAF 834970 / WBAN 99999)**. A fonte é o [arquivo integral NOAA NCEI/ISD de 1963](https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz), uma **compilação digital retrospectiva**, não fotografia da ficha instrumental de 1963. Seus campos incluem vento, temperatura, ponto de orvalho e pressão reduzida ao nível do mar; não constitui radiossonda de altitude.

O arquivo integral capturado em 13/11/2026 possui SHA-256 `c4a0b2f625e8febcd03c4b6ca6ac37b91c9d38423a2ccddd6f0cd7a7712e7e05` (8.532 linhas no ano). As **72 linhas brutas originais**, com todos os campos adicionais e quebras de linha, foram extraídas sem normalização e preservadas de forma reversível em [base64 de zlib](isd_caravelas_19631107_09.zlib.b64), SHA-256 do trecho reconstruído `c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000`. Os bytes, flags, horários e cálculos foram confrontados com o GZIP completo. Os campos QA de vento, temperatura, orvalho e pressão exibem código `1` nas 72 linhas; **código QC não fornece sigma instrumental**.

| Dia UTC | Horas disponíveis | Vento de superfície (m/s, média) | Temperatura (°C, média) | Pressão nível do mar (hPa, média) |
|---|---:|---:|---:|---:|
| 07/11/1963 | 24 | 3,367 | 26,192 | 1010,938 |
| 08/11/1963 | 24 | 3,367 | 26,196 | 1011,121 |
| 09/11/1963 | 24 | 3,775 | 26,075 | 1008,400 |

O arquivo ISD relata vento à superfície, **sem garantir altura de 10 m** ou exposição específica do anemômetro em 1963. A conversão de velocidade e temperatura utiliza décimos nas posições fixas originais. Pressão é `SLP`, **não** pressão de estação. O relato contém mínimas/máximas e ponto de orvalho no [manifesto](isd_caravelas_19631107_09.json), que é reprodutível pelo parser.

## Cobertura e dependência

No [índice integral NOAA/ISD 1963](https://www.ncei.noaa.gov/pub/data/noaa/1963/) (SHA-256 do HTML capturado `93627d0e6010063fc54d6029d67499952107784f47740d895a17516e6dfb401d`), aparecem arquivos 1963 de Caravelas `834970`, Brasília `833780` e Belo Horizonte/Pampulha `835830`. Não aparecem arquivos para os códigos `828990` (aeroporto Recife), `829000` (Recife) ou `832290` (Salvador) **naquele produto e diretório**. O [cadastro ISD retrospectivo](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv) (SHA-256 `1994747ab4af1b97e63adb434b4d0d022f2daee76f0c144ea9ab46be2d906604`) associa Caravelas a uma posição catalogada no sul da Bahia; esta posição **não foi autenticada por levantamento de 1963**. Nem faixa de operação do cadastro nem ausência de arquivo em uma coleção provam inexistência histórica de observações.

Caravelas fica aproximadamente **663 km** da referência cartográfica usada no inventário IGRA (ponto médio da caixa envolvente IBGE 2022 de Conde, `-11,8641854, -37,6893514`), por Haversine; são coordenadas retrospectivas e uma distância apenas documental. É fonte de outra estação de **superfície**, potencialmente independente da família de sondagens Recife/IGRA C149–C151, mas sem auditoria concluída de dependências entre fornecedores da compilação. Não basta para calibrar vento em Conde, perfis de alta atmosfera, densidade, deriva ou horário de reentrada.

A [ligação cumulativa](../constraints/isd_caravelas_surface_1963.json) registra `Caravelas_surface_wind(t) -> [transferência a verificar] -> Conde_surface_wind(t) -> [trajetória e altitude] -> hipótese de queda`, com `CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION` e incerteza `null`. Há **72 observações horárias**, não 72 instrumentos independentes. Não foi ativada nenhuma restrição numérica para o Castor.

## Reprodução

```bash
python3 tools/audit_isd_caravelas_1963.py --check
python3 -m unittest discover -s tests -p 'test_isd_caravelas_1963.py' -v
curl -fL https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz -o /tmp/caravelas-1963.gz
python3 tools/audit_isd_caravelas_1963.py --check --verify-full-gz /tmp/caravelas-1963.gz
```

O gate CI deve executar a comparação do GZIP integral no **SHA da PR**, não apenas o snapshot local. Mudança de hash no servidor exige investigação comparativa; nunca atualizar checksum sem evidência. Próximo passo: identificar os instrumentos de superfície de 1963 e avaliar, por comparação com reanálise e fontes independentes da costa baiana, se alguma função de transferência é defensável, com incertezas explícitas.
