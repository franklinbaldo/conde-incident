---
type: Guide
title: "C241-L33: registro original ONU 1963-3B em janeiro e retirada em novembro"
description: "Quatro documentos ONU com hashes e páginas inspecionadas, sem sensor independente do NORAD 528."
---

# C241-L33: 1963-3B no registro enviado pelos Estados Unidos à ONU

**Quatro fac-símiles completos:** ONU Assembleia Geral, documentos A/AC.105/INF.30, .53, .54 e .55, de 1963. PDFs oficiais UNOOSA baixados em 13/11/2026; ambas as páginas de cada edição examinadas visualmente. URL, bytes, SHA-256, data da publicação, data da carta e corte de atualização constam do [ledger](un_1963_registration_C241-L33.json). A imagem, não OCR, é a evidência da leitura.

## Registro inicial de três objetos em janeiro

[INF.30 (13/03/1963)](https://www.unoosa.org/documents/pdf/inf030E.pdf), carta dos EUA de 12/03/1963, página 2: suplemento de registros atualizado até **2400Z 31/01/1963**. A tabela contém 1963-3-A, 1963-3-B e 1963-3-C, lançados em 16 JAN 63 pelo **THOR AGENA**. Na ordem A/B/C, categorias **A/D/D**; períodos nodais **94,7 / 94,5 / 94,7 min**; inclinações **81,97° / 81,97° / 81,97°**; apogeus **518,6 / 505,5 / 525,5 km**; perigeus **479,5 / 476,4 / 476,4 km**.

É um **registro contemporâneo governamental de parâmetros catalogados**, não três TLEs primários nem observações independentes de radar. A tabela não imprime NORAD 527/528/529: as correspondências A/B/C vêm do documento NASA institucional retrospectivo **C241-L32** de 1977 (NTRS 19780009188, página -43-). Casas decimais não definem sigma físico.

## Estado reportado em 15 de novembro

[INF.53 (31/12/1963)](https://www.unoosa.org/documents/pdf/inf053E.pdf), carta de 20/12/1963, página 2: relatório de registro atualizado até **2400Z 15/11/1963**. Afirma explicitamente que **1963-3B e 1963-35A já não estavam em órbita** naquele corte administrativo. Não registra detecção negativa nesse instante nem informa método, sensor, previsão, hora de reentrada ou erro.

O [NASA Satellite Situation Report 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) **C197#1/C241-L11** informa dia de decaimento catalogado **8 NOV 63** para 1963 3B. A fonte ONU confirma **publicação governamental da mudança de status**, compatível com o dia NASA, sem se tornar segunda medição instrumental independente. Não confundir datas de corte (**15/11**), carta (**20/12**) e circulação (**31/12**). NASA, NORAD e registro enviado pelos EUA à ONU podem compartilhar o mesmo rastreamento.

## Controles de inclusão incremental

[INF.54](https://www.unoosa.org/documents/pdf/inf054E.pdf): corte 2400Z **31/10/1963**, adições e retiradas; menciona 1962 Omega 1 como não mais em órbita. [INF.55](https://www.unoosa.org/documents/pdf/inf055E.pdf): corte 2400Z **15/10/1963**, retirada de 1963-37A. Ambos publicados em 31/12/1963, cartas de 20/12/1963. Não imprimir 1963-3B nestes suplementos **não demonstra** ausência de observação, rastreio contínuo ou dia físico exato, pois são listas de mudanças e não censos instrumentais completos.

O vínculo 31/01 → 15/11 é documental. Transformá-lo em limite físico exigiria supor regras e exatidão de classificação não demonstradas; o predicado físico permanece **inativo**. O relatório ONU tampouco converte 8/11 em observação de reentrada ou local de queda.

**Status:** quatro originais pinados, três linhas documentais de janeiro, um relato de ausência de órbita em novembro, seis novas arestas, zero sensor original do 528, zero nova restrição física ou prova Lean ativada e nenhuma conclusão sobre hora/local em Conde.

## Reproduzir

    python3 -m unittest discover -s tests -p test_tle_un_1963_registration_audit.py -v
    python3 tools/tle_un_1963_registration_audit.py --pdf-dir /tmp/unoosa-1963 --output /tmp/c241-l33.json

O CI baixa os PDFs reais da UNOOSA, exige hashes SHA256/bytes, renderiza a página 2 dos quatro documentos e executa os testes adversariais sem ajustar os fatos às expectativas. Hash fixa o conteúdo recuperado, não a autenticidade de sensores.

**Próximo insumo:** encontrar a ficha NORAD/SPADATS de identificação, última estação/hora UTC e covariância do objeto S00528 e o procedimento de atribuição da data 8/11. Sem esses dados, a precisão temporal permanece desconhecida.
