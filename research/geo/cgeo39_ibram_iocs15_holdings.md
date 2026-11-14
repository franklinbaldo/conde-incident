---
type: Guide
title: 'CGEO-39: exemplar catalogado no Museu da República para IOCS 15'
description: 'Um segundo caminho de custódia para o mapa do Itapicuru (1912), sem confundir catálogo, fac-símile e medição.'
---

# CGEO-39 | Um caminho adicional para o original IOCS nº 15

O [Museu da República (IBRAM), subsérie Mapas de Epitácio Pessoa](https://atom-museurepublica.museus.gov.br/index.php/mapas-2), classificada em **BR RJMRAHI EP-IC-MA**, lista literalmente **Mapa da Bacia do Rio Itapicuru (BA)** como quarto título de um conjunto de 11 mapas da antiga Inspetoria de Obras Contra as Secas (IOCS). O inventário descreve **12 itens físicos, incluindo uma duplicata**, e conservação regular. Este acervo oferece uma rota documental **adicional ao fundo Francisco Bhering do Arquivo Nacional** (CGEO-38).

O [instrumento de pesquisa integral do IBRAM](https://atom-museurepublica.museus.gov.br/downloads/epitacio-pessoa.pdf) foi adquirido em 13/11/2026, **136.248 bytes**, SHA256 `2f99bbd2594254ce484b5c905907852eb1b6142f6c44d94913837aeb89edca4f`. A descrição está na página impressa **27** (índice PDF **26**). O PDF contém **a descrição do acervo, não o próprio mapa de 1912**. Não há número individual de item publicado nesse trecho, nem base para inferir a qual dos onze mapas se refere a duplicata.

A ficha anterior do [Arquivo Nacional, F4.0.MAP.448](https://www.gov.br/arquivonacional/pt-br/servicos/copy_of_instrumentos-de-pesquisa/bhering-final-14-fev-13.pdf), identificara `Mapa da bacia do rio Itapicuru, estado da Bahia` como **IOCS publicação 15**, março de 1912, 1:500.000; uma anotação de 1917 diz que esse conteúdo fora incluído na publicação 29 (1913). O IBRAM confirma uma **obra de título correspondente no conjunto de holdings**, mas não comprova que se trate da *mesma folha física* do Arquivo Nacional, que a edição seja idêntica, nem que o objeto físico tenha sido inspecionado nesta rodada.

## Limites e próxima aquisição

O grafo marca a aresta `SAME_TITLE_FAMILY_CANDIDATE_DIFFERENT_CATALOGUES`; não adiciona observação independente nem geometria. Não se infere que o mapa cubra o centro urbano de Conde, nem a precisão cartográfica, fotogramas de 1963 ou localização de queda. Permanecem nulos centro de 1963, ponto da alegada queda, precisão horizontal e data de voo.

Próximo passo: obter **cota de item, condições de consulta e fac-símile específico** do mapa de 1912 no Museu da República ou Arquivo Nacional, sem afirmar contato institucional já realizado; só então comparar feições com IOCS 29 e Soper 1914. O fotoíndice USAF 63-32 é outra linha de aquisição, [issue #558](https://github.com/franklinbaldo/conde-incident/issues/558).

**Reprodução:** `python3 -m tools.cgeo39_ibram_iocs15` valida o contrato; com `--pdf arquivo.pdf` verifica PDF integral (comprimento + SHA256) sem fixtures sintéticas. CI baixa novamente o instrumento oficial.
