---
type: Guide
title: 'CGEO-41: fac-símile adquirido da publicação IOCS 14 (março de 1912)'
description: 'Fonte cartográfica primária verificada por bytes e hashes, distinta do mapa Itapicuru nº 15 ainda não adquirido.'
---

# CGEO-41 | Recuperamos o mapa IOCS nº 14, não o nº 15

Em **14/11/2026**, obtivemos o PDF integral de [Mapa de parte dos Estados de Pernambuco, Piauí e Bahia](https://commons.wikimedia.org/wiki/File:Mapa_de_parte_dos_Estados_de_Pernambuco,_Piau%C3%AD_e_Bahia_1912.pdf), publicação **nº 14, série 1-G**, da Inspetoria de Obras Contra as Secas, datada nominalmente de março de 1912, escala impressa 1:500.000. A página do acervo digital indica **Arquivo Nacional, BR RJANRIO DS.0.MAP.22**. O texto de legenda recuperável do PDF identifica nº 14, Guilherme Lane, Roberto Miller e M. Arrojado Lisboa; a revisão cartográfica integral das feições ainda não foi feita.

O arquivo de 1 página, adquirido da distribuição pública do Commons em duas rotas com digest idêntico, mede **1.803.202 bytes**, SHA-256 `f0ca966501154833d8fd011b4e00c5e50a9c148b20233f3578dc94706c10340f`, SHA-1 `3920fdc7e8db516af62eb8f60ac2089ed5c55646`. O SHA-1 coincide com o índice estruturado do Commons e não substitui o SHA-256 integral aferido. O metadado de digitalização de **17/07/2018** e o upload de **14/10/2021** **não** datam o levantamento de 1912.

**Não confundir** este fac-símile da publicação nº **14** com a publicação nº **15**, *Mapa da bacia do rio Itapicuru*, registro Arquivo Nacional **F4.0.MAP.448**, também de 1912, cujo original segue sem aquisição efetiva (CGEO-38 a 40). O mapa IOCS nº **29**, de 1913, identificado como **DS.0.MAP.5** (CGEO-38), é outra obra. A sequência 14 → 15 → 29 **não é genealogia comprovada**, e coincidência institucional não significa independência de levantamentos. Não usar uma obra substituta como se fosse a outra.

A validação `python3 -m tools.cgeo41_iocs14_facsimile --pdf caminho.pdf` verifica bytes, hash e identidade documental. Sem o argumento, valida apenas o contrato, não a disponibilidade da fonte. A CI faz download novo da URL explícita e executa ambos os testes adversariais e replay integral; eventuais falhas de rede serão reportadas separadamente.

A cobertura espacial exata do nº 14, a presença do topônimo Conde, seu datum, georreferenciamento, o centro de Conde em novembro de 1963 e a queda alegada **não foram demonstrados**. Toda geometria é nula e nenhuma restrição orbital é ativada. A prioridade fotocartográfica [#558](https://github.com/franklinbaldo/conde-incident/issues/558) permanece em aberto.
