---
type: Guide
title: '🦅 G54: verificações de exportação orbital em Python otimizado'
description: Auditoria retrospectiva de 12 integrações e contraprovas de integridade da saída C241 sob Python -O.
---

# G54: o exportador científico não pode depender de `assert`

**Janela:** `9baf7b17` (exclusivo) → `7784cf8` (inclusivo): **12 integrações first-parent, 12 commits no DAG, zero merges convencionais**. O manifesto JSON adjacente enumera os commits; checks históricos individuais não examinados permanecem `NOT_CHECKED`.

## G54-F1: `--check` declarava PASS sem ler o arquivo sob `python -O`

O exportador de mapa C241 introduzido na [#692](https://github.com/franklinbaldo/conde-incident/pull/692) usava `assert` como barreira de validação de fonte, grid, valores e paridade entre artefato gerado e versão publicada. A opção de CPython `-O` elimina todas essas linhas. A [#698](https://github.com/franklinbaldo/conde-incident/pull/698) fortaleceu os gatilhos do replay, mas não corrigiu o exportador.

**Contraprova local executada:** cinco cenários sintéticos foram aceitos pelo CLI em `python3 -O`: resumo com posterior histórico fictício, probabilidades negativas, grid com 399 células, arquivo público adulterado e arquivo público inexistente. Para os dois últimos, `--check` retornava **0/PASS sem conferir bytes**. No modo normal essas contraprovas eram rejeitadas. Não foi alterada nenhuma fonte histórica nem demonstrada falsificação real.

**Correção:** substituir todas as assertivas do exportador por guardas incondicionais `ValueError`, verificar a existência e bytes do artefato no modo `--check` e executar os mesmos testes adversariais por subprocesso em Python normal e otimizado dentro do workflow especializado C241. O controle positivo é um grid sintético de 400 células com probabilidade zero. **Após reparo, 6/6 testes passaram em ambos os lançadores.** O replay de 1,5 milhão não foi rodado localmente, pois depende do CI especializado no HEAD da PR.

**Limites epistemológicos:** o experimento é condicional, usa TLE secundário e um dia NASA sem erro temporal calibrado; não representa medição instrumental independente nem uma probabilidade histórica de queda em Conde. Nenhuma hora, local ou identificação de impacto do NORAD 528 foi demonstrada.
