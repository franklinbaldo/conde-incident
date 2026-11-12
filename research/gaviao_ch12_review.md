# 🦅 Caderno 12: auditoria geométrica independente de C241-T10

**Status da auditoria:** novo achado editorial **G12-B1, bloquear parecer factual da PR #62 até correção**. Issue-mãe #16; retoma PR #60 e o bloqueio G11-B1 agora corrigido em #59. Esta análise é separada da interpretação de dados da Tartaruga e da redação da Coruja.

## Quatro eixos independentes de revisão

### 1. Autenticidade documental e dependência

- **Vetor legado**: `src/lib/constants.ts`, blob Git `0284f1217557b0ea891b5e51b6ac56bd13529d3f`, ref `c84cce85e51252f9e589a851950385aea008e951`. São linhas TLE *sintaticamente válidas*, mas sem original instrumental de 1963. O checksum **não** atesta origem, referencial nem acurácia.
- **Par moderno secundário**: [mirror do 528](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/research/tle_custody/mirror_528_1963-10-27.tle), SHA256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; a [matriz cumulativa, ocorrência C241-T10](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/research/evidence_matrix_C001-C238_2026-11-11.md) também pinou Parquet 1963 `4b4fb3a` e seu digest. São séries possivelmente **da mesma linhagem**, não observações de dois radares independentes.
- **NASA**: [*Satellite Situation Report* 15/11/1963, PDF página física 10, índice zero 9, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10) inspecionada visualmente nesta revisão. Em `DECAYED OBJECTS`, `1963 3B` consta `8 NOV 63`. É uma **data catalogada**, sem hora ou latitude/longitude. C131/C197 e a ficha C198 se referem ao mesmo boletim, não sensores independentes. A PR #61 corrige o índice PDF antigo da matriz (8 → 9).
- **FBIS**: [FBIS 03 p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), imagem inspecionada. `RADIO TUPI ... 2330 8 NOV 63 W` e corpo do relato sobre uma esfera, quatro metros de profundidade e corpo humano. É documento de *transmissão de notícia*, não uma observação no solo ou relatório instrumental. C01/C02 são uma cadeia, não testemunhos autônomos. Não reinterpretar `2330` como hora da queda.

### 2. Coerência matemática e limite Lean

A auditoria independente `tools/gaviao_ch12_plane_geometry.py` usa apenas Python padrão, baixa **duas revisões imutáveis** de GitHub e valida Git blob SHA-1/arquivo SHA-256 antes de analisar campos em largura fixa, checksums e épocas decimais. Não importa código da Tartaruga nem fabrica elemento orbital.

- Legado `1963-10-27T14:39:59.999904Z`; espelho `1963-10-27T14:40:16.132512Z`: diferença **16,132608 segundos**.
- Inclinação escrita **81,8615°** em ambos; RAAN escritos `284,1520°` e `198,5261°`: distância circular **85,6259°**.
- **Achado G12-B1:** a separação entre *planos orbitais* não é a diferença entre RAAN. Se os campos descrevessem planos convencionais **no mesmo referencial** e inclinação, o ângulo entre normais é
  `arccos(cos(i1)cos(i2) + sin(i1)sin(i2)cos(Ω1−Ω2))`
  = **84,5612921°**, NÃO mais de 85°. A diferença de ~**1,064608°** importa porque o primeiro período da reportagem #62 pergunta se os registros apontam para *“planos orbitais separados por mais de oitenta e cinco graus”*. Isso mistura orientação do nó com distância angular entre planos. Como o mesmo referencial **não foi autenticado**, nem 84,56° deve ser afirmado como separação histórica real. Substituir por **“valores de RAAN separados por 85,6259°”** e preservar a ressalva de referencial.
- J2 de primeira ordem, `J2=0,00108262668`, `μ=398600,4418 km³/s²`, `Rₑ=6378,137 km`, com `T=86400/n`, `a=(μ(T/2π)²)^(1/3)`, `p=a(1-e²)`: taxas **−1,17328099°/dia** e **−1,17312407°/dia**. Maior deslocamento proxy no intervalo ~**0,0002191°**, enquanto seriam necessários **~458.579°/dia**, descontando 0,0001° de quantização textual.
- A exclusão é **somente** para `same frame + same kind of node + offset de 16,132608 s isolado + proxy J2 declarado`. O máximo entre taxas de dois vetores não é limite físico experimental sobre uma trajetória desconhecida, e o texto da reportagem precisa continuar chamando isso de aproximação/modelo. **Nenhuma restrição Lean 4.35.0 sobre uma órbita histórica autêntica** foi introduzida. Compilar um teorema de implicação não tornaria autêntico o antecedente.

### 3. Solidez numérica e holdouts

Os 15 controles adversariais cobrem datas com precisão de microssegundos, TLE checksum, adulteração, identidades, circularidade 0/360°, **distinção RAAN versus plano**, singularidade equatorial, taxa J2 recalculada via período, limite de arredondamento e estados de conhecimento. Há replay das duas fontes revisionadas e verificadas por hash no GitHub Actions. É **reprodução de um diagnóstico condicional**, não órbita calibrada. Sem covariância instrumental, referencial histórico, erro posicional ou holdout de reentrada, não há simulador terminal validado nem domínio empírico reduzido.

### 4. Inferência, reportagem e decisão editorial

- **PR #62:** G12-B1 material, correção necessária da frase de abertura. O restante do capítulo distingue corretamente hipótese J2 estreita, proveniência, posição e impacto. A primeira linha não pode sugerir que diferença de RAAN é literalmente distância entre planos observados. Mesmo CI verde verifica construção editorial, não a semântica geométrica.
- **PR #59:** a correção G11-B1 foi conferida na versão `2c2301e1c1b203fa39898a1d3f7d521be457ad1e`: tabela 2/31/18, RMSE 7–30 dias 0,016023/0,020939/0,013378, ressalva pós-hoc, sem ganho universal. [CI editorial #43183133331](https://github.com/franklinbaldo/conde-incident/actions/runs/43183133331) reportou SUCCESS para esse head. A mensagem contém uma ênfase Markdown aninhada em “superioridade universal” que merece polimento sem alterar o veredito.
- **PR #3:** ainda baseada em Zola, enquanto #22 determina SSG Rust. Sem parecer para liberação arquitetural, apesar do CI da solução Zola.

**Resultado físico:** `INDETERMINATE`: nem exclui nem exige Conde; tampouco fornece hora/posição terminal ou prova de fragmento recuperado. C241-T10 **não** autentica o 528 nem seu ângulo real.

**Próxima pergunta verificável:** obter elementos orbitais instrumentais originais com época, referencial e covariância; antes disso, apurar se o legado de 284,1520° foi calculado, transcrito ou extraído de outro objeto/época. No capítulo #62, pedir substituição precisa da frase e novo CI no HEAD efetivamente corrigido. Sem merge, publicação, contatos externos ou edição do blog pessoal.
