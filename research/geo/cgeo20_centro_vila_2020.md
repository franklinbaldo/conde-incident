---
type: Guide
title: "CGEO-20: distinção espacial nominal do Centro e da Vila de Conde"
description: "Documento municipal de 2020 distingue os nomes; sua geografia não pode ser retroprojetada ao relato FBIS de 1963"
---

# CGEO-20: qual centro da cidade?

**Descoberta documental:** a Prefeitura de Conde (BA), no processo administrativo **024/2020**, Dispensa **010/2020**, lista na capa (p. 1) **“CENTRO DA CIDADE, VILA DO CONDE”**. A solicitação datada de **26 de fevereiro de 2020** (p. 2) distingue **“Praça Severino Vieira (centro)”** de **“Praça Vila do Conde (Vila)”**. Conferi as imagens das duas páginas do [PDF original municipal](https://www.conde.ba.gov.br/Handler.ashx?f=f&name=PADISP10.pdf&query=81844712-82f9-45bd-9201-d30b853780a2.pdf) em 13/11/2026. Os bytes PDF não foram adquiridos integralmente; SHA256 permanece não verificado. Repetições no mesmo processo não criam testemunhas independentes.

O [blog local de 26/03/2014](https://condebahia.wordpress.com/2014/03/26/) nomeia uma passarela entre Conde e Vila do Conde e outra legenda a descreve sobre o Rio Itapicuru. São afirmações editoriais publicadas em **2014**. Não demonstram a data da construção nem a existência da travessia em **1963**.

## Relação cumulativa com a investigação

1. **CGEO-17 / IBGE 1958**: Praça Severiano Lima, igreja do Senhor do Bonfim, Rua do Carro, Rua Marechal Floriano e Prefeitura. Não equiparar por semelhança de nome a praça Severiano Lima à Praça Severino Vieira de 2020.
2. **CGEO-19 / blog de 2012**: fotografias *atribuídas* a 1959 na **Vila do Conde**, incluindo Nossa Senhora do Monte, não são necessariamente fotos do centro referido em 1963.
3. **CGEO-18 / FBIS–Rádio Tupi 1963**: a expressão inglesa *FELL IN THE CENTER OF THE CITY* não especifica praça, bairro, igreja, nem preserva as palavras originais em português.

**Delta científico:** a distinção de topônimos do documento municipal de 2020 passa a integrar o grafo e evita a premissa implícita de que Vila histórica e Centro comercial atual são a mesma área. A edição de 2020 não prova que essas unidades tenham sido definidas igualmente em 1963. As duas interpretações do relato de 1963 ficam ligadas a entidades nominais *candidatas*, sem seleção arbitrária. Não se conclui que o centro de 1963 fosse um ou outro.

O [contrato JSON](cgeo20_centro_vila_2020.json) exporta ponto e polígono de 1963, limite entre Centro/Vila, ponte em 1963, ponto de impacto, datum e precisão como desconhecidos. Não há nova restrição orbital; estado **CONNECTED_PENDING_HISTORICAL_SPATIAL_BRIDGE**.

**Verificação offline:** executar python3 -m tools.cgeo20_center_vila e python3 -m unittest tests.test_cgeo20_center_vila -v. Testes adversariais impedem promoção de observações modernas a posição de impacto, precisão ou continuidade temporal.

**Próxima fonte discriminante:** uma planta urbana de 1950–1963 com os topônimos e vias, provas contemporâneas sobre travessia do Itapicuru e transcrição portuguesa da Rádio Tupi. Verificar periodização e georreferenciamento antes de produzir qualquer faixa espacial.
