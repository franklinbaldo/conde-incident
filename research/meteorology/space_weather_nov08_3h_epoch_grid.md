# 🦎 Grade trihorária condicional de 8 de novembro de 1963

**Estado: CONNECTED_PENDING_CALIBRATION.** O NORAD 528 tem um dia de decaimento catalogado, mas não uma hora ou local observado. Os oito inícios de bins de 3 h (00, 03, 06, 09, 12, 15, 18 e 21 UTC) são escolhas para avaliar os índices do dia, **não** oito horários observados, cenários de queda geográfica ou probabilidades. O arquivo JSON ao lado preserva os sete componentes de histórico ap por início de bin, sem densidade ou vento local inventado.

## Proveniência e independência

- [GFZ Potsdam](https://kp.gfz.de/en/data): índices definitivos Kp e ap por intervalos UTC de 3 h, e Ap médio diário. APIs originais com URLs, hashes e tamanhos no arquivo space_weather_msise_inputs_1963_11_07_09.json. Kp, ap e Ap são uma **família dependente** de observações planetárias, sem posição específica e sem altitude física; erro e covariância histórica desconhecidos.
- [Natural Resources Canada](https://www.spaceweather.gc.ca/solar_flux_data/daily_flux_values/F107_1947_1996.txt): série canadense F10.7 observada em sfu, independente enquanto variável instrumental dos índices magnéticos. Em 8/11, F10.7 de **7/11 = 76,6 sfu**, e média centrada de 81 dias observados = **82,265432 sfu**. A média retrospectiva usa datas posteriores. CelesTrak é republicador, não uma terceira medição.
- [Contrato NRLMSISE-00](https://github.com/magnific0/nrlmsise-00/blob/master/nrlmsise-00.h): histórico de sete valores ap = Ap diário; ap dos bins t, t-3h, t-6h, t-9h; médias dos oito bins t-12..33h e t-36..57h. **Kp**, quase logarítmico, não pode substituir ap linear.

## Índices planetários observados para cada início de intervalo UTC

| Intervalo UTC | ap 3h | Kp 3h |
|---|---:|---:|
| 00–03 | 56 | 5,333 |
| 03–06 | 67 | 5,667 |
| 06–09 | 80 | 6 |
| 09–12 | 32 | 4,333 |
| 12–15 | 32 | 4,333 |
| 15–18 | 39 | 4,667 |
| 18–21 | 32 | 4,333 |
| 21–24 | 27 | 4 |

Ap diário = **46**, embora ap trihorário varie de **27 a 80**. Essa amplitude é de **índices geomagnéticos**, não limite de densidade, arrasto ou trajetória. Não há independência entre os oito bins da mesma série instrumental.

**Contraste com evidências:** C17–C23 descrevem índices e limitações do benchmark; C144–C146 são cartas de pressão de superfície CHM; C149–C151 são perfis em Recife com horário real do lançamento não determinado; C193 mede outra época (abril–junho de 1963). Não são observações da densidade ou dos ventos em Conde em novembro.

**Ponte ao Castor:** índices históricos -> drivers de NRLMSISE-00 por época -> densidade condicionada a tempo exato, latitude, longitude, altitude, hora solar local e modelo de erro -> arrasto condicionado a estado orbital e coeficiente balístico. Os campos ainda desconhecidos permanecem null, e não se ativa qualquer restrição de parâmetro. Exibir estes oito bins não equivale a conhecer a hora da reentrada, e a variação dentro de cada bin não é aqui medida.

**CI e reprodutibilidade offline:** executar 'python3 tools/derive_1963_nov8_epoch_grid.py --check' ou 'python3 tools/validate_1963_space_weather.py'. O workflow já existente Historical space-weather driver audit executa o segundo comando e confere o arquivo agregado byte a byte na semântica. Alteração indevida de qualquer bin, F10.7, Kp, ap, vetor, nulidade ou proveniência falha o gate.
