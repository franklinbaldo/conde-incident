---
type: Guide
title: "C241-R66: periódico polonês do último trimestre de 1963 já estava impresso em outubro"
description: "Colofão original da Postępy Astronomii XI(4), fac-símile integral e limite temporal da busca por relatos de novembro de 1963."
---

# C241-LONTRA-R66 · corte editorial antes de 7 de novembro

**Fonte original conferida:** *Postępy Astronomii*, tomo XI, fascículo 4, Varsóvia, **outubro–dezembro de 1963**. [PDF institucional Urania](https://www.urania.edu.pl/sites/default/files/archiwum/postepy_astronomii_1963_04.pdf#page=2). A capa é a página PDF 1. No **colofão, página PDF 2**, está indicado **“Oddano do druku 12 X 1963 r.”** (entregue à impressão em 12/10/1963) e **“Druk ukończono w październiku 1963 r.”** (impressão concluída em outubro de 1963). A página foi conferida visualmente, não apenas por OCR.

**Custódia:** documento binário integral baixado no executor Ifro em 14/11/2026, **5.014.393 bytes, 76 páginas, PDF 1.6**, SHA-256 `d83044a1bcbb43b8448614adf7778e8ee811776925160b7bc86840c4da3084c2`. A verificação da integridade dos bytes é distinta do teor original impresso. Não colocar o PDF no Git. Fonte da série: [índice institucional de 1963](https://www.urania.edu.pl/archiwum/postepy-astronomii-1960-1969).

**Conclusão negativa delimitada:** apesar de anunciado como fascículo do quarto trimestre, o exemplar impresso foi concluído **antes de 07/11/1963**; portanto **não pode conter, na impressão original, uma reportagem contemporânea sobre o acontecimento de 07/11/1963**. Não inferir disso que observações polonesas de novembro não existiram, que outras publicações não as divulgaram, que suplementos posteriores não foram acrescentados, ou que a narrativa de Conde é falsa. A página final menciona planos de assinatura para 15/11, mas não altera a data de encerramento gráfico declarada no colofão. A busca deve migrar a **cadernos/boletins de observação** e impressos posteriores.

**Sem promoção física:** este PDF não fornece uma observação individual dos NORAD 527/528/529 com estação, época, coordenadas ou calibração. Identificadores 1151–1162 das estações polonesas pertencem à [PR #977](https://github.com/franklinbaldo/conde-incident/pull/977), não à medição neste documento. **Novas restrições: 0.** Nenhuma instituição foi contatada.

Reprodução: `python3 -m tools.audit_polish_1963_print_cutoff_r66`; `python3 -m unittest discover -s tests -p test_polish_1963_print_cutoff_r66.py -v` e sob `python3 -O`. Verificar também o HEAD exato, `prek run --all-files`, logs e controles negativos. Relacionado: [Conde #545](https://github.com/franklinbaldo/conde-incident/issues/545) e [Cafezinho #9](https://github.com/franklinbaldo/cafezinho/issues/9).
