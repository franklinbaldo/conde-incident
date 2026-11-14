---
type: Guide
title: 'C241-L52: relatório NORAD de 1963 e fronteira entre plano e observação'
description: 'Páginas 55–56 de relatório institucional contemporâneo distinguem proposta de troca óptica SAO/NASA de medição efetivamente recebida por SPADATS.'
---

# C241-L52 — NORAD, SAO, SPADATS e câmeras Baker–Nunn em 1963

**Nova fonte contemporânea:** NORAD/CONAD, *Historical Summary, July–December 1963*, datado **1º de maio de 1964**, páginas impressas **55–56** (PDF índices **70–71**), hospedado como [fac-símile desclassificado pelo The Black Vault](https://documents.theblackvault.com/documents/afhistory/norad/%28U%29%201963%20NORAD%20CONAD%20History%20Jul-Dec.pdf). O relatório cobre diretamente o período da reentrada atribuída pelo catálogo ao NORAD 528, mas não identifica o 528 em nenhuma das duas páginas verificadas.

**Custódia da variante baixada em 14/11/2026:** **7.111.330 bytes**, SHA-256 `eb8682425a393b016642165a9c00b6be8868a27954ddd0e55c40c1e14da425b4`, **122 páginas** na referência PDF. A inspeção das páginas foi **visual do scan**, não inferência de OCR. O SHA certifica esta variante do espelho, não uma declaração de independência sobre o documento original guardado pelos órgãos militares. A [página institucional de história do NORAD](https://www.norad.mil/About-NORAD/NORAD-History/) lista a publicação; o host oficial do PDF respondeu HTTP 403 à tentativa de recuperar bytes nesta rodada.

**Linha do tempo documental, sem fazer dela uma série instrumental:**

- **17/07/1963, p. 55:** o JCS declarou indisponíveis as três câmeras SAO que o plano previa integrar; solicitou revisão com quatro câmeras operadas pela USAF mais Cold Lake, no Canadá, somando cinco, e esforços para obter dados Baker–Nunn da NASA para SPADATS. Solicitar dados não demonstra que tenham sido transferidos, nem seus alvos.
- **Setembro/1963, p. 56:** o NORAD preparava plano revisto de integração USAF/RCAF; participação das câmeras SAO ainda dependia de decisão e estudo. O plano tinha submissão futura prevista, não cobertura observacional comprovada no dia 08/11.
- **Outubro/1963, p. 56:** a Marinha dispensou Baker–Nunn para a finalidade específica de calibrar SPASUR; isso não significa proibição de outras observações ópticas.
- **Cold Lake, p. 56:** a câmera estava sob controle operacional NORAD desde fim de 1962; entretanto, circuitos de comunicação segura previstos para 15/11/1963 não estavam instalados até o fim de 1963. Controle e fluxo instrumental são fatos diferentes.

**Interpretação:** o texto permite catalogar **propostas, dependências de intercâmbio e obstáculos administrativos**. Não autoriza afirmar que NASA/SAO/NORAD fizeram medições independentes do 528, nem que não observaram o objeto. Uma cadeia de publicações NASA/NORAD/SAO pode reutilizar dados, de modo que contagem de sensores deve permanecer **desconhecida**, não zero e não dois. O documento não é TLE, telemetria, tabela de resíduos ou estimativa de covariância. As posições, época UTC instrumental, estação efetiva do 528, variância, natureza da peça, hora e local da reentrada permanecem `null`; **nenhuma restrição física/Lean nova foi ativada**.

**Reprodução:** `python3 -m unittest discover -s tests -p test_tle_norad_spadats_scope_c241_l52.py -v`; repetir com `python3 -O`; `python3 tools/tle_norad_spadats_scope_c241_l52.py --verify-remote` (requer curl e pypdf 6.1.3) recalcula SHA, tamanho e número de páginas. Conservar hash histórico caso a fonte altere seus bytes.

**Próxima busca:** arquivos efetivos de trocas SAO/NASA–SPADATS e logs com `1963-003B`/`NORAD 528`, UTC, estação, observável, frame e estimador de erro. Relacionado a [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396), sem reabrir o conflito de hardware B/D da C241-L51 como se fosse medição do objeto.
