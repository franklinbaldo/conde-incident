---
type: Evidence
title: "CGEO-63: homografia editorial e cronologia retrospectiva da Praça Severino Vieira"
description: "Uma matéria de 2018 alterna Severiano/Severino para o mesmo festival; 1904–1960 é história retrospectiva, não geocódigo de 1963."
---

# CGEO-63 | O nome da praça não equivale à posição da queda

**Pergunta:** a diferença entre “Praça Severiano Vieira” e “Praça Severino Vieira”, em fontes modernas, representa dois logradouros? E como isso se relaciona com a “Praça Severiano Lima” mencionada na foto IBGE de 1958?

## Uma única programação usa duas grafias

O [Jornal Grande Bahia, matéria publicada em 22/02/2018](https://jornalgrandebahia.com.br/2018/02/conde-apresenta-o-1o-festival-do-coco/) (programação de 22–28/01/2018), escreve *Praça Severiano Vieira* na narração dos shows, mas *Praça Severino Vieira* na programação do mesmo Festival do Coco em Conde/BA. Os tokens literais aparecem respectivamente **2 e 7 vezes** no HTML original recuperado; as duas ocorrências de “Severiano” e as sete de “Severino” pertencem à **mesma publicação**, não a nove testemunhos.

Reaquisição HTTP 200 em 14/11/2026, **379.832 bytes**, SHA-256 `45a86bade93889c5bdf734acb96453f7973e81a81882879b2440087ac308dfeb`. Os bytes originais foram verificados em executor externo, **não versionados no Git** (limite 20 KB e respeito ao conteúdo editorial). `python3 tools/cgeo63_praca_editorial_variants.py --live` só declara correspondência se uma nova resposta tiver exatamente comprimento, SHA e contagens iguais; `--live` não integra o gate offline obrigatório.

**Interpretação restrita:** na matéria de 2018, as duas grafias se referem ao local anunciado para o mesmo festival. Isso é evidência de **variação editorial interna**, não um ato oficial de renomeação e não uma medida geométrica. Não corrigir automaticamente um nome em documentos históricos.

## Uma hipótese histórica anterior a 1963, mas retrospectiva

A [matéria local de 04/08/2025, atualizada em 09/08/2025](https://conde.portaldacidade.com/noticias/cidade/historia-de-conde-parte-iv-curiosidades-do-municipio-entre-os-seculos-xix-e-xx-2248) atribui os fatos abaixo à pesquisa de Walber Luide Andrade da Silva, sem reproduzir no texto os documentos contemporâneos correspondentes:

- Julho de **1904**: inauguração, na Ribeira, de praça em homenagem a Severino Vieira.
- **8/07/1949**: inauguração de busto de Severino Vieira na praça.
- **1960**: inauguração da nova Igreja do Senhor do Bonfim.

O conteúdo foi consultado como texto web em 14/11/2026, porém a recuperação dos bytes HTML no Ifro retornou HTTP **403**. Portanto, o estado de custódia é `WEB_TEXT_VISIBLE_BINARY_NOT_ACQUIRED_HTTP_403_IFRO`, sem tamanho ou SHA inventados. Esses três episódios são **alegações históricas secundárias publicadas em 2025**, não três fontes primárias independentes ou provas cartográficas contemporâneas.

Se confirmado em jornais, plantas, leis ou álbuns originais de 1904, 1949 e 1960, esse conjunto pode orientar uma pesquisa por marco físico reconhecível em 1958–1963. Hoje ele **não** determina posição, polígono, mudança de nome ou centro urbano de 1963.

## Dependências que não devem ser fundidas

O [processo municipal de 2020](cgeo20_centro_vila_2020.json) menciona *Praça Severino Vieira (Centro)*, mas não retroage automaticamente para 1963. A [foto IBGE de 1958](cgeo17_1958_urban_toponym_crosswalk.json) menciona *Praça Severiano Lima*; apesar do elemento nominal parecido, é **outra ocorrência literal**. A base [OSM atual](cgeo62_praca_severino_vieira.json) contém quatro objetos com o nome Severino Vieira, incluindo duas áreas e duas ruas: não há equivalência comprovada entre um deles e uma única praça histórica.

O [manifesto estruturado](cgeo63_praca_editorial_variants.json) mantém `identity_with_1958_praca_severiano_lima=null`, `identity_with_2020_severino_vieira_geometry=null`, `historical_center_polygon_1963=null`, `event_location_1963=null`, `active_constraint=false`.

**Reprodução offline:** `python3 tools/cgeo63_praca_editorial_variants.py`; `python3 -m unittest discover -s tests -p 'test_cgeo63_praca_editorial_variants.py' -v`; repetir sob `python3 -O`. O replay offline testa o contrato fixado, não autentica novamente o HTML ao vivo. O teste negativo deve rejeitar afirmações de identidade, posição e independência forjadas.

**Próxima busca discriminante:** atos de denominação/renomeação; foto identificada do busto de 1949; projeto ou implantação da igreja inaugurada em 1960; planta cadastral com referências datadas entre 1958 e 1963. Qualquer georreferenciamento exige pontos de controle, datum, revisão temporal e incerteza explicitados.
