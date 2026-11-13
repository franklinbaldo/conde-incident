---
type: Guide
title: '🦅 G51: otimização Python apagava controles de custódia'
description: Auditoria retrospectiva de 12 integrações e contraprovas para verificador documental da estação 1023.
---

# G51: verificação científica não pode depender de `assert`

**Janela congelada:** `e26d0db8` (exclusivo) → `cf163c58` (inclusivo), 12 integrações first-parent, 12 commits no DAG e nenhum merge convencional. O manifesto JSON adjacente conserva SHA, PR e contagem de arquivos por integração; CI histórico individual não consultado continua `NOT_CHECKED`.

## G51-F1: mutações falsas aprovadas sob `python -O`

A PR #668 incluiu `tools/verify_kyiv_station1023_archive.py`, auditor de metadados de fontes ucranianas. Seus controles de proveniência, limites epistêmicos e autenticação SHA estavam implementados com `assert`. Python otimizado (`-O`, `PYTHONOPTIMIZE`) **remove essas operações**, de modo que executar `validate()` com um manifesto sinteticamente adulterado retornava `True`: um `sha256` inventado, a declaração de que objetos desconhecidos seriam 527/528/529 ou a ativação indevida de uma restrição orbital não eram rejeitados. O teste RED foi reproduzido no HEAD congelado (sem alegar execução histórica sob `-O`).

**Correção:** usar `require(...)` com `ValueError` para as verificações científicas de produção, incluindo o par de arquivos HTML originais e a combinação de argumentos CLI; adequar os testes `unittest` e criar controle positivo mais três negativos em **subprocessos Python `-O` reais**. **GREEN local:** 9/9 testes normais e 9/9 testes com `-O`; execução do auditor no manifesto intacto passou, e `git diff --check` ficou limpo. CI HEAD da PR e CI pós-merge ainda não confirmados no momento de autoria.

## Leitura científica

O inventário de Kyiv comprova a existência de uma rota de acervo secundária, não observações originais dos NORAD 527/528/529. A coleção datada de 1976 não foi transformada em registro de novembro de 1963; totais de vários anos não são leituras daquele dia. Nenhuma nova hora, sigma ou coordenada terminal do 528 foi recuperada. Não há evidência de adulteração histórica real.
