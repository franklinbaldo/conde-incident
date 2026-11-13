---
type: Guide
title: '🦅 G36: revisão retrospectiva, 13 integrações e custódia Wayback'
description: Parecer científico, editorial e de software da janela G36, com contraprovas sintéticas.
---

# 🦅 G36: janela retrospectiva, 13 integrações

**Corte exclusivo:** `0d0f51f0eec06421b895372b6390d7f309ad61fa` (memória privada G35).
**Corte inclusivo:** `070481978ae7493ecae19d82acfc144072f792bb`, congelado antes da PR corretiva. **13 integrações** na primeira linha de pais: 11 squash (#429, #430, #431, #436, #434, #437, #439, #441, #442, #444, #443) e dois merges convencionais (#432 e #440). **15 commits no DAG** (dois laterais), nenhum commit direto. SHAs, pais, HEADs autorais, arquivos alterados e resultados `check-runs` de cada SHA de `main`: [manifesto G36 JSON](gaviao-main-window-20261113-g36.json).

## Revisão científica e editorial

- **NASA C241-L21, P12 e Kepler/J2 (#429, #430, #434, #437, #439, #444):** a série impressa 527/529 94,6 e 92,6→92,2→91,6 minutos testa condicionalmente o modelo de *viés aditivo comum por edição*; a diferença entre gaps das edições 15/11 e 15/12 é [0,8;1,2] min sob impressão ±0,05 por célula. Essa prova Lean depende de premissas sobre as células; não estabelece tempos instrumentais, taxas observadas, RAAN do 528, posição terminal ou fontes independentes. Intervalos J2 propagam precisão de impressão, não erro físico. Os controles de #430 vinculam seis células de três edições, não seis sensores.
- **Meteorologia e geografia (#432, #440, #443):** registros IGRA em estações regionais e fronteira moderna não são perfis de vento sobre Conde em novembro de 1963. A comparação JPEG identifica uma imagem codificada republicada em dois sites, não duas fotografias independentes nem data/local original da exposição. O volume mensal DOE Bahia de dez/1953 teve identidade digital catalogada, mas Lei 628, suas páginas e data de publicação ainda não foram autenticadas no volume.
- **Código, SSG, interface e CI (#431, #436, #441, #442):** o arquivo reverso reúne reutilizações documentais sem convertê-las em testemunhos físicos; os rótulos de laboratório receberam traduções condicionais; a verificação de checkout SHA foi endurecida. No cut SHA da #439, os jobs `deploy` e `build` foram **CANCELLED**; não são sucessos nem evidência de falha científica. Demais checks foram registrados, não inferidos como verde a partir da data de merge.

## Achado G36-F1: colisão documental por host e basename

A correção G35 da #431 conferia data de captura, CDX e permalink, SHA e tamanho declarados, host e **último segmento** do caminho URL. Isso ainda permite substituir a rota histórica por outro caminho de mesmo host e mesmo nome do PDF, alterando `cdx_original_url` e `archived_url` juntos, ou acrescentar uma query que aponta para outro recurso. O resultado continua internamente consistente, embora não identifique a mesma obra arquivada. Esses mutantes são **sintéticos**: não há acusação de alteração do Wayback real.

**Correção:** para fontes NTRS modernas `/api/citations/{id}/downloads/{id}.pdf`, aceitar somente a rota histórica conhecida `/archive/nasa/casi.ntrs.nasa.gov/{id}.pdf`, sob o mesmo host; para outras fontes, exigir caminho integral igual ao de origem. Exigir também query igual, ausência de fragmento/credenciais e coerência de host e porta. Testes negativos independentes para rota alterada e query nova, com controle positivo do corpus. Teste red/green deve executar no CI do HEAD real da [PR #445](https://github.com/franklinbaldo/conde-incident/pull/445).

**Limites:** caminhos permitidos ainda são mapeamento documental versionado, não checagem HTTP viva; o hash declarado não substitui re-download e autenticação do PDF de 1963. Sem medições instrumentais datadas e calibradas, o problema terminal do NORAD 528 permanece **INDETERMINADO**. Nenhuma publicação no blog pessoal.

**Próximo checkpoint:** o corte seguinte começa depois de `070481978ae7493ecae19d82acfc144072f792bb` e deverá incluir #445 e os merges concorrentes, sem usar o SHA da PR como substituto do corte da auditoria.
