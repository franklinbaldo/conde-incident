---
type: Guide
title: 'C241-L16: Wayback e citacoes NASA C197/C198 no Lean'
description: 'Rastreabilidade de capturas Wayback, mesmo documento e tempo terminal desconhecido sem adicionar observações do objeto 528.'
---

# C241-L16: cadeia Wayback como proveniência, não medição orbital

Fonte auditada: [crosswalk WB-01](../../public/data/conde-wayback-citation-links.json), publicado pela 🐝 Abelha na [PR #330](https://github.com/franklinbaldo/conde-incident/pull/330), com captura e hashes custodiados pela 🦦 Lontra na [issue #308](https://github.com/franklinbaldo/conde-incident/issues/308). A compilação para Lean consome esse artefato, verifica sua reprodução a partir dos pais e compara C197#1 e C198#1 com o catálogo canônico de citações e com o documento de dependências.

A URL **API atual** da NASA SSR de 15/11/1963 foi consultada no índice Wayback sem captura exata sob aquela URL. Isso não significa ausência do documento. A auditoria subsequente da [PR #354](https://github.com/franklinbaldo/conde-incident/pull/354) acrescentou **três capturas históricas** do PDF NASA nos endereços legados de 17/02/2015, 28/02/2017 e 02/03/2017: todas têm **o mesmo SHA-256**, correspondendo a **um único conteúdo documental**, não três sensores ou três observações independentes. Dois outros PDFs preservados são o resumo NORAD/CONAD (15/03/2023) e o inventário Smithsonian (28/02/2021), totalizando cinco replays e três trabalhos. SHA-256 dos **bytes recuperados** e digest CDX Base32 SHA-1 são coisas distintas. Timestamp da captura nunca substitui a data de produção/observação do documento.

C197#1 (NASA SSR 15/11/1963) e C198#1 (metadados NTRS) apontam para o **mesmo trabalho** `NASA_SSR_VOL3_22`, não para duas observações instrumentais independentes. A matriz original está presa ao blob `a7978c3a75a153b16ab70118a92c434bba674cb7` e aos hashes de cada ocorrência. Os registros em `formal/Conde1963/WaybackCitations.lean` incluem `Option` para captura, data de captura e tempo do evento terminal. Para C197/C198, `eventTimeUtc = none` e `activated = false`; o parâmetro `reentry_terminal_timestamp_528` continua sem valor.

O gate verifica que nenhuma transição silenciosa transformou alguma das cinco capturas preservadas em uma medição do NORAD 528, que NTRS não se tornou um segundo sensor e que a captura recente não se tornou uma época orbital de 1963. As mutações adversariais reproduzem esses riscos. **Resultado:** duas ocorrências conectadas a um trabalho documental e três replays NASA vinculados ao mesmo PDF, sem redução adicional do domínio físico de simulação Θ. Um evento com horário/local exigiria uma fonte primária de rastreio com ID 528, época UTC, quadro, unidade e incerteza; este crosswalk não a fornece.
