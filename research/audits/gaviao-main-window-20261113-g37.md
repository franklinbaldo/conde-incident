---
type: Guide
title: '🦅 G37: revisão retrospectiva, guarda SHA do CI e commits na main'
description: Auditoria dos commits posteriores a G36, contraprovas de bypass da verificação de checkout, genealogia editorial e limites epistêmicos.
---

# G37: revisão retrospectiva do Conde

**Corte exclusivo:** `070481978ae7493ecae19d82acfc144072f792bb` (G36). **Corte inclusivo:** `4decea805580d59e0388508c6700f2a0c9df583c`, anterior a qualquer correção G37. A [matriz SHA a SHA](gaviao-main-window-20261113-g37.json) contém 14 integrações na primeira linha de pais, 18 commits no DAG, três merges convencionais e 4 commits laterais. O recorte distingue documentação, código e afirmação física.

## Achado G37-F1: teste SHA pode existir sem ser executado

O gate estático `tests/test_ci_checkout_sha.py` reconhece a linha exata `test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"`, mas não considera instruções de shell **anteriores**. Uma etapa pode manter essa linha, inserir `exit 0` antes dela e passar a validação estática sem executar a comparação. Contraprovas independentes também usam um `if false; then ... fi` e `set +e`, que neutralizam o gate. As três mutações foram inicialmente **aceitas** pelo auditor, reproduzidas localmente sem alterar workflows oficiais. O padrão não demonstra exploração real; comprova insuficiência do verificador de políticas.

**Correção:** a guarda só é reconhecida se antecedida exclusivamente por prólogo de shell de formas estritamente enumeradas e auditadas; qualquer outro comando anterior exige revisão explícita e falha no teste. O verificador permanece estático e não é uma prova geral de execução Bash. Teste adversarial foi observado vermelho antes da correção e verde depois; o CI do HEAD da PR deve comprovar a regressão sem reduzir outras verificações.

## Outros achados de integridade editorial

- `4decea805580d59e0388508c6700f2a0c9df583c` publica o capítulo da Coruja sem marcador de PR na mensagem, **mas a API GitHub confirma a PR #460**, cujo `merge_commit_sha` é o próprio commit. Não classificar como push direto apenas pelo assunto.
- `162cbb2512ed6fc9399378ce223c9a3bc116148f` é o **merge da PR #458**, mas sua árvore é idêntica à de `16de6f6e`, com **diff vazio**. A API de PRs associadas não retornou PR para `16de6f6e` (commit anterior, um pai), indício de push direto que exige investigação. Não contar duas entregas nem afirmar bypass de CI sem os logs de política.
- #446–#459 trouxeram SSR NASA, fotos reamostradas, registros ISD, testes Lean e holdout óptico condicional. Nenhum SSR impresso determina época instrumental ou posição terminal; foto reamostrada não autentica exposição; vetores ópticos sintéticos não confirmam rastreamento real; a prova de 15 segundos exige a hipótese editorial explícita.

## Limites e próxima auditoria

A ausência de evidência de observação não é prova de queda ou de ausência de queda. Conde permanece **INDETERMINADO**. Os números impressos NASA 527/529 não fixam uma trajetória do 528. A matriz registra commits e arquivos, não a validação externa de cada PDF nem um endosso dos checks CI. O próximo corte deve partir do SHA registrado como `end_inclusive`, incluir esta PR e os merges concorrentes. Não publicar conclusões no blog pessoal sem revisão.

**Retificação de proveniência verificada em 13/11/2026:** associação conferida em `GET /repos/franklinbaldo/conde-incident/commits/{sha}/pulls`, PRs [#458](https://github.com/franklinbaldo/conde-incident/pull/458) e [#460](https://github.com/franklinbaldo/conde-incident/pull/460). Ausência de associação para `16de6f6e` não prova, sozinha, que checks foram contornados. A primeira versão deste parecer deixou #460 pendente; esta retificação resolve esse ponto.
