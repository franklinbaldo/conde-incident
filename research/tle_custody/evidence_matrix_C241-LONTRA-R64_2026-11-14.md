---
type: Guide
title: "C241-R64: índice autoral húngaro identifica INTEROBS 1963 n. 2"
description: "Fac-símile bibliográfico da Academia Húngara distingue Наблюдения ИСЗ n. 2 de boletim soviético n. 32; sem observação dos objetos 527–529."
---

# C241-LONTRA-R64: identificar a série, não inventar uma medição

A coleção digital **REAL-MS**, da Academia Húngara de Ciências, disponibiliza um [fac-símile de 167 páginas](https://real-ms.mtak.hu/30094/1/1.pdf) identificado na extração por *Körlevél*. O **anexo da página PDF 93** intitula-se *Almár Iván idegennyelvű tudományos publikációinak jegyzéke* (lista das publicações científicas em línguas estrangeiras de Iván Almár). A **página PDF 95, impressa 3**, lista três itens consecutivos da série **Наблюдения ИСЗ**:

- Item **27**: cooperação internacional em observações de base, número **1**, Moscou, **1962**.
- Item **28**: *О точности базисных визуальных наблюдений, выполненных по программе ИНТЕРОБС за 1962 год*, número **2**, **Varsóvia, 1963**. O assunto é a precisão de observações visuais de base feitas em **1962**, não uma observação de novembro de 1963.
- Item **29**: cálculo de elementos orbitais instantâneos por observações de base, número **3**, **Berlim, 1964**.

A [biblioteca de Kyiv já catalogada em C241-L29](https://mao.kiev.ua/index.php/ua/gao-biblio-periodyka/sciencefilds-n) lista **Наблюдения ИСЗ n. 2 (1963)**. O anexo húngaro oferece **título de artigo e local de publicação**, permitindo dirigir a próxima busca. **Esse periódico não pode ser confundido** com a série distinta *Бюллетень станций оптического наблюдения ИСЗ*, da qual a biblioteca cataloga **números 32–37 em 1963**.

**Custódia:** download integral via executor **Ifro**, PDF de **46.217.178 bytes, 167 páginas**, SHA-256 `cc91eb383c90ecd5f15f5d2db89e08860642c6a8a683401350e97af8bb4098ac`. Páginas PDF 93 e 95 renderizadas e examinadas visualmente em 14/11/2026. O PDF original **não é a publicação de 1963**: é uma compilação bibliográfica posterior, sem data editorial original confirmada nesta análise. Hash e tamanho referem-se somente ao PDF completo da coleção húngara. O original de Varsóvia e o boletim soviético n. 32 **não foram recuperados**.

O anexo comprova uma referência bibliográfica rastreável, **não uma medição**, série negativa ou cobertura dos NORAD 527, 528 e 529. Consequência: **zero novas restrições orbitais**. Nenhuma instituição foi contatada. Próxima busca: fac-símile do n. 2 (Varsóvia 1963), texto e páginas do estudo INTEROBS, e em paralelo boletim n. 32. Não atribuir ao estudo de precisão de 1962 erro instrumental do rastreamento de 1963.

Executar `python3 -m tools.audit_hungarian_interobs_r64` e `python3 -m unittest discover -s tests -p test_hungarian_interobs_r64.py -v` em ambientes normais e otimizados; `prek run --all-files` e CI no HEAD exato continuam gates. Relacionado a [Conde #545](https://github.com/franklinbaldo/conde-incident/issues/545) e [Cafezinho #9](https://github.com/franklinbaldo/cafezinho/issues/9).
