---
type: Guide
title: "C241-LONTRA-R35: memórias de negativos AFU em Zvenigorod"
description: "Rota de custódia fotográfica em testemunho retrospectivo: catálogo de negativos AFU em 2007 não demonstra imagens ou órbitas de 1963."
---

# C241-LONTRA-R35 · Negativos fotográficos mencionados em Zvenigorod

**Fonte consultada em 13/11/2026:** [«Мемуары несостоявшегося астронома», portal SAI/MSU](https://www.sai.msu.ru/EAAS/rus/doc/MEM-12.htm). O autor relata ter entrado na pós-graduação do Astrosovet em 1963 e, **a partir de maio de 2007**, ter ajudado a criar um **catálogo eletrônico dos negativos de câmeras AFU conservados na observatória de Zvenigorod**, para a *International Virtual Observatory*. Em outro trecho, menciona catalogar imagens AFU-75 obtidas em estações diferentes. O testemunho é memorialístico, não um inventário arquivístico autenticado.

**Custódia técnica dos bytes de 2026:** resposta HTTPS HTTP 200, validação TLS pelo executor, **613.158 bytes**, SHA-256 \`3eef0389a2c752cf52803965a4e4a13e2ea12699b7f2129fbe98f6aa841a057d\`. O cabeçalho HTTP informa \`charset=koi8-r\`, enquanto o HTML inclui metadado conflitante \`windows-1251\`: o texto russo foi inspecionado por decodificação KOI8-R, não por confiança cega no metadado interno. Esta impressão digital refere-se **à página contemporânea**, não a um negativo histórico.

**Separação temporal:** a formação de 1963, a atividade catalográfica de 2007 e a data de cada negativo são informações diferentes. O texto não identifica um negativo obtido em 7–9/11/1963. AFU/AFU-75 **não pode ser atribuída retroativamente** a uma estação/câmera de 1963 sem documentação instrumental. O catálogo de 2007 não comprova a sobrevivência, localização ou acessibilidade desses negativos em 2026.

**Rota de investigação, ainda não executada:** localizar o catálogo da Virtual Observatory, números de chapa/dataset e registros de transferência da observatória Zvenigorod; verificar datas **de tomada da fotografia**, códigos de estação, identificação do objeto, época/fuso, referencial, medidas astrométricas e instrumentos. Antes de propor ajuste orbital, 🐢 Tartaruga precisa verificar correspondência explícita com 1963-003A/B/C (NORAD 527/528/529), distinguindo originais e derivações. Nenhuma instituição foi contatada.

**Estado epistêmico:** \`VERIFIED_MEMOIR_BYTES_ARCHIVE_REFERENCE_NOT_ORIGINAL_1963_OBSERVATION\`. Atesta somente a recuperação fiel dos bytes de um relato retrospectivo e uma pista arquivística de 2007, **não** custódia em 2026, medição independente ou presença dos três objetos. Novos observáveis orbitais **0**; novas restrições ativas **0**. Relacionado à [investigação soviética #545](https://github.com/franklinbaldo/conde-incident/issues/545), à rota de Yeniseisk [#631](https://github.com/franklinbaldo/conde-incident/pull/631) (outra estação, sem pressupor dependência instrumental) e à matriz acumulativa.

**Reprodução:** \`python3 -m unittest discover -s tests -p 'test_zvenigorod_afu_memoir_route.py' -v\`. Com HTML original disponível localmente: \`python3 tools/verify_zvenigorod_afu_memoir_route.py --html caminho.html\`. O HTML de 613 KB não foi colocado no Git.

