# Colisões C44–C46: índice de ocorrências, não reconciliação

**Escopo:** matriz cumulativa de pesquisa, branch-base da [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), commit `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`, blob Git SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7`. Este documento é **somente um mapa de linhas inspecionadas da matriz versionada**; não são inspeções novas dos originais históricos, nem um registro Lean recuperado.

A matriz **reutiliza C44, C45 e C46** em duas seções com sentidos distintos. A chave `C44`, isolada, portanto não é um identificador unívoco neste instantâneo. Não deduplicar, nem somar as entradas como observações independentes.

| Chave textual | Ocorrência na matriz | Natureza reportada | Limite |
|---|---|---|---|
| C44 | [linha 164](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L160-L168) | Solo aproximado da sede, camada ArcGIS CONDER 11 | Não informa solo de cratera histórica nem resistência no ponto real |
| C45 | [linha 165](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L160-L168) | Geologia regional da sede, camada CONDER 48 | Não determina estratigrafia a 5 m |
| C46 | [linha 166](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L160-L168) | Energia/resistência condicionais para esfera e parâmetros adotados | Não é medição de artefato/cratera |
| C44 | [linha 175](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L171-L183) | Últimos quatro TLEs reportados antes de 27/10/1963 | Espelho secundário, não observação terminal do 528 |
| C45 | [linha 176](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L171-L183) | Quatro soluções preditivas condicionais, com erros de fase | Não constitui localização observada |
| C46 | [linha 177](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L171-L183) | Ajuste conjunto fase/frequência a registros prévios | Não determina atmosfera nem hora/local final |

O vínculo entre as duas seções é **colisão editorial de rótulo**, não causalidade nem confirmação. Para qualquer citação atual, usar **commit + linha + seção**, e preservar o rótulo textual original sem reatribuição silenciosa.

**Relação com o arquivo Lean histórico:** a afirmação de que um ZIP anterior continha 154 proposições, 151 rótulos e colisões C44–C46 permanece **não auditada** sem os bytes originais, `Evidence.lean`, `evidence_registry.json`, gerador e SHA-1/SHA-256 de custódia independentes. Este mapa de seis ocorrências na matriz **não demonstra** que sejam as mesmas entradas ou a mesma colisão do ZIP ausente. `scripts/audit_zip.py` executa apenas checagem estrutural, nunca restaura textos nem autentica proposições.

Não acrescenta hipóteses orbitais, medições ou novas fontes históricas. Preparado para revisão independente pelo Gavião; integração exclusiva do Elefante.

## Crosswalk executável, sem substituição do corpus histórico

O script `formal/scripts/verify_matrix_refs.py` computa o SHA-1 **Git
blob** do Markdown e verifica, dentro do instantâneo da PR #1, cada linha
C01 (19), C131 (502), C197 (905) e as seis linhas acima. Em especial,
a linha 19 contém C01; a linha 20 contém **C02** (link anterior do
laboratório Web corrigido). A linha C197 está grafada `**C197**`,
exigindo reconhecimento de Markdown. A execução no CI compara os bytes
do instantâneo e não faz nova leitura das fontes NASA/FBIS. Os testes
negativos usam corpus de linhas inteiramente **sintético**.

Comando (raiz do repositório):
```sh
python3 formal/scripts/verify_matrix_refs.py research/evidence_matrix_C001-C238_2026-11-11.md
```

Status de sucesso: `PINNED_MATRIX_ROWS_PASS_ONLY`. Autenticidade do
corpus histórico, correspondência com registro Lean 154/151 e igualdade
das colisões do ZIP ausente: **NOT_VERIFIED/NOT_RUN**.
