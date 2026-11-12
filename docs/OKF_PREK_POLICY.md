---
type: Guide
title: Prek e OKF no projeto Conde
description: Política auditável de tamanho e validação dos documentos Markdown novos ou modificados.
---

# Prek e OKF no Conde

**Obrigatório:** o workflow `.github/workflows/prek.yml` executa `prek run --all-files` no SHA real. O prek executa tanto o limite de **20.000 bytes** por arquivo como o **`okf-parser==0.48.2 check`** com specs normativas. Verifique a execução, não apenas a presença do YAML.

## Acervo anterior

A base existente continha **16 arquivos acima do limite** e **94 Markdown** sem migração OKF integral. Os dois inventários em `config/` guardam os caminhos e hashes Git originais. As exceções são **temporárias, exatas e imutáveis por hash**. Qualquer arquivo alterado ou novo deve obedecer imediatamente às regras.

Não aumentar, reformatar ou alterar qualquer blob legado mantendo o tamanho acima do limite. Para modificar um Markdown legado, primeiro convertê-lo para OKF (frontmatter `type/title/description` e spec correspondente) e, caso ultrapasse 20.000 bytes, dividir em partes que preservem todas as referências e IDs originais. Remover do inventário o item migrado em PR específica. Nenhuma fonte primária, matriz ou prova Lean pode ser apagada só para conseguir CI verde.

O checker incremental `scripts/check_okf_incremental.py` **executa o parser oficial**, mas prepara um diretório de validação apenas com arquivos Markdown novos, modificados e specs. Não afirma que os 94 documentos antigos já passaram. Essa dívida é explícita e deve diminuir até que `okf-parser check . --require-spec '.okf/specs/{slug}.md' --normative-spec` passe diretamente na raiz.

## Repositórios pessoais

Os workspaces privados dos 14 animais já usam prek + OKF normativo no workflow `OKF all Markdown`; nesses repositórios não há tolerância a Markdown pessoal inválido nem a arquivo acima do limite. O projeto público requer migração controlada de seu corpus anterior, sem perda de proveniência.

## Execução local

```sh
uvx --from prek==0.5.10 prek run --all-files
```

Antes de declarar uma PR integrada, confirmar todos os workflows necessários no SHA exato e anotar qualquer falha. Uma checagem de arquivos não certifica medições orbitais, fontes históricas nem publicação no GitHub Pages.
