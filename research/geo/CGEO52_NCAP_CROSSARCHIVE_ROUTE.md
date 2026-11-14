---
type: Evidence
title: 'CGEO-52: parceria NARA–NCAP como rota digital condicional para fotografias históricas'
description: 'Separar existência da parceria, cobertura publicada, acesso HTTP e localização comprovada de fotogramas de Conde.'
---

# CGEO-52 | Rota digital NARA–NCAP, ainda sem fotograma de Conde

**14/11/2026.** Após [CGEO-51](CGEO51_NARA_COPY_ACCESS.md), que documentou a necessidade de visita ou representante para negativos físicos, examinei uma possível saída digital **já existente**, sem contato institucional: a parceria do National Archives (NARA) com a National Collection of Aerial Photography (NCAP).

O [guia primário do NARA para fotografia aérea estrangeira RG 373](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography), revisado em 18/02/2025, declara que fotografias digitalizadas pela NCAP estão sendo acrescentadas ao catálogo do NARA e que é possível procurar por *spot number* ou quadrícula. A [página oficial da coleção NARA na NCAP](https://www.ncap.org/image-collection/nara) descreve a parceria iniciada em 2016 e um projeto de digitalização progressivo. Sua relação **publicada** de cobertura geográfica inclui Argentina, mas não Brasil. Isso **não prova ausência** de negativos brasileiros nos acervos, nem prova que o catálogo da NCAP seja completo ou atualizado para esta célula.

## Aquisições e falhas diferenciadas

- **Guia NARA integral:** HTTP 200, 51.079 bytes, SHA-256 `326b33c82aaef86bfba3b4be2a201c311ad167a6a2a0785dcb366ed1ff836648` em 14/11/2026. Reaquisição viva deve conferir marcadores de conteúdo, **não hash imutável de HTML mutável**.
- **Catálogo NCAP:** requisição direta do Jatobá obteve HTTP 403 e 5.432 bytes de página de bloqueio. O conteúdo da coleção foi consultado em visualização web separada, sem custódia dos bytes da página original; não se converte 403 em inexistência da fonte.
- **Busca NARA 11S037W:** a tentativa de recuperar JSON por `/proxy/records/search` recebeu HTTP 200, 5.454 bytes, porém **HTML de aplicação**, e não resposta JSON de busca. Por isso **nenhuma contagem de hits ou ausência de fotografias foi inferida**.

São etapas de acesso/catálogo para uma **mesma família de negativos NARA**, não observações fotográficas independentes. A busca continua ancorada em RG 373 / série 306062 / unidade 46716637 / 11S037W / índice 00248, com `O.P. FILE NO. 125374` e etiquetas candidatas 26/16. Nenhum *spot*, lata, fotograma original, data individual de exposição ou geometria urbana de 1963 foi recuperado.

## Próximo teste verificável

Tentar o mapa [NCAP Air Photo Finder](https://airphotofinder.ncap.org/) ou a interface de registros do NARA, mantendo a consulta da quadrícula e dos números provisórios como **candidatos**. Qualquer resultado positivo precisa trazer ID do fotograma, cobertura espacial, exposição, data e identidade dos bytes antes de entrar no grafo; o caminho presencial de CGEO-51 continua válido. Nenhum contato externo foi enviado.

**Resultado:** nova rota técnica **condicional**, sem prova de cobertura brasileira publicada para este caso, sem reconstituição da praça central de novembro de 1963 e **sem nova restrição orbital**. Contrato: [JSON](cgeo52_ncap_crossarchive_route.json).
