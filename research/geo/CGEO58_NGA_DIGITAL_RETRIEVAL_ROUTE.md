---
type: Evidence
title: 'CGEO-58: rota NGA de digitalização histórica sem acesso presumido'
description: 'Fontes institucionais NGA e NARA verificadas: capacidade geral de digitalização não implica fotograma de Conde localizado.'
---

# CGEO-58 | Uma porta distinta para negativos históricos

**14/11/2026.** A [National Geospatial-Intelligence Agency (NGA)](https://www.nga.mil/resources/Historical_Maps_and_Charts.html) afirma oficialmente que mantém acordo para obter filmes negativos originais do NARA desde 1936 e que consegue fornecer **cópias digitalizadas de missões de fotografias aéreas e satelitais de 1935 a 2004**. Essa afirmação institucional é uma **rota de pesquisa potencial**, independente do impedimento de solicitar ao NARA reproduções remotas. **Não** confirma que a NGA detenha ou possa liberar o voo candidato sobre Conde, Bahia.

A [página oficial FOIA da NGA](https://www.nga.mil/resources/FOIA_Information.html) descreve como solicitar **registros existentes**, sujeitos a exceções legais. FOIA **não obriga por si** a criação de uma digitalização nova; tampouco comprova que o material particular esteja liberado, georreferenciado, localizado, gratuito ou pronto para download. Nenhuma consulta foi enviada.

| Fonte institucional | HTTP | Bytes coletados | SHA-256 |
|---|---:|---:|---|
| [NGA Historical Imagery](https://www.nga.mil/resources/Historical_Maps_and_Charts.html) | 200 | 27834 | `7f21f746057d7cebb2064946d051a4adde7f8263af8629cd8bacdb554a4a070d` |
| [NGA FOIA Information](https://www.nga.mil/resources/FOIA_Information.html) | 200 | 35581 | `71ee943bfaf0810792b1950308d6b7a76991b8001859e77e2bdd69ef476d72a7` |
| [NARA RG373 guide](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography) | 200 | 51079 | `326b33c82aaef86bfba3b4be2a201c311ad167a6a2a0785dcb366ed1ff836648` |

**Ligação à evidência anterior:** as folhas NARA [00247](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00247.jpg), [00248](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00248.jpg), [00431](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00431.jpg) e [00432](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00432.jpg) são índices preparados em outubro de 1956 com datas candidatas de setembro de 1942. O.P. FILE NO. `125370`/`125374` ainda não foi associado a número *spot*, exposição ou lata. **A NGA e o NARA não representam sensores independentes para a mesma fotografia.**

**Teste falsificável:** antes de qualquer contato institucional, procurar referência pública que ligue **O.P. + ORGN/SORTIE + exposição** a uma missão/registro digital da NGA, ou a seu índice de negativos. Se inexistente publicamente, preparar consulta técnica indicando NARA RG373, M1765 rolo 317, as quatro folhas, os dois números O.P. e a pergunta explícita sobre disponibilidade de **registros existentes**, sem pressupor digitalização nem solicitar trabalho não autorizado. Submeter somente com aprovação do proprietário. A 🦦 [Lontra #8](https://github.com/franklinbaldo/lontra/issues/8) mantém a trilha spot→lata do NARA.

**Reprodução:** `python3 tools/cgeo58_nga_digitization.py` verifica contrato e limites, `python3 -m unittest discover -s tests -p 'test_cgeo58_nga_digitization.py' -v` testa mutantes, `--live` readquire os três HTML oficiais, conferindo bytes e SHA-256. HTML é dinâmico e eventual mudança futura deve gerar investigação, não suposta fraude.

**Limite científico:** foram adquiridas três páginas institucionais, **zero** fotogramas e **zero** geometrias históricas de Conde. O núcleo urbano de novembro de 1963 e a alegada localização da queda continuam não determinados; nenhuma restrição orbital nova foi ativada.

