---
type: Guide
title: "C241-L13: GCAT Agena B 527 versus rótulo payload; 528 não identificado"
description: "Auditoria reproduzível de categorias de catálogo com dependência e falta de ficha material 528/529 explícitas."
---

# C241-L13: o rótulo do 527 não identifica o objeto 528

**Ocorrência C241-L13**, continuação de [C241-L10](evidence_matrix_C241-L10_2026-11-12.md) e [C241-L12](evidence_matrix_C241-L12_2026-11-12.md), vinculada à [issue #13](https://github.com/franklinbaldo/conde-incident/issues/13). Consulta em 12/11/2026 (Porto Velho), 13/11 UTC. Não foram encontrados TLEs instrumentais novos.

## Achado material: taxonomias diferentes para o mesmo NORAD 527

No catálogo histórico **GCAT, arquivo auxiliar** de Jonathan McDowell, [auxcat.html](https://planet4589.org/space/gcat/data/cat/auxcat.html), registro **A00324**, revisto em **09/11/2026 00:53:07** segundo cabeçalho visível, a entrada `00527 / 1963-003A` é classificada **R2**, nome **Agena B 2313**, fabricante LMSC, data catalogada de decaimento 09/01/1969. A classificação é **compilação histórica moderna**, não observação direta do sensor de 1963, nem prova instrumental da taxonomia.

O [KeepTrack 00527](https://keeptrack.space/satellite/00527) chama a mesma entrada de **Payload** e informa bus **SAMOS F-2**. Esses rótulos de nível de sistema não são necessariamente incompatíveis: uma carga integrada a estágio/plataforma Agena pode ser descrita com mais de uma ontologia. **Não há prova de duas peças físicas independentes**, nem transferência automática da classe R2, da massa do Agena ou dos sensores do 527 para os objetos 528/529.

No [KeepTrack 00528](https://keeptrack.space/satellite/528) e [00529](https://keeptrack.space/satellite/529), os dois são etiquetados **Debris** sem ficha material autenticada. O arquivo **auxcat** é um catálogo *auxiliar*, portanto ausência de uma linha não autoriza dizer que 528/529 estão ausentes de todo o GCAT. Não foi feito inventário completo de `satcat` nesta fatia. Os agregadores podem compartilhar a mesma origem do catálogo orbital.

## Âncora contemporânea e linhagem

A [NASA, Satellite Situation Report 15/10/1963, NTRS 19640000428](https://ntrs.nasa.gov/citations/19640000428), edição 20, tabela *OBJECTS IN ORBIT*, página impressa 5/PDF 7, registra **1963 3A, 3B e 3C**. O fac-símile e suas **duas versões binárias** já foram auditados na [C241-L12](nasa_ssr_1963_oct15_C241-L12.json): não foram baixados ou inspecionados visualmente de novo aqui. A publicação não associa a letra B a número de peça, massa, origem do fragmento ou sensor individual. O vínculo `00527↔003A`, `00528↔003B`, `00529↔003C` é secundário, descrito em C241-L10.

A cadeia documental é: NASA 1963 (designador, lista de órbita) → junção moderna NORAD/COSPAR (C241-L10) → classificação GCAT de 527 e rótulos KeepTrack → **identidade física de 528 NÃO RECUPERADA**. É uma aresta `CONNECTED_PENDING_CALIBRATION`, não redução numérica do domínio dinâmico. **Nenhum registro de rastreamento nem sensor independente foi recuperado**.

## Dataset e prova de integridade

[Ledger JSON](gcat_identity_527_529_C241-L13.json) registra URLs, tipos de fonte, datas/editorial, objetos, campos desconhecidos e cinco dependências. [Auditor Python](../../tools/tle_gcat_identity_audit.py) faz a checagem *fail-closed* da linha `A00324/00527/1963-003A/R2/Agena B 2313` na captura atual do GCAT. [Testes adversariais](../../tests/test_tle_gcat_identity_audit.py) recusam troca de identidade, mudança de categoria, provas falsas de independência, preenchimento de frame, σ, TLE, peça 528 e promoção da RAAN legada. A linha sintética usada nos testes é **somente teste de parser**, não nova fonte histórica.

O código calcula SHA-256 e quantidade de bytes do arquivo GCAT **efetivamente baixado**, arquivados pelo CI; o arquivo remoto é mutável, então **não declaramos hash fixo da fonte na ausência de cópia preservada**. O controle sem rede valida exclusivamente ledger e estrutura, não equivalência de bytes da publicação. Uma alteração da linha esperada faz falhar a validação. Reproduzir:

```sh
python3 -m unittest discover -s tests -p 'test_tle_gcat_identity_audit.py' -v
curl -fL --retry 2 https://planet4589.org/space/gcat/data/cat/auxcat.html -o /tmp/auxcat.html
python3 tools/tle_gcat_identity_audit.py --ledger research/tle_custody/gcat_identity_527_529_C241-L13.json --gcat-file /tmp/auxcat.html --output /tmp/c241-l13.json
```

**Negativos e limites:** nenhuma observação instrumental, check digit histórico, epoch/sensor/frame/σ, ficha técnica do S00528 ou testemunho de separação encontrado. A RAAN 198,5261° continua apenas no espelho secundário e 284,1520° não foi autenticada e permanece inativa. A data NASA 08/11/1963 é dia catalogado sem hora/posição. Lean físico `NOT_PROMOTED`; simulação `NOT_RUN`; **Conde INDETERMINATE**. A próxima etapa é confrontar registros técnicos de lançamento 2313 e listagens instrumentais NORAD/NRO, sem inferir anatomia de 528 pela descrição de 527.
