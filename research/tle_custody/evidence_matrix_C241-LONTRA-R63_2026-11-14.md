---
type: Guide
title: "C241-R63: o KFT de Kyiv de 1965 não observou satélites em 1963"
description: "Cronologia instrumental retrospectiva, arquivos do Museu de Kyiv e proibição de retroprojeção para NORAD 527–529."
---

# C241-LONTRA-R63: estação ≠ instrumento em uma época

O [artigo de L. V. Kazantseva e S. L. Salata](https://viv.nuou.org.ua/article/view/229864), *Воєнно-історичний вісник*, **38(4), 2020, pp. 254–272**, DOI **10.33099/2707-1383-2020-38-4-254-272**, descreve os instrumentos da estação soviética de observação de satélites **1023**, em Kyiv. Na [página impressa 263, PDF folha 10](https://viv.nuou.org.ua/article/download/229864/228719/523958#page=10), há uma distinção verificável: a estação começou a operar em 1957, mas o **KFT-10/20 chegou de Moscou somente em 1965**, foi preparado para operação em **1966** e recebeu modificações de sincronização em **1969**. Na p. 265 aparecem atrasos instrumentais medidos em **1976**: cronógrafo 0,029 s e obturador 0,004 s.

**Regra temporal:** a existência de uma estação em 1963 não prova que ela utilizou um instrumento incorporado em 1965. Os atrasos de 1976 jamais podem fundamentar uma incerteza de astrometria de 1963, nem podem ser importados como se fossem calibração dos objetos 527, 528 e 529. A estação pode ter realizado observações fotográficas com outros aparelhos antes do KFT; esse fato precisa de fontes instrumentais e registros efetivos, não de suposições.

O trabalho cita duas cotas do **Arquivo do Museu do Observatório Astronômico de Kyiv (МКАО), fundo «Астрономічна обсерваторія»**, para instruções de operação: **ССШСЗ-04-18-01, folhas 1–7** e **ССШСЗ-04-18-02, folhas 1–12**, na página impressa 265. São **localizadores de documentos internos**, não documentos recuperados, e parecem tratar do método KFT posterior. Para 1963, o alvo mais útil são cadernos, filmes, efemérides e instrumentação **anteriores a 1965** da estação 1023. Nenhuma instituição foi contatada.

**Custódia e limites:** página 263 do PDF lida visualmente em 14/11/2026 via visualizador web; tentativas de recuperar os bytes integrais no executor Ifro falharam com HTTP 403/timeout. **Sem hash, tamanho ou certificação de PDF integral**; estes valores permanecem nulos no manifesto. O artigo é retrospectivo (2020), não registro observacional primário de 1963. Não há identificação de observações dos NORAD 527/528/529, nem restrições orbitais novas.

Executar `python3 -m tools.audit_kyiv_kft_r63` e `python3 -m unittest discover -s tests -p test_kyiv_kft_r63.py -v`; versões normais e otimizadas, testes negativos e `prek run --all-files` precisam de executor externo autorizado e CI em HEAD exato. Relacionado a [Conde #545](https://github.com/franklinbaldo/conde-incident/issues/545) e [Cafezinho #9](https://github.com/franklinbaldo/cafezinho/issues/9).
