---
type: Guide
title: Prek e OKF no projeto Conde
description: Política auditável de tamanho e validação dos documentos Markdown novos ou modificados.
---

# Prek e OKF no Conde

**Obrigatório:** o workflow `.github/workflows/prek.yml` executa `prek run --all-files` no SHA real. O prek executa tanto o limite de **20.000 bytes** por arquivo como o **`okf-parser==0.48.2 check`** com specs normativas. Verifique a execução, não apenas a presença do YAML.

## Acervo anterior

A base anterior continha **15 arquivos acima do limite** e **94 Markdown** sem migração OKF integral. `bun.lock` passa a ser exceção editável explícita, mantendo os outros **15 blobs** congelados. Os dois inventários em `config/` guardam os caminhos e hashes Git originais. As exceções legadas são **temporárias, exatas e imutáveis por hash**. Exceções editáveis de arquivos gerados são listadas em `config/file-size-exemptions.json`, com caminho exato, sem curingas e com justificativa **e com uma allowlist revisada no código `scripts/check_file_size.py` (atualmente somente `bun.lock`)**. A inclusão de outro arquivo exige alteração explícita de código e testes; o manifesto JSON, sozinho, não autoriza dispensa do limite. Isso não dispensa OKF ou outros gates. Qualquer arquivo alterado ou novo deve obedecer imediatamente às regras.

Não aumentar, reformatar ou alterar qualquer blob legado mantendo o tamanho acima do limite. Para modificar um Markdown legado, primeiro convertê-lo para OKF (frontmatter `type/title/description` e spec correspondente) e, caso ultrapasse 20.000 bytes, dividir em partes que preservem todas as referências e IDs originais. Remover do inventário o item migrado em PR específica. Nenhuma fonte primária, matriz ou prova Lean pode ser apagada só para conseguir CI verde.

O checker incremental `scripts/check_okf_incremental.py` **executa o parser oficial**, mas prepara um diretório de validação apenas com arquivos Markdown novos, modificados e specs. Não afirma que os 94 documentos antigos já passaram. Essa dívida é explícita e deve diminuir até que `okf-parser check . --require-spec '.okf/specs/{slug}.md' --normative-spec` passe diretamente na raiz.

## Repositórios pessoais

Os workspaces privados dos 14 animais já usam prek + OKF normativo no workflow `OKF all Markdown`; nesses repositórios não há tolerância a Markdown pessoal inválido; exceções exatas de tamanho para arquivos gerados não dispensam OKF nem Prek. O projeto público requer migração controlada de seu corpus anterior, sem perda de proveniência.

## Execução local

```sh
uvx --from prek==0.5.10 prek run --all-files
```

Antes de declarar uma PR integrada, confirmar todos os workflows necessários no SHA exato e anotar qualquer falha. Uma checagem de arquivos não certifica medições orbitais, fontes históricas nem publicação no GitHub Pages.
