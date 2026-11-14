---
type: Evidence
title: 'CGEO-47: fotoíndices NARA de 1942–1945 perto de Conde'
description: 'Duas unidades documentais RG 373/M1765 e 14 fac-símiles JPEG autenticados, incluindo mapa-base com Conde, sem alegar fotografias do centro ou geometria de 1963.'
---

# CGEO-47 | NARA: sobreposições de voo anteriores a 1963

**Descoberta em 14/11/2026.** A busca candidata `11S037W` da CGEO-46 não estava vazia: a API efetiva de catálogo é `/proxy/records/search`, não o endpoint genérico `/api/v2/` que retorna apenas o HTML da aplicação. Foram localizadas duas unidades do Record Group 373, série 306062, microfilme M1765, rolo 317:

| Célula | Unidade NARA | Intervalo impresso no cartucho | Digitalizações próprias |
|---|---|---|---|
| [11S037W](https://catalog.archives.gov/id/46716637) | `46716637` | **1942–1943** | 6 JPEGs (`00245`–`00250`) |
| [11S038W](https://catalog.archives.gov/id/46716645) | `46716645` | **1942–1945** | 8 JPEGs (`00251`–`00258`) |

O cartucho de `m1765-317-00245.jpg` declara `S 11-00-00 / W 37-00-00`, `1942 - 1943`. O de `00251` declara `S 11-00-00 / W 38-00-00`, `1942 - 1945`. Esses são **períodos do conjunto de overlays**, não datas autenticadas de cada negativo. Ambos são anteriores a 8/11/1963.

**Observação direta decisiva:** o mapa-base `m1765-317-00246.jpg` tem o topônimo **Conde** junto à costa, além de Esplanada, Jandaíra, Acajutiba e Itanhi. Trata-se de uma reprodução de mapa para alinhar sobreposições, não de fotografia aérea da cidade. Os demais JPEGs são folhas transparentes/diagramas de faixas com campos de datas, missões e exposições. Podem apontar fotografias aéreas **dos anos 1940**, mas a cobertura exata do centro de Conde ainda não foi demonstrada. O índice vizinho 11S038W mostra outros levantamentos de 1942–1945; nenhuma ponte de posição temporal está autorizada só pelo topônimo.

## Custódia verificável

- Fonte primária: [NARA RG 373, guia para fotografia aérea de países estrangeiros](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography). O próprio NARA explica que *overlay*, `spot number`, exposição e localizador de lata são etapas distintas.
- Consulta bruta de `11S037W`: `https://catalog.archives.gov/proxy/records/search?limit=10&page=1&q=11S037W`; resposta JSON adquirida, 6.129 bytes, SHA-256 `d2dc4cbfc430c1b2c58cb4ca0f280143dcdeae273d4356cdfb7b52d1ec209069`.
- Consulta bruta de `11S038W`: mesma consulta com chave `11S038W`; resposta JSON adquirida, 6.791 bytes, SHA-256 `605ec940469120640082f1defc59250067e2b60e8a8e0eab773aa4e298f5c298`.
- **14 JPEGs integrais adquiridos via HTTP 200**, conferidos por tamanho, marcador de JPEG e SHA-256 individuais, todos enumerados em `cgeo47_nara_m1765_conde_pre1963.json`. As leituras online foram repetidas, com 14/14 hashes corretos. Nenhum JPEG foi re-hospedado no Git.
- Exemplo de mapa-base com Conde: [NARA `m1765-317-00246.jpg`](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00246.jpg), 2.254.327 bytes, SHA-256 `902ce5bb15f6b40ddeecd793ec6407d3728a880e91cfd0d455519bdddbd33dda`.
- Exemplo de overlay de voo: [NARA `m1765-317-00248.jpg`](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00248.jpg), 2.519.162 bytes, SHA-256 `21016e6c141d5ac495893e13bc9a4b01bbf992e596416054fd0c03c164f3d2a0`.

## Limite científico e próxima tarefa

**Confirmado:** existem registros arquivísticos e catorze imagens de índices e mapas dos quadrantes selecionados; existe mapa-base rotulado *Conde*; o intervalo editorial da coleção antecede o incidente de 1963. **Não confirmado:** negativas ou ampliações das fotografias reais; correspondência entre um contorno de exposição e a sede de Conde; georreferenciamento e precisão do mapa-base; posição do centro em novembro de 1963; independência da série SGB/USAF 63-32 (1964–1970). Registro `same_flight_as_sgb=null`, posição da queda `null`, nenhuma restrição orbital.

Próximo ensaio falsificável: alinhar **cada overlay original** com o mapa-base com controles visuais de latitude/longitude e 30 minutos, verificar se os polígonos de exposições atravessam a marca **Conde** (com erro de alinhamento), transcrever diretamente dos cabeçalhos os identificadores de missão e *spot number* pertinentes e procurar negativos originais pelo localizador NARA. **Não usar as coordenadas do mapa como geodesia de 1963 sem validação.** Não contactar instituições externamente sem autorização.

Reprodução determinística: `python3 tools/cgeo47_nara_m1765.py` (contrato offline); `python3 tools/cgeo47_nara_m1765.py --live` (duas respostas de catálogo e 14 JPEGs completos); `python3 -m unittest discover -s tests -p 'test_cgeo47_nara_m1765.py' -v` (controles negativos).
