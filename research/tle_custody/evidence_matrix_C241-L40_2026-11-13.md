---
type: Guide
title: "C241-L40: 1.176 kg do GCAT é TotMass do 527, não uma soma demonstrada de 527–529"
description: "Auditoria dos campos Mass, DryMass, TotMass e OrbPay do GCAT, com 6 snapshots por SHA e discrepância de 30 kg entre duas interpretações da Agena."
---

# C241-L40 · O que a tabela realmente atribui aos 1.176 kg?

**Resultado:** nas tabelas digitais do [GCAT](https://planet4589.org/space/gcat), versão 1.8.9, a linha **S00527 / 1963-003A** informa **Mass = 306 kg**, **DryMass = 306 kg**, **TotMass = 1176 kg**. As linhas **S00528 / 003B** e **S00529 / 003C**, classificadas como componentes/detritos, imprimem **0** nos três campos. **Zero de catálogo não é observação física de massa nula.**

A [definição oficial de colunas](https://planet4589.org/space/gcat/web/cat/cols.html) explica que **Mass** é a massa própria do objeto na inserção orbital, excluindo objetos ligados; **TotMass** contabiliza o objeto e objetos fisicamente ligados, sendo atribuído a uma das linhas do grupo. Portanto, **1176 não é um levantamento demonstrado das massas exclusivas dos três números NORAD**. A declaração anterior de orçamento para 527+528+529+X continua somente cenário condicional, não restrição histórica.

| Registro GCAT | Mass kg | DryMass kg | TotMass kg | Escopo |
|---|---:|---:|---:|---|
| S00527, 003A | 306 | 306 | 1176 | Carga útil / entrada de referência do conjunto |
| S00528, 003B | 0* | 0* | 0* | Fragmento sem massa documentada |
| S00529, 003C | 0* | 0* | 0* | Fragmento sem massa documentada |
| A00324, Agena B 2313 | 900 | 870 | 0* | Estágio em outra linha com mesmo SATCAT 527 |

*Valor literal impresso, não física de massa zero.*

O registro do [lançamento 1963-003](https://planet4589.org/space/gcat/data/launch/Thor.html) informa **OrbPay = 1.176 toneladas**. Sua [documentação](https://planet4589.org/space/gcat/web/launch/lcols.html) define OrbPay como carga útil entregue à órbita, **gerada automaticamente** a partir de tabelas de payloads, com ressalvas de casos especiais. Não se trata de **OrbMass** total dos corpos. O campo OrbMass imprime 0.000, mas sua definição informa que esse campo **ainda não estava preenchido**. O catálogo de payloads lista apenas S00527 entre 1963-003A/B/C.

**Controle numérico discriminante:** 306 + **870 (Agena seca)** = 1176, mas 306 + **900 (Agena na inserção)** = **1206**, diferença de **30 kg**. O significado da coincidência com a massa seca e a origem da diferença não estão demonstrados; não inventar uma perda de combustível de 30 kg nem escolher uma combinação para fechar o balanço. A regra geral de TotMass exige reconciliação com a genealogia e as épocas dos valores. A linha A00324 do GCAT identifica Agena **B**; fontes anteriores que denominam Agena **D** exigem avaliação documental, não substituição automática.

**Custódia da consulta:** seis arquivos completos recuperados em 13/11/2026 do portal GCAT, incluindo satcat (32.734.213 bytes), auxcat (5.604.643), psatcat (8.798.305), Thor (314.863) e as duas páginas de documentação (26.532 e 19.191). URLs, comprimentos e SHA-256 exatos constam do [ledger C241-L40](gcat_mass_semantics_C241-L40.json), reproduzíveis em CI com o auditor. Os dados são **catálogo secundário mutável**, não ficha de engenharia de 1963. Um novo hash futuro requer uma variante explicitamente identificada e reauditoria das colunas.

**Consequência no grafo:** os modelos de massa da [PR #621](evidence_matrix_C241-mass-budget-X_2026-11-13.md) e [PR #622](evidence_matrix_C241-L39_2026-11-13.md) permanecem disponíveis como *experimentos contrafactuais condicionais*, mas não devem receber os 1.176 kg como fechamento físico histórico até identificação e época comum de todas as partes. Nem os 528/529 nem a massa seca da Agena podem ser inferidos a partir do dia de reentrada. Zero nova observação, zero parâmetro de arrasto calibrado e zero redução de Θ.
