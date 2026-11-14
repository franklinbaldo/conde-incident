---
type: Guide
title: 'CGEO-38: publicação IOCS 29 de 1913 e genealogia do mapa de Soper'
description: 'Dois catálogos institucionais e um fac-símile integral conectam as publicações IOCS 15 e 29 ao mapa de 1914, sem dupla contagem.'
---

# CGEO-38 | A fonte cartográfica anterior a Soper

Em 13/11/2026, foi recuperada a referência literal à **publicação 29, série I-G**, da Inspectoria de Obras contra as Seccas (IOCS), citada no mapa de Ralph H. Soper de 1914 (CGEO-37). É o *Mapa parcial do estado da Bahia*, publicado em **outubro de 1913**, com Guilherme Lane e Roberto Miller, escala **1:500.000**. Não se confunde com a publicação 34, sobre geologia.

O [instrumento de pesquisa oficial do Arquivo Nacional (DS), p. 9, índice PDF 8](https://www.gov.br/arquivonacional/pt-br/servicos/copy_of_instrumentos-de-pesquisa/academia-brasileira-de-letras.pdf), descreve o item **BR AN,RIO DS.0.MAP.5**. PDF oficial adquirido integralmente: **1.274.536 bytes**, SHA256 **f7f15d448f4ae48dd22a091e55c4a1d2e8324c114d42cb5a1dde600393d792a3**.

O [fac-símile integral do mapa 1913, Arquivo Nacional/Wikimedia](https://commons.wikimedia.org/wiki/File:Mapa_parcial_do_estado_da_Bahia.pdf) foi adquirido: **2.440.283 bytes**, SHA256 **feaae0eb8534e4f71242c01faa9dbbe71c0f7440b85e5791d8548a46306bb3dd**. Isto é uma reprodução digital de uma obra histórica, não inspeção do exemplar físico, nem fotografia aérea do ano de 1963. A inspeção de microtopônimos e cobertura de Conde dentro do fac-símile ainda está pendente.

## Uma fonte predecessora: IOCS 15 (1912)

O [catálogo oficial do fundo Francisco Bhering, p. 116, índice PDF 115](https://www.gov.br/arquivonacional/pt-br/servicos/copy_of_instrumentos-de-pesquisa/bhering-final-14-fev-13.pdf) identifica **BR AN,RIO F4.0.MAP.448**, *Mapa da bacia do rio Itapicuru, estado da Bahia*, edição de **março de 1912**, publicação **15, série I-G**, escala 1:500.000, também com Lane e Miller. O próprio instrumento reproduz uma anotação de **Duarte, 3 de fevereiro de 1917**, segundo a qual ele deixara de ser registrado por **estar incluído na publicação 29**. PDF oficial adquirido: **2.382.507 bytes**, SHA256 **17ef624688aecb8f20a08b447792cb09dddb9de763c45289b28c0a3ddabd9587**.

A declaração de 1917 é prova documental de uma relação arquivística, **não** de identidade pixel a pixel, de todos os elementos geográficos ou da direção material da cópia. O mapa original nº 15 **ainda não foi adquirido**.

## Grafo cumulativo

IOCS nº 15 (1912) → anotação arquivística de inclusão → IOCS nº 29 (1913) → fonte cartográfica declarada → Soper (1914, CGEO-37/36). As duas digitalizações do mapa Soper são duas custódias, não duas observações da paisagem. A publicação de 1913 tampouco estabelece por si só qual parcela do mapa Soper veio dela.

Os anos 1912, 1913 e 1914 descrevem **publicações**, 1917 é a **anotação de arquivo**, e novembro de 1963 é o evento investigado. Não há data instrumental de medição, erro cartográfico quantificado, perímetro do Centro de Conde em 1963, coordenadas da alegada queda nem observação orbital. Todos esses campos permanecem nulos.

**Reprodução:** `python3 -m tools.cgeo38_iocs29_lineage` valida contrato e dependências offline. Com `--map`, `--ds`, `--f4` verifica bytes inteiros, SHA256 e marcadores PDF. A workflow adquire novamente os três PDFs no GitHub Actions. Os binários não entram no Git.

**Próxima etapa:** localizar o original IOCS nº 15 e comparar visualmente sua extensão, legenda e conteúdo aos mapas de 1913 e 1914; tratar os fotoíndices USAF 63-32 como uma linhagem distinta.
