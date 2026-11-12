---
type: Guide
title: "CGEO-13: mapas MME 1985 de Conde e Jandaíra no Memória SPU"
description: "Custódia catalográfica, IDs, escalas, UTM não calibrada e limites epistêmicos em 1963."
---

# CGEO-13 — duas fichas de mapas municipais de 1985

**Pergunta:** há fontes institucionais identificáveis para confrontar a cartografia de Conde e Jandaíra? **Sim: duas fichas de acervo da Secretaria do Patrimônio da União (SPU)**, mas não os fac-símiles inspecionados, nem uma reconstituição de limites de 1963.

## Ocorrências e custódia

- **Conde (BA):** [ficha com número SPUnet 2020200296040](https://memoria-spu.gestao.gov.br/acervo-historicodesativado/ibge-conde-ba-1985/), [ficha alternativa](https://memoria-spu.gestao.gov.br/acervo-historico/ibge-conde-ba-1985/), registro digital `Reg6345_0006`. A ficha cataloga cópia do Mapa Municipal Estatístico (MME) IBGE com revisão de **setembro de 1985**, escala **1:100.000**, menção textual à quadrícula **UTM, fuso 24**, e ao meridiano 39° WGr. Registra complementação por **MMC 1970** ao sul do paralelo 12° S.
- **Jandaíra (BA):** [ficha SPU](https://memoria-spu.gestao.gov.br/acervo-historico/ibge-jandaira-ba-1985/), registro digital `Reg6341_0002`. Cópia MME IBGE revista em **setembro de 1985**, escala **1:50.000**, menções UTM/fuso 24 e 39° WGr. A ficha menciona Conde e Rio Real, sem comprovar a posição cartográfica de um vértice comum.

As fichas identificam SPU-BA como origem, SPU-RJ como custodiante e suporte físico **cópia em papel manteiga**. A data original da elaboração cartográfica, **datum**, época geodésica, parâmetros completos da projeção e erro posicional não foram verificados. **Não** atribuir EPSG unicamente com base no termo UTM/fuso 24.

## Acesso e independência

As URLs oficiais dos PDFs estão no contrato `cgeo13_spu_mme_1985_catalogue.json`. A aquisição dos PDFs **não se completou** no leitor remoto por tamanho do arquivo (aproximadamente 11 e 22 MB); não se conhecem SHA256 nem o conteúdo visual efetivo das cartas nesta entrega. Os dados acima provêm **das descrições catalográficas**, não da leitura dos mapas. Não transcrever de fichas geometrias ou coordenadas inexistentes.

São duas ocorrências arquivísticas distintas da **mesma família IBGE MME**, sem prova de levantamentos independentes. As revisões em 1985 e a dependência cartográfica de 1970 **sucedem o incidente de 08/11/1963**. As fichas não validam a continuidade normativa de 1944/1953 nem substituem os anexos jurídicos ainda não autenticados.

## Interface ao Castor

`python3 -m tools.cgeo13_spu_mme --check --date 1963-11-08` valida as fichas e emite situação **CATALOGUES_READ_FACSIMILES_NOT_ACQUIRED**. `python3 -m unittest tests/test_cgeo13_spu_mme.py -v` testa alteração adversarial de geodésia, identificação, linhagem, fac-símile e uso orbital indevido.

**Aresta cumulativa:** CGEO-09/10/11/12 → duas fichas MME 1985 → família cartográfica IBGE MME → `1963_LEGAL_BOUNDARY_LATENT` com transferência temporal **não validada**. A matriz congelada C001–C238 não é modificada. Polígono municipal válido em 1963, precisão, datum, posição de evento e pertinência permanecem `null`, e `can_constrain_reentry=false`.

**Próxima prova discriminante:** adquirir e verificar integralmente os dois PDFs oficiais, hashes e legenda/rodapé; procurar antecedentes de 1963 e confrontar documentação original dos limites com a carta georreferenciada e erro justificado. Nenhum local de reentrada foi inferido.
