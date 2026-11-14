---
type: Guide
title: 'C241-LONTRA-R52: localizadores verificáveis para STL Space Log v.3 n.4'
description: 'Dois localizadores independentes da reprodução NASA, sem fac-símile do fascículo, sem unidades e sem observações de novembro.'
---

# C241-LONTRA-R52 · O original STL tem pista física e índice digital

O quadro **B-12** da [NASA TM X-59315](https://ntrs.nasa.gov/api/citations/19670008638/downloads/19670008638.pdf) já foi custodiado em [C241-LONTRA-R51](stl_space_log_nasa_r51.json): declara a reprodução do *STL Space Log*, **volume 3, número 4**. Esta rodada não recuperou o fascículo original, mas encontrou duas rotas bibliográficas novas:

1. [Bolerium Books, inventário de 26 fascículos](https://www.bolerium.com/pages/books/275244/space-log-26-issues): o inventário lista expressamente **volume 3, números 1, 2 e 4** entre os exemplares descritos. É um catálogo comercial secundário, **não** uma digitalização consultada nem confirmação de disponibilidade física permanente. A busca web expôs o texto; o acesso direto do Jatobá retornou **HTTP 429**.
2. [Google Books, *TRW Space Log*, volume 3](https://books.google.com/books?id=uUhwtQJoegAC): a ficha apresenta ano **1963**, procedência **University of Colorado Boulder** e digitalização em **9/05/2023**. O acesso HTTP ao índice respondeu **200** no Jatobá. O texto exibido é **somente ficha/trechos**: não foi confirmado que essa digitalização contém o **número 4**, nem foram lidas suas páginas originais.

O terceiro elo permanece a **reprodução posterior da NASA**; seus números pareados (94,7/94,6 min; 298/286 e 322/334 de altitude, unidade não fixada; 82,0°/81,9°) são da tabela reproduzida, **não** medições novas. Também não se demonstrou derivação da tabela soviética de 1964 (459/533 km, 94,66 min, 81,89°) a partir desse fascículo. Não atribuir páginas impressas, SHA-256 do n.4 ou unidade de altitude sem seus bytes e legenda.

**Estado:** localização editorial e inventário bibliográfico, com **zero observações independentes dos NORAD 527/528/529 nos dias 7–9/11/1963**, zero sensores adicionados e zero restrições físicas ativadas. Nenhum contato externo foi realizado. [Manifesto de limites](stl_space_log_locator_r52.json) e [auditoria](../../tools/audit_stl_space_log_locator_r52.py) impedem promover índice/snippet a fac-símile.

**Próximo teste verificável:** consultar o exemplar físico do v.3 n.4 ou visualizar integralmente o volume digitalizado, confirmar sumário, páginas e legenda de unidade e depois confrontar as linhas 1963-003A/B/C com a reprodução NASA e outras fontes. Não inferir observação de novembro por referência cruzada.
