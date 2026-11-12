# 🐙 C179/C151: transformações físicas para testar restrições cruzadas

**Escopo:** PR #17, issue #15; fonte documental → variáveis com unidades → relações físicas → observáveis e erros → contrato ao Castor. Isto **não** é nova observação de Conde ou prova de reentrada. O arquivo de dados da matriz é fixado pelo Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7` (PR #1). O novo script `formal/scripts/physical_observable_bridge.py` lê C151 da matriz, valida o snapshot e emite um JSON reproduzível para a simulação condicional.

## Evidências realmente disponíveis

- **C179#1**, linha 839 da matriz: par TLE secundário atribuído à AFSPC, documentado no [espelho 528](https://www.itau.magnetic-declination.com/satellite/?s=528), época `1963-10-27T14:40:16.132512Z`, movimento médio `15.74901460 rev/day`, inclinação `81.8615°`, excentricidade `0.0017147`, RAAN `198.5261°`. Literal fixado em [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; comparação com Parquet da mesma família NÃO fornece uma medição independente ou covariância. RAAN 284,1520° do projeto legado **não é cenário ativo**.
- **C149–C151**, especialmente C151#1 linha 606: [NOAA/NCEI IGRA BRM00082900, Recife](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip), ingestão `ncdc6301`: 08/11/1963, perfil nominal de 12 UTC, sem hora real de lançamento (`RELTIME=9999`). Cinco níveis citados diretamente na matriz (850, 700, 500, 300, 250 hPa), vento em m/s e direção meteorológica `from`. São cinco níveis de **uma fonte**, não cinco confirmações independentes. O ZIP da NOAA não foi reinspecionado nesta implementação; a transcrição auditada da matriz é a entrada.
- **C144–C146**, Marinha do Brasil DHN/CHM, [cartas sinóticas de novembro de 1963](https://idem.marinha.mil.br/geonetwork/srv/api/records/9ea5e9a4-199d-4d14-8b55-682eb4daa211/attachments/Nov_1963.pdf), incluindo 08/11/1963 às 12 HMG. Isóbaras não bastam para produzir diretamente vento horizontal observado em Conde, muito menos vento vertical/superior.
- **C131#1/C197#1** são referências à mesma [NASA/Goddard *Satellite Situation Report*, 15/11/1963, p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), que registra o dia de decaimento, não a trajetória nem vento/local de queda.

## Encadeamento físico (não confundir mudança de unidade com observação nova)

| Entrada e transformação | Quantidade de saída | Fonte do valor | Estado científico |
|---|---|---|---|
| `n[rev/dia] × 2π/86400` | `n[rad/s]` | C179#1 | Conversão exata da unidade do valor informado |
| `a=(μ/n²)^(1/3)`, `h_p=a(1-e)−R_E` | `a≈6723,05 km`; `h_p≈333,38 km` | C179#1 + constantes declaradas do modelo | Proxy kepleriano de elementos médios TLE, NÃO posição osculadora observada |
| `dotΩ_J2=−(3/2)J2 n (R_E/[a(1−e²)])² cos(i)` | `dotΩ≈−1,173124071°/dia` | C179#1 + modelo gravitacional | Sensibilidade dinâmica de RAAN a `i,e,n,a`, não limite empírico de erro |
| `p[hPa] × 100` | `p[Pa]` | C151#1, Recife | Conversão exata de unidades, mesma medição |
| `u_E=−V sin(D_from)`, `v_N=−V cos(D_from)` | vento para leste/norte em m/s | C151#1, Recife | Vetor derivado da mesma observação, não vento em Conde |
| `ρ=p/(R_d T)` | densidade kg/m³ | Exigiria temperatura da mesma época/local/altitude e modelo de ar | **NOT_RUN** nesta extração; não supor temperatura/pressão em Conde |
| `β=m/(Cd A)`, `a_drag=−(ρ/(2β)) |v_rel|v_rel` | parâmetro balístico e aceleração | Requer massa, área, Cd, estado e ρ; **não observados** |
| `Δr_horizontal=∫ u(z)/v_descida(z) dz` | deriva sob perfil, altitude e velocidade definidos | C151#1 apenas como proxy Recife | Sensibilidade condicional, **não** posição de fragmento em Conde |

Para tornar concreto o último cálculo sem **inventar uma medição**, o script exige que o operador forneça explicitamente a velocidade vertical constante. Sob **hipótese de 50 m/s de descida** e interpolação trapezoidal dos cinco ventos de **Recife** entre alturas **aproximadas** de 11,00 km (250 hPa) e 1,56 km (850 hPa), o tempo condicional é 188,8 s; a deriva calculada é cerca de **871 m para oeste e 1.000 m para norte**, magnitude **1.326 m**. O cálculo não cobre o trecho inferior a 1,56 km, nem assume que o objeto esteve em Recife ou que sobreviveu à reentrada. **50 m/s não foi medido** nem é uma estimativa da velocidade de qualquer fragmento real. Dobrar a descida hipotética para 100 m/s divide o deslocamento por dois; o teste automatizado confirma essa sensibilidade.

A simulação anterior de balão na matriz estimou ~31 km durante **ascensão** no perfil mais completo de Recife a 5 m/s de subida. É outro intervalo vertical e outro cenário; não se deve confrontar 31 km e 1,326 km como duas previsões rivais.

## Critérios para restringir a órbita ou a hipótese de queda

1. A escala orbital (~7,7 km/s) é muito distinta dos ventos meteorológicos (m/s). Vento superficial ou mesmo tempestade intensa pode alterar **deriva após desaceleração atmosférica** de um fragmento/artefato ou trajetória de um balão; não anula diretamente o plano orbital ou a RAAN do 528. Incompatibilidade exige especificar qual observação, fase de voo, velocidade relativa, massa/área, altitude, horário, posição e erro foram comparados.
2. Para empregar um vento medido em Recife como restrição em Conde, é preciso uma reconstrução meteorológica defensável em 8/11/1963 com transferência espaço/tempo/altitude e incerteza. Essa ponte NÃO existe: `cross_location_transfer_to_conde=NOT_VERIFIED`. As cartas sinóticas da Marinha podem servir de informação regional, mas não substituem um perfil local de vento sem um modelo validado.
3. Uma cadeia de Markov exploratória pode variar `Ω₀,i,e,n,β,ρ(φ,λ,z,t),u(φ,λ,z,t)`, **apenas** com domínios/priors explicitados. MCMC com interpretação posterior exige verossimilhança, dependências entre fontes, erros calibrados, testes de convergência/mistura, controle de holdout. Até lá, reportar sensibilidade/resíduos e conjunto de soluções possíveis, não porcentagens de "queda em Conde".
4. O próximo teste que efetivamente reduziria parâmetros exige observações contemporâneas com erro e coordenadas/altitudes, ou modelo meteorológico regional validado; usar esses dados para impor limites ao deslocamento/arrasto de **um estado orbital candidato já definido**. A ligação ao Castor deve produzir intervalos antes/depois e demonstrar não-vazio, não só flags.

## Reproduzir no HEAD da PR

```sh
python3 -m unittest discover -s formal/tests -v
python3 formal/scripts/physical_observable_bridge.py \
  --matrix research/evidence_matrix_C001-C238_2026-11-11.md \
  --descent-vertical-speed-mps 50 \
  --output /tmp/conde-physical-observables.json
(cd formal && lake build && lake env lean Conde1963/AxiomAudit.lean)
```

O workflow `.github/workflows/science.yml` anexa `conde-physical-observables.json` ao artefato `conde-evidence-contracts` para o Castor. **Resultado atual:** transformação C179/C151 reproduzida; **nenhuma redução do domínio do NORAD 528 demonstrada**; vento local de Conde/erro de transferência ainda ausentes. Sem blog, publicação, contato, merge ou reconstrução fictícia.
