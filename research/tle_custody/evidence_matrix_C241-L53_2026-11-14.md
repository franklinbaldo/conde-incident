---
type: Guide
title: 'C241-L53: Smithsonian RU263, Cold Lake e a cadeia de troca óptica de 1963'
description: 'Inventário oficial localiza séries operacionais e técnicas de estações SAO/RCAF; não demonstra recebimento SPADATS nem observação do NORAD 528.'
---

# C241-L53: arquivos de estação Cold Lake, Irã e Curaçao (1959–1965)

**Fonte primária quanto à existência de acervos:** Smithsonian Institution Archives, *Satellite Tracking Station Records, 1953–1968*, **Record Unit 263** (82 caixas, 41 pés cúbicos), [catálogo institucional](https://siarchives.si.edu/collections/siris_arc_216832) e [inventário PDF](https://sirismm.si.edu/EADpdfs/SIA.FARU0263.pdf). É **instrumento de pesquisa arquivística**, não registro óptico instrumental de um alvo. A variante obtida em **14/11/2026** tem **192.142 bytes**, **58 páginas PDF** (56 páginas impressas) e SHA-256 `0648a4807160099c1c5146f9a90e8ab291af8cb7a0eff1f5a9ca0bc53e074603`. O PDF original foi conferido por texto extraído e por inspeção visual das páginas relevantes. O digest identifica os bytes acessados, não os documentos ainda não consultados dentro das caixas.

| Série e caixa | Página impressa; índice PDF de base zero | Escopo catalogado | Critério de abertura |
|---|---|---|---|
| Série 2, caixa **36** | **14; 15** | Cold Lake, Canadá, **1963–1965**, arquivos da Station Operations Division | Correspondência/registro sobre integração e circulação dos dados SPADATS/SAO/RCAF em 1963 |
| Série 8, caixa **67** | **43; 44** | Cold Lake, Canadá, **1961–1963**, arquivos de engenharia | Estado de câmera, relógio, correção temporal e calibração contemporânea |
| Série 9, caixa **72**, código **#420** | **47; 48** | Cold Lake, Canadá, **Operations, 1963–1965**, arquivos de engenharia | **Nova primeira prioridade:** comunicações técnicas, disponibilidade e manutenção do equipamento, possível rastreio da transferência SAO–SPADATS |
| Série 9, caixa **72**, código **#130** | **47; 48** | Cold Lake, Canadá, **Inventory and audits, 1963** | Inventário técnico para testar qual equipamento havia, sem presumir funcionamento ou observação |
| Série 8, caixa **69** | **43; 44** | Irã, **1959–1963**, arquivos de engenharia | Identificação física da estação Shiraz/SC-8/9008 e erros do equipamento, se documentados |
| Série 8, caixa **68** | **43; 44** | Curaçao, **1959–1963**, arquivos de engenharia | Controle comparativo de instrumentação e cronologia; sem assumir mesmo objeto |

**Complemento de 14/11/2026 na mesma fonte C241-L53:** inspeção visual da p. impressa **47** (índice PDF de base zero **48**) localizou duas pastas adicionais sob o cabeçalho *Cold Lake, Canada*: a série 9, caixa 72, **#420 Operations 1963–1965** e **#130 Inventory and audits 1963**. O cabeçalho e ambas as linhas foram verificados na imagem do fac-símile e no texto extraído de um novo download cujo tamanho e SHA-256 coincidem exatamente com os já custodiados. **São duas pastas do mesmo inventário, não duas novas fontes nem dois sensores.** Seu conteúdo ainda não foi aberto.

A série 2 declara manter arquivos de estações da USAF e RCAF cooperantes, inclusive Cold Lake. A série 8 descreve correspondências técnicas sobre problemas, operação e manutenção das câmeras. A descrição de uma pasta, por si só, **não prova que houve observação de um satélite específico**. O inventário ainda avisa que os registros foram reorganizados sob códigos numéricos por assunto, inclusive materiais anteriores a 1964. O pedido de arquivos precisa mencionar **série, caixa e assunto/intervalo temporal**, não apenas título de estação.

**Conexão verificável:** a fonte NORAD *Historical Summary July–December 1963*, p. 55–56, **C241-L52**, documenta propostas e obstáculos de transferência óptica envolvendo SAO, NASA e Cold Lake, com circuitos seguros não instalados até o fim de 1963. As caixas RU263 são pistas para buscar **comprovação ou refutação documental da transferência efetiva**. As coleções RU263 e RU478 pertencem ao mesmo ecossistema SAO; não são, por isso, sensores independentes. Nenhum documento de pasta foi aberto nesta rodada, e não há observação individual dos objetos 527/528/529, época UTC, estação atribuível ao 528, ângulos, resíduos ou sigma instrumental. **Não há nova restrição física nem demonstração de reentrada em Conde.**

**Próxima aquisição:** solicitar prioritariamente série 9/caixa 72/#420 (Cold Lake, Operations 1963–1965) e #130 (Inventory and audits 1963), em paralelo à série 2/caixa 36 e série 8/caixa 67, perguntando por relatórios datados **julho–novembro de 1963** que indiquem o identificador `1963-003B` ou `NORAD 528`, remetente/destinatário, timestamp, clock correction e se houve transmissão/recebimento efetivo. A ausência em pastas consultadas não deve ser extrapolada como ausência global de observações.

**Reprodução:** `python3 -m unittest discover -s tests -p test_tle_sao_ru263_station_files_c241_l53.py -v`, repetir com `python3 -O`; `python3 tools/tle_sao_ru263_station_files_c241_l53.py --pdf <arquivo>` (requer `pypdf==6.1.3`); `--live` busca a mesma variante remota e interrompe se o SHA mudar. O manifesto JSON é `research/tle_custody/sao_ru263_station_files_C241-L53.json`. Referências: [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396), [Cafezinho #14](https://github.com/franklinbaldo/cafezinho/issues/14).
