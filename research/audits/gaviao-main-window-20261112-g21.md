---
type: Guide
title: "G21: auditoria retrospectiva de 13 integrações da main e contraprova do Pages"
description: "Revisão científica, documental, editorial, de Lean e CI entre os checkpoints 5c2f610d e 86cf4e2c, com correção G21-F1."
---

# G21 | revisão retrospectiva independente, 12/11/2026

**Janela auditada (first parent, corte imutável):**
`5c2f610d624a79dab9b4b181851d8fe2883868f5..86cf4e2cec271532b95a134623150539a0926b07`.
A API de comparação GitHub devolveu `ahead_by=13`, `behind_by=0`, 13 commits. Foram conferidos os pais consecutivos, os arquivos de cada commit e os HEADs individuais de PR. **13 squash merges, zero commits diretos**, 42 caminhos distintos. A PR **#171** foi encerrada sem merge dentro da janela; não a confundir com um commit da main. Detalhes e arquivos, com todos os SHAs completos: [manifesto G21](gaviao-main-window-20261112-g21.json).

| Ordem | PR | SHA merge (prefixo) | Verificações no HEAD final da PR | Escopo principal |
| --- | --- | --- | --- | --- |
| 1 | #168 | 69d88388 | 12/12 | C232: duas citações documentais na mesma ocorrência |
| 2 | #169 | 654f781a | 12/12 | Lean: ancestralidade de contratos documentais |
| 3 | #170 | a3ab2d7d | 12/12 | Perfis nominais IGRA de Recife em 7, 8 e 9/11 |
| 4 | #158 | 46f123dd | 12/12 | Verossimilhança circular condicional |
| 5 | #173 | 28066fa3 | 12/12 | Legenda e projeção cartográfica UWM |
| 6 | #174 | 51d33a05 | 12/12 | Correção e auditoria G20 de proveniência |
| 7 | #176 | 6b5b0b92 | 12/12 | URL original JP2 UWM; checksum pendente |
| 8 | #175 | 4a692369 | 12/12 | Veto a épocas NASA SSR inventadas |
| 9 | #177 | 7c87a687 | 12/12 | Instrumento repetido em treino/holdout |
| 10 | #178 | dcae1839 | 12/12 | Auditoria de conteúdo Pages, objeto da G21-F1 |
| 11 | #179 | 3b4afe64 | 12/12 | Exibição separada das fontes de C232 |
| 12 | #180 | f9d8ac9a | 13/13 | NORAD e datação original de documentos |
| 13 | #182 | 86cf4e2c | 14/14 | Precisão de armazenamento Parquet, não TLE original |

**Escopo dos checks:** as contagens acima são execuções `pull_request` recuperadas da API de Actions para o **HEAD exato de cada PR**, com conclusão SUCCESS. Não são provas de autenticidade dos bytes externos, de independência física ou de publicação. O merge #182 ocorreu após a consulta inicial; seu commit, pai e CI foram incluídos antes do corte.

## G21-F1: falso positivo de conteúdo em Pages (corrigido nesta PR)

O verificador criado na [#178](https://github.com/franklinbaldo/conde-incident/pull/178) examinava expressões regulares no HTML bruto. Um documento poderia ter links de navegação somente dentro de comentários HTML, um `<article>` exclusivamente num comentário ou string JavaScript e referências de `<script>` dentro de comentário. Respostas HTTP 200 de CSS/JS contendo apenas espaços também passavam por serem strings não vazias. Em conjunto com respostas sintéticas de metadados verdes, essas contraprovas poderiam produzir `VERIFIED_PUBLICATION` sem navegação, artigo ou bundles reais.

A correção **desconsidera comentários, conteúdo de templates e corpos de script/style/textarea** ao examinar elementos; preserva a tag `<script src>` visível; exige corpo não vazio após `trim()`; acrescenta quatro casos adversariais em `scripts/pages-live-audit.test.mjs`. Esta é uma verificação conservadora sobre HTML, **não uma implementação integral do parser DOM nem autenticação de deployment**.

**G21-F2, aberto:** o gate de metadados roda antes da coleta HTTPS e não vincula os bytes HTML/JS/CSS a um digest do artefato de deploy ou conteúdo assinado pelo SHA. Um site que mudou após a leitura de metadados ainda pode receber `VERIFIED_PUBLICATION` para conteúdo pertencente a outro estado. Propor controle de versão/digest do artefato e rechecagem após HTTPS com o responsável 🐘 Elefante na [issue #6](https://github.com/franklinbaldo/conde-incident/issues/6). Não alegar correção completa.

Na consulta autenticada à API GitHub nesta rodada, **`has_pages=false`** para o projeto. Logo, nenhum conteúdo Pages foi comprovado como publicado; os testes da PR usam HTTP e metadados sintéticos, não um deployment real.


**Regressão observada no CI da integração:** a primeira tentativa da PR G21 [#187](https://github.com/franklinbaldo/conde-incident/pull/187), no HEAD `f801a19b`, encontrou o gate `Publish Conde site` vermelho no [run #43274184201](https://github.com/franklinbaldo/conde-incident/actions/runs/43274184201): apesar do ambiente `VITE_BASE_PATH=/conde-incident/`, o Vite 8 emitiu links `/assets/*`. A correção operacional **separada** [#190](https://github.com/franklinbaldo/conde-incident/pull/190) passou em 14/14 workflows no SHA `55036c8a0d1f2b8c0b9557e78261b44d04253b59` e foi integrada em `dbb6ed742e661b1b43c71dd710024b2e5281e269`, usando `bunx vite build --base /conde-incident/`. Esses checks aprovam o **build**, não um deploy real.

## Autenticidade, independência e contraprova histórica

A [#180](https://github.com/franklinbaldo/conde-incident/pull/180) trouxe registros contemporâneos NORAD, sem observar diretamente o objeto 528. O [fac-símile 07.pdf](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/07.pdf), página PDF 3 (índice zero 2), documenta o objeto **687** e detecção de Shemya. O [08.pdf](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/08.pdf), página PDF 2 (índice zero 1), traz a janela de aproximadamente **110 minutos, 12/11/1963, 22:10–24:00 UTC**, **para SPADATS 688, Cosmos 21, não 528**. A evidência de capacidade de rastreamento do NORAD não vira uma localização da reentrada do NORAD 528.

Os fac-símiles [09.pdf](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/09.pdf) e [10.pdf](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/10.pdf) registram **30 NOV 64**, relatórios `216-64` e `217-64`, embora tenham sido catalogados online com data de 1963. Reinspeção visual das primeiras páginas: correção documental favorável. Nesta rodada não se baixaram e autenticaram todos os bytes, hashes e sensores externos do acervo; graus de confirmação variam entre inspeção de fac-símile e leitura de custódia no Git.

A #168 e #179 agora distinguem índice e cartão NARA em C232#1; são **dois documentos**, não duas detecções independentes. A #174 rejeita caminhos ancestrais inválidos. A #175 veta horas/minutos NASA SSR fabricados. A #176 preserva o endpoint original JP2 sem afirmar checksum do original. A cartografia #173 não delimita o município de Conde em 1963.

## Lean, TLE, métodos e física

- A #169 compila vínculos documentais para tipos Lean 4.35.0, incluindo snapshot de C151 e dependência NTRS→NASA. **Nenhum novo predicado físico ativo, prova de trajetória, ou redução demonstrada do domínio admissível**. A execução Lean de CI verifica contratos e geração condicional.
- A #158 implementa identidade da verossimilhança von Mises com viés de linhagem marginalizado, e checks adversariais de integridade matemática. Falta previsão orbital calibrada, erro histórico e escolha justificada de `kappa`; a integral de viés não é posterior da queda.
- A #170 compara ventos **da mesma estação de Recife**, em três datas nominais, sem horário exato de lançamento, incerteza instrumental ou transferência validada a Conde. Não são três estações independentes.
- A #177 rejeita reaproveitamento declarado do mesmo registro instrumental em treino/holdout em controles sintéticos, sem autenticar registros reais. A #182 audita seis campos numéricos em 123 linhas do Parquet secundário, 738 roundtrips e tipos Arrow, sem recuperar as duas linhas TLE originais nem converter RAAN legado 284,1520° em observação. RAAN 198,5261° também depende do espelho secundário.

## Editorial, conclusão e próxima dúvida

Nenhum `stories/*.md` foi incorporado à `main` dentro do intervalo. A [#181, Caderno 21](https://github.com/franklinbaldo/conde-incident/pull/181) permanece draft; a [#3](https://github.com/franklinbaldo/conde-incident/pull/3) também. O avanço documental da #180 não autoriza publicar capítulo ou concluir impacto.

**Resultado científico: INDETERMINADO.** O registro NASA C197 traz o dia catalogado de decaimento de 528, não tempo/posição terminal; as novas janelas NORAD são de outro objeto. Nenhuma prova Lean ou ajuste numérico reduz um domínio de trajetória física autenticada até um ponto de impacto em Conde.

Próxima dúvida: recuperar observação instrumental de 527/528/529 com objeto, UTC, referencial, incerteza e linhagem original; só então qualificar o parâmetro de órbita, executar holdouts físicos e testar exclusão ou inclusão de Conde. Próxima auditoria G22 deve começar **após** `86cf4e2cec271532b95a134623150539a0926b07`, cobrindo os merges posteriores, inclusive a entrega G21 se integrada. Sem publicar nem alterar o blog pessoal.
