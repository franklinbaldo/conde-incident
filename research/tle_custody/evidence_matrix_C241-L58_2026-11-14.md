---
type: Guide
title: 'C241-L58: errata visual da paginação Baker–Nunn NORAD 1963'
description: 'Corrige índice zero-based, documenta leitura visual das páginas 33–35 e impede ativação de restrição orbital indevida.'
---

# C241-L58 · Errata de custódia NORAD, páginas 33–35

**Correção material:** o registro C241-L57 atribuiu as páginas impressas 33–34 aos índices zero-based 47–48. A inspeção visual do mesmo PDF original revelou deslocamento de uma página: impressa 33 = página PDF 47 = índice 46; impressa 34 = PDF 48 = índice 47; impressa 35 = PDF 49 = índice 48. A afirmação de que a câmera RCAF de Cold Lake se encontrava sob controle operacional direto do NORAD está **na impressa 35**, que faltava na lista C241-L57. O manifesto anterior é mantido byte a byte. O novo arquivo JSON é um adendo, não uma revisão silenciosa.

**Fonte custodiada:** NORAD/CONAD Historical Summary, January–June 1963, publicado em 01/11/1963, cópia em https://documents.theblackvault.com/documents/afhistory/norad/%28U%29%201963%20NORAD%20CONAD%20History%20Jan-Jun.pdf. Binário de 12.218.228 bytes e 107 páginas, SHA-256 0ee50f207563618f98173d61be9bcc1db1b0a2afa83978ec9d6ee797a5d806f6, idêntico ao C241-L57. Renderização legível das páginas PDF 47, 48 e 49 em executor Ifro em 14/11/2026. A confirmação é **visual humana**; não reivindicar transcrição automaticamente verificada, porque as páginas escaneadas não têm texto extraível.

**Leituras específicas:** impressa 33: a USAF inicialmente possuía cinco câmeras Baker–Nunn, tendo transferido uma ao Canadá em meados de 1962; o SAO operava mais doze em apoio à NASA, total descrito como dezessete câmeras. A câmera canadense integra as cinco originais da USAF, não é décima oitava. Impressa 34: pedido de análise da capacidade/precisão em 9/1, pedido JCS de revisão em 12/2 e resposta NORAD de 19/3; o programa 706 foi reorientado. Impressa 35: continuação da resposta de março, encaminhamento da análise NORAD em 9/5 e declaração de controle direto do NORAD sobre Cold Lake, sem a data exata de início.

**Barreiras:** inventário de câmeras não significa número de medições. Controle operacional não demonstra exposição de NORAD 528, transferência, recepção SPADATS, sigma, época UTC, hora de reentrada nem impacto. Trata-se da **mesma linhagem documental institucional** de C241-L57, portanto nenhuma observação independente foi acrescentada e não se ativa restrição física. A pesquisa da queda em Conde continua aberta.

**Reprodução:** auditar o adendo com python3 tools/tle_norad_janjun_visual_c241_l58.py; executar unittest normal e com python3 -O no arquivo tests/test_tle_norad_janjun_visual_c241_l58.py. A identidade e paginação do PDF podem ser testadas com --pdf ARQUIVO e pypdf==6.1.3, mas o CI não substitui a revisão visual. Próxima aquisição: RU263, série 9, caixa 72, pastas #420 e #130; buscar identificação de alvo 1963-003B/528 com UTC, calibração e recibo de envio ao SPADATS. Relacionado à issue Conde #396 e cafezinho #14.
