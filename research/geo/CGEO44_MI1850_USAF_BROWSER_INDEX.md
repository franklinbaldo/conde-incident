---
type: Evidence
title: "CGEO-44: fotoíndice MI-1850 adquirido com estado do navegador"
description: "Custódia reproduzida por Chromium, SHA do JPEG e leitura cautelosa da legenda 1964–1970."
---

# CGEO-44 | Fotoíndice SGB MI-1850

Fonte primária: [SGB, coleção FotoUSAF, pasta 1850](https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF&pasta=1850). O nó 680 tem o título **1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI**.

**Correção de CGEO-43:** um POST artificial isolado podia repor a seleção na pasta 0335 e entregar JPEG errado. Em 14/11/2026, duas sessões reais independentes de Chromium com scripts ASP.NET/Telerik executados mantiveram simultaneamente nó 680, cabeçalho PastaTxt da pasta 1850, hPagFis=680 e GET de I0000680-...JPG. Não houve retorno à pasta 0335 nessas sessões.

**Objeto adquirido:** JPEG de 957.893 bytes, 4.355 × 4.350 pixels, SHA-256 45d72dff84520bb387d5b8ce7c5a8f4c9361457841341b2c21016e992c0fef79. O cache é exclusivo da sessão e não é identificador persistente. Bytes e captura de rede ficam fora do Git; workflow os readquire em pasta temporária. Duas sessões deram o mesmo SHA e dimensões. Trata-se de **fotoíndice composto**, não de fotograma aéreo individual.

**Leitura visual do cartucho, sem OCR:** estão impressas "and Geodetic Service (ACGS)", "Date 1964-1970", "ALT. 30,000' ASL", "Scale of Photography 1:60,000" e "Scale of Index 1:180,000". A série USAF 63-32 do catálogo e o cartucho ACGS 1964–1970 na imagem devem permanecer distintos. Ano da série não equivale à data de exposição. A faixa impressa 1964–1970 é posterior a novembro de 1963, mas não demonstra os dias de cada fotograma.

**Limites:** a carta traz marcas de latitude/longitude, mas datum, incerteza de georreferenciamento, correspondência das faixas aos fotogramas originais, posição do Centro em 1963, limite municipal jurídico histórico e posição da queda continuam desconhecidos. A imagem não prova cobertura fotográfica de Conde em 1963 nem ausência dessa cobertura por outro projeto. Geometria do Centro em 1963: nula. Posição do evento: nula. Restrição orbital nova: nenhuma. Não misturar a custódia com a da Petrobras 53 D ou as cartas IOCS.

**Replay:** python3 tools/cgeo44_browser_photoindex.py valida offline. python3 tools/cgeo44_browser_photoindex.py --live --output-dir /tmp/cgeo44-acquisition usa Playwright Chromium + Pillow, confere estado/imagem/resposta e salva bytes fora do projeto. A workflow reproduz a aquisição no HEAD exato; HTTP 200 isolado não basta.
