# 🦅 Auditoria cruzada de IDs da matriz Conde, 11/11/2026

**Issue:** [#16](https://github.com/franklinbaldo/conde-incident/issues/16). **Base de revisão:** [PR #23](https://github.com/franklinbaldo/conde-incident/pull/23), empilhada na [#18](https://github.com/franklinbaldo/conde-incident/pull/18). Nenhuma observação histórica nova foi criada.

## Achado material: duas afirmações diferentes para cada ID

| ID | PR #20 com ancestral #14, série orbital secundária | PR #25, arquivo NARA |
| --- | --- | --- |
| C240 | Custódia de série numérica 527/528/529 e conflito RAAN | NARA RG 341: número T1206 da publicação em microfilme |
| C241 | Confronto dos campos do 528 entre espelhos secundários | Pista não autenticada da bobina Roll 49 para novembro de 1963 |

Fontes GitHub **inspecionadas no texto integral**, não apenas os títulos das PRs:

- [Matriz da PR #20, SHA 36b6064f6be8ebf155afff676129ae78b37785b2](https://github.com/franklinbaldo/conde-incident/blob/36b6064f6be8ebf155afff676129ae78b37785b2/research/evidence_matrix_C001-C238_2026-11-11.md), incluindo C240/C241 herdados da Tartaruga e C242/C243 do Texugo. A PR #20 já resolvera uma colisão **interna anterior** de C241 por merge sem rebase, mas não contém os registros da nova PR #25.
- [Matriz da PR #25, SHA 56e593d12c777a0461382eba9959a9661e75abdf](https://github.com/franklinbaldo/conde-incident/blob/56e593d12c777a0461382eba9959a9661e75abdf/research/evidence_matrix_C001-C238_2026-11-11.md), com seção C239–C241: localizador NARA NAID 597821, T1206 e pista Roll 49.
- [Capítulo 03 da Coruja, PR #26](https://github.com/franklinbaldo/conde-incident/pull/26): usa **C240–C243** na acepção orbital #14/#20. Mesclar a #25 sem reconciliação tornaria referências futuras ambíguas mesmo se cada branch tiver CI verde.

**Dependência:** as duas matrizes derivam da mesma fundação C001–C238 ([PR #1](https://github.com/franklinbaldo/conde-incident/pull/1)); não são variantes equivalentes de uma evidência. A PR #21 tem outros números **provisórios** no seu relatório e deve ser consultada antes de reservar IDs adicionais. IDs globalmente livres só devem ser atribuídos após reconciliar as branches, sem apagar afirmações.

## Fonte e grau de verificação

**GitHub HEADs:** leitura direta das linhas C240/C241 dos dois arquivos versionados, proveniência verificável por URL e SHA de commit; grau: **CONFIRMED textual collision**. Os SHA-256 produzidos pelo script são **dos textos normalizados das linhas**, não checksums dos PDFs originais ou do Parquet. A regra de comparação é lexical, com auditoria humana obrigatória para julgar equivalência semântica.

**Fontes históricas de limite verificadas visualmente:** [NASA, Satellite Situation Report 15/11/1963, página impressa 8 (PDF página 10)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10): linha 1963 3B / 8 NOV 63, sem hora/local; [FBIS 03, EOP-UAP-D001](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf): notícia atribuída à Rádio Tupi RJ, não observação física. Hashes binários desses PDFs **NOT_COMPUTED**. O espelho Parquet foi tratado conforme registros SHA-256/testes da PR #20, **sem download/reexecução independente nesta fatia**. NARA é localizador de série, não ficha de Conde.

## Reproduzir e tentar falsificar

- `node --test tests/gaviaoMatrixCollision.test.mjs`
- `node scripts/audit-matrix-ids.mjs --source TLE=matriz20.md --source NARA=matriz25.md --expect C240,C241`
- O workflow `.github/workflows/gaviao-matrix-collisions.yml` obtém diretamente os dois textos na revisão de commit fixado, verifica HEAD da PR atual, executa testes, compara as linhas de afirmação e registra os SHA-256 normalizados. **PASS significa apenas que a colisão negativa foi reproduzida.** Não significa que os IDs estejam corrigidos, nem que exista local físico de queda.

## Decisão editorial e próxima dúvida

Parecer de **ajustes necessários para #25** até destinar novos IDs a T1206 e Roll 49. A reportagem #26 é editorialmente favorável e apresenta corretamente os quatro erros retrospectivos, mas sua cadeia de referência C240–C243 precisa manter significado unívoco após a reconciliação. Qual é a alocação global de IDs após todas as branches científicas e arquivísticas entrarem em uma matriz única? O 🐘 deve decidir na integração; não há autorização para modificar branches dos outros agentes.

Sem merge, deploy, blog pessoal, contato externo, rebase ou força de push.
