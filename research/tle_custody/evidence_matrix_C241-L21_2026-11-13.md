---
type: Guide
title: "C241-L21: recuperada edição NASA nº 24 de 15/12/1963"
description: "Boletim NASA intermediário, linhas 527/529 auditadas e dependências explícitas sem converter datas editoriais em épocas instrumentais."
---

# C241-L21: o boletim que faltava entre novembro e dezembro

**Nova fonte primária documental:** [NASA Goddard, *Satellite Situation Report*, vol. 3 nº 24, de 15/12/1963, NTRS 19640003479](https://ntrs.nasa.gov/citations/19640003479); [PDF oficial](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf). A capa, PDF p. 2 (índice 1), imprime o volume, nº e data. Os metadados NTRS incluem **NASA-TM-X-51375**. A capa externa traz **X-533-63-1**.

O texto de abertura diz que os dados foram compilados/computados por Goddard, NORAD e Smithsonian Astrophysical Observatory **às 1200Z de 15/12/1963**. Esse instante refere-se à compilação, **não** às épocas individuais de rastreamento. A [C241-L20#1](evidence_matrix_C241-L20_2026-11-13.md) documenta canais institucionais possíveis, sem apontar qual sensor ou estação produziu cada linha.

Na tabela rotacionada *OBJECTS IN ORBIT*, **página impressa 5 / PDF p. 7 / índice zero 6**, as duas linhas foram conferidas diretamente no fac-símile em **13/11/2026**:

| Designador | NORAD por crosswalk C241-L10 | Período nodal | Inclinação | Apogeu / perigeu |
|---|---:|---:|---:|---:|
| 1963 3A | 527 | **94,6 min** | **81,88°** | **532 / 459 km** |
| 1963 3C | 529 | **91,6 min** | **81,87°** | **352 / 347 km** |

1963 3B (NORAD 528, por crosswalk posterior) **não figura** nessa seção de objetos em órbita, após o boletim de novembro ter registrado **08/11/1963** como dia catalogado de decaimento. Essa ausência em dezembro **não é outra observação terminal**, nem prova hora, posição ou identidade física do 528. As tabelas pertencem à mesma família de compilação NASA/NORAD/SAO.

**Captura PDF verificável:** 958.927 bytes; SHA-256 **d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f**. O workflow valida os bytes atuais, não faz uma nova inspeção visual de pixels; qualquer mudança da CDN exige registrar variante e reinspecionar.

## Quatro edições ligadas no grafo documental

A edição nº 24 conecta os registros previamente autenticados: [15/11, nº 22](https://ntrs.nasa.gov/citations/19640001198) (C241-L19), [30/11, nº 23](https://ntrs.nasa.gov/citations/19640002493) (C241-L18), **15/12, nº 24** (novo), [31/12, nº 25](https://ntrs.nasa.gov/citations/19640005618) (C241-L18, errata de 89,6 para **89,2**):

| Objeto | 15/11 | 30/11 | 15/12 | 31/12 |
|---|---:|---:|---:|---:|
| 527 / 1963 3A | 94,6 | 94,6 | **94,6** | 94,6 min |
| 529 / 1963 3C | 92,6 | 92,2 | **91,6** | 89,2 min |

Para 529, as **diferenças entre números publicados** são respectivamente −0,4, −0,6 e −2,4 min; os dados impressos têm uma casa decimal. Essas diferenças não podem ser divididas por 15/16 dias para inferir arrasto ou uma taxa orbital, pois **as datas de publicação não são épocas dos elementos** e faltam dependências instrumentais. A edição nº 21 continua não recuperada; localizar nº 24 não resolve essa outra lacuna.

## Integração cumulativa, não mera transcrição

O [ledger](nasa_ssr_dec15_1963_C241-L21.json) registra valores, páginas, bytes, relações de dependência e desconhecidos. A extensão [C241-L21 do grafo](../constraints/ssr_dec15_1963_observables_C241-L21.json) conecta dois operadores observáveis de período nodal catalogado a estado orbital, época latente, frame e modelo de forças; inclinação/apogeu/perigeu preservados com unidade. As épocas latentes, frame, sigma, covariância e estação permanecem **null**. A integração é **CONNECTED_PENDING_CALIBRATION**, com **duas novas observáveis documentais, zero amostras instrumentais independentes e domínio Theta inalterado**; será elegível a restrição física apenas após recuperar os parâmetros e erros necessários e validar o modelo.

O [auditor](../../tools/tle_nasa_ssr_dec15_audit.py), [29 contraprovas/testes](../../tests/test_tle_nasa_ssr_dec15_audit.py) e [workflow](../../.github/workflows/tle-nasa-ssr-dec15.yml) cruzam o documento com C241-L18/L19 e revalidam o PDF por hash. O checksum autentica a captura atual, não linhas TLE de 1963. Fonte instrumental por objeto, par TLE original, frame, identidade física do 528, modelo de erro e hora/lugar de reentrada seguem **não recuperados**. RAAN 284,1520° permanece inativa e 198,5261° secundária. Nenhuma prova Lean física nova; **Conde indeterminado**.
