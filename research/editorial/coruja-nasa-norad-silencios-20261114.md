---
type: Guide
title: "R35: boletins NASA não equivalem à custódia integral das medidas NORAD"
description: "Cadeia documental de divulgação pública 1961–1965; distinção entre fontes, memorandos, boletins e observações instrumentais."
---

# C241-CORUJA-R35: silêncio de publicação não é ausência de sensor

**Pergunta:** que prova sobre NORAD 528 pode ser tirada do conteúdo ou da ausência de uma linha no *Satellite Situation Report*?

## Originais e eventos distintos

| Ocorrência | Data do fato | Data da publicação | Fonte/posição | Alcance e estatuto |
|---|---|---|---|---|
| Acordo GSFC–NORAD (anexo 4) | 07/11/1961 | 22/03/1965 | House Report 197, pp. impressas 13–14 | Regras de transferência de catálogo público e dados classificados; não é registro 528 |
| Acordo GSFC–NORAD (anexo 5) | maio/1962 | 22/03/1965 | House Report 197, pp. 15–17 | Regras NAVSPASUR e dados de sensor. Já catalogado no [grafo do Morcego](../constraints/morcego_1963_tracking_release_policy.json) |
| Hiato de boletins / A-Tau | 31/08 a 10/10/1962 | exame publicado 1965 | House Report 197, pp. 8–9 | Acusação e depoimento sobre omissões na divulgação de satélites soviéticos, não do 528 |
| Audiências NASA | 23/05 e 06/06/1963 | notícia AP 24/05/1963; relatório 1965 | *Oregon Statesman* p.22; House Report 197 pp. 4–5 | Mesma audiência/linhagem, **não** duas observações |
| Crônica NASA sobre mudança de escopo SSR | 16/01/1963 | 1964 | NASA SP-4004 p. 14 | Frase administrativa a contrastar com boletins reais; não prova que NASA deixou de catalogar 527–529 |
| Boletim NASA nº 22 | as-of a conferir no fac-símile | 15/11/1963 | NTRS 19640001198 | Publicação de catálogo, não tempos/sensores originais do 528 |

## Custódia nesta rodada

- **House Report 197**, 89º Congresso, 1ª sessão, aprovado 22/03/1965: [PDF oficial GovInfo](https://www.govinfo.gov/content/pkg/SERIALSET-12667_05_00-002-0197-0000/pdf/SERIALSET-12667_05_00-002-0197-0000.pdf).
- Download HTTPS integral no Jatobá em 14/11/2026: **24 páginas**, **SHA-256 `a08b4c505a37c09d1eb9c33ed14cc56228fd5e67f7ec1645f38554310bd60ca0`**; tamanho aproximadamente 8,9 MiB. Texto indexado da fonte e seções 1, 4, 7–9, 13–14 consultado. Tentativas de screenshot pelo leitor web terminaram em timeout. **Não afirmar inspeção visual de todas as folhas**. Sem republicar imagem do documento.
- Texto do próprio House Report 197: pp. 7–9 definem canal NASA/NORAD/SAO, hiato de 40 dias, sequência A-Tau e regras de sigilo; anexos 4–5 reproduzem acordos, mas a filiação textual ao evento é a mesma fonte parlamentar.
- Texto do SP-4004 p. 14 identificado em [PDF NASA](https://www.nasa.gov/wp-content/uploads/2023/04/sp-4004-1963.pdf#page=22), cuja crônica se baseia em fontes públicas. O enunciado sobre mudança do SSR não foi auditado contra todas as edições; `CLAIM_PENDING_RECONCILIATION`.

## Interpretação e teste

Amostragem pública de catálogo != observação instrumental bruta. Acordo NORAD–NASA não implica automaticamente classificação efetiva de documento referente ao **528**. O depoimento sobre omissões soviéticas não autoriza inferir retenção de medição de satélite militar americano. A cadeia `NORAD/SPADATS -> NASA SSR -> catálogos posteriores` não cria independência estatística por republicação.

**Próximo teste discriminante:** observar arquivo original 1963 de sensor do 528: NORAD ID inequívoco, estação, instante e escala de tempo, observável, referencial e `sigma` ou calibrador; comparar com edição do SSR e distinguir publicação de época instrumental. Caso contrário, `THETA_UNCHANGED`.

**Reutilização, sem duplicar fonte:** [Morcego PR #214](https://github.com/franklinbaldo/conde-incident/pull/214), C90#1/C132#1, [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396).
