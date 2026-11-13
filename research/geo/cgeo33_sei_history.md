---
type: Guide
title: 'CGEO-33: edição cartográfica, corte de folha e cobertura efetiva'
description: 'Síntese oficial SEI de 2025 identifica programas históricos e impede inferências espaciais retroativas.'
---

# CGEO-33 | Folha cartográfica não é pegada de voo

Foi adquirido o [Plano Cartográfico do Estado da Bahia, Série Cecar 1, SEI/CECAR (2025)](https://www.ba.gov.br/sei/sites/site-sei/files/2026-03/serie_cecar_1_plano_cartografico_da_bahia_2025.pdf), seção 5.1, páginas impressas **69 e 70**. Arquivo PDF de **12.278.693 bytes**, SHA256 **267f1f30775f8a44b1c5ab17ce1bf25d303713530d006c0302e4854760fa0865**, adquirido em 13/11/2026. O texto da edição foi consultado, mas a captura visual das páginas falhou pelo tamanho do PDF. Não afirmar inspeção visual do fac-símile. A fonte de 2025 é **retrospectiva**, não uma observação realizada em 1963.

A página 69 descreve 31 folhas IBGE na escala 1:250.000 produzidas em **1949–1952 e 1956**. A série não recobriu totalmente o estado. É uma pista para procurar mapas anteriores ao incidente, mas ainda não sabemos se alguma folha abrange **Conde/BA** e essa escala não demonstra geometria de praça ou rua. A mesma página registra que folhas 1:100.000 foram produzidas por distintas organizações nas décadas de 1960–1980, com **edições coexistentes**. A edição conhecida de Esplanada MI-1850 é de **1973** (CGEO-25), posterior a 8/11/1963.

A página 70 menciona cartografia 1:25.000 produzida com interveniência da **Petrobras nos anos 1960**, em região aproximada Recôncavo/Tucano/Jatobá. Diz que **o primeiro mapeamento tinha cortes de folhas livres**; a atualização posterior de **1998** foi executada com articulação padronizada, mas mapeou apenas **partes de folhas de interesse**. Essa limitação de cobertura de 1998 **não deve ser transportada como fato do voo de 1961**. A fonte também não autentica a identidade desse programa com o **Projeto PETROBRAS 53 D** citado em catálogo secundário, nem cobre necessariamente Conde. DNOCS 213 e USAF 63-32 permanecem cadeias de referência separadas e sem fotogramas originais.

**Relevância cartográfica:** encontrar a folha MI-1850, uma entrada de catálogo ou uma escala nominal não prova a pegada real do levantamento. Faltam fotoíndice, faixa, fotograma, data individual, georreferenciamento e identificação positiva de marcos urbanos de 1958/1963. Limite de 1963, centro histórico, possível ponto de queda e erro espacial permanecem desconhecidos. Não há restrição orbital nova.

**Teste seguinte:** identificar qual das 31 cartas IBGE 1:250.000 antigas, se alguma, cobria Conde; obter fotogramas 53 D / DNOCS 213 / USAF 63-32 com data e cobertura verificadas. A verificação do contrato pode ser executada com python3 -m tools.cgeo33_sei_history e testes com python3 -m unittest discover -s tests -p 'test_cgeo33_sei_history.py'. A flag --pdf valida a reprodução integral por tamanho e SHA256.
