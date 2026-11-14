---
type: Experiment
title: "G76: sensibilidade dos planos 528/637 a dois nós OSM e aos ramos de relógio FBIS"
description: "Contraprova geográfica contemporânea sem vincular plano orbital, carimbo jornalístico ou reentrada a um evento observado em 1963"
experiment_id: C241-G76-OSM-FBIS
verification_status: SECONDARY_LINEAGE_MODERN_PROXY_CLOCK_UNRESOLVED
---

# G76: mudar o ponto moderno quase não muda a hora do plano

**Questão (#870):** ao substituir a câmera moderna CGEO15 de 2022 por dois nós nominais OSM modernos, as janelas geométricas condicionais do NORAD 528 e do 637 mudam o suficiente para afetar o contraste de horas? E como interpretar o carimbo FBIS `2330 8 NOV 63` sem promovê-lo a hora do evento?

**Fontes e custódia:** saída base de [PR #892](https://github.com/franklinbaldo/conde-incident/pull/892): Parquet secundário SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, planos J2 com `a` constante e secante de `da/dt`; arquivos `research/statistics/c241_plane_{528,637}_*.json` e índice de proveniência. [CGEO-60, PR #935](https://github.com/franklinbaldo/conde-incident/pull/935): nós OSM `415521889` (Conde, −11,8129758; −37,6138705) e `4697713641` (Villa Velha, −11,7968448; −37,6214666), em 2026/2023. [C241-P48, PR #940](https://github.com/franklinbaldo/conde-incident/pull/940): `fbis_1963_clock_branches.json`, significado do relógio `UNRESOLVED`, zero âncoras independentes. O programa G76 valida os hashes dos três arquivos geográficos base, os identificadores e as coordenadas exatas dos nós OSM e as condições do contrato FBIS; a saída versionada registra os SHA-256 dos insumos.

**Operador e validação:** `tools/c241_plane_proxy_clock_g76.py` recompõe, sem baixar outro TLE, todas as raízes do produto `n·r_ECI=0` entre 6 e 9/11/1963, a partir dos quatro registros orbitais condicionais de #892. Confronta cada raiz com a câmera original (tolerância 1 segundo), troca apenas a latitude/longitude nominal, preserva os dois ramos J2 e os cortes no fim do dia NASA em UTC e Bahia. Os deslocamentos abaixo são calculados no executor externo, não horários de observação. O script e sua saída **não** estimam fase orbital, hora de reentrada, evento ou probabilidade.

| Modelo | Nó OSM Conde, deslocamento relativo à câmera | Nó OSM Villa Velha, deslocamento |
|---|---:|---:|
| 528, semieixo constante | −1,81 a −0,47 s | +0,56 a +0,78 s |
| 528, semieixo com secante de decaimento | −1,85 a −0,40 s | +0,02 a +0,89 s |
| 637, semieixo constante | −1,84 a −0,35 s | +0,11 a +1,07 s |
| 637, semieixo com secante de decaimento | −2,14 a −0,37 s | +0,05 a +0,88 s |

São diferenças inferiores a três segundos **entre três pontos contemporâneos**, não um limite para coordenadas históricas desconhecidas. Em contraste, as raízes nominais da câmera já divergiam por horas entre planos 528 e 637 no mesmo dia. A diferença de 1,975 km entre os dois nós OSM não prova ser a distância entre o centro e a vila em 1963.

**Relógio FBIS e sentido causal:** para a raiz vespertina do 528 em 08/11, a hipótese `GMT` localiza o carimbo de transmissão às 23h30 UTC. A raiz do plano nos dois nós modernos cai 12,93–13,58 minutos **depois** do carimbo, portanto não seria um fenômeno antecedente àquela transmissão **se** o fenômeno coincidisse com essa raiz e **se** o relógio representasse GMT. Na hipótese `RIO_LOCAL`, permitida pelo horário civil de Guanabara em 1963, o carimbo corresponderia a 09/11 01h30 UTC: a mesma raiz fica aproximadamente 106,4–107,1 minutos **antes**. Nenhuma dessas hipóteses está escolhida ou verificada, e um cruzamento de plano não equivale à passagem do satélite em fase. O ramo de horário `OTHER_UNVERIFIED` permanece nulo. Não é lícito excluir órbita com base nessa notícia.

**Reprodução:** `python3 tools/c241_plane_proxy_clock_g76.py --repo . --output research/statistics/c241_plane_proxy_clock_g76.json --check`; `python3 -m unittest discover -s tests -p 'test_c241_plane_proxy_clock_g76.py' -v` e repetir com `python3 -O`. Negativos alteram identificação histórica, coordenada, âncora do relógio, época do ramo, fonte geográfica base e raiz original para exigir falha. A saída é byte-a-byte determinística, menor que 20.000 bytes. A execução do CI deve mostrar testes descobertos e HEAD/SHA coincidente; nenhum verde com steps vazios vale como validação.

**Decisão:** `CENTRO20=NOT_EVALUATED_NO_CUSTODIED_POINT`; `VILA20=NOT_EVALUATED_NO_CUSTODIED_POINT`; `phase_constraint=NOT_EVALUATED`; `posterior=false`; `active_constraint=false`. A incerteza dominante permanece documental (local e tempo do fenômeno, fase orbital e identificação), não a escolha entre esses pontos modernos. Só observações independentes e uma hora documental efetiva podem reduzir o domínio histórico.
