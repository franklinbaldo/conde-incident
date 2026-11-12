---
type: Guide
title: "CGEO-11 | Proveniência da malha retrospectiva 1960 segundo metodologia IBGE"
description: "Dependência declarada da malha de 1991, ausência de precisão cartográfica e contrato seguro para Castor"
---

# CGEO-11 | Uma malha nominal 1960 construída a partir de 1991

**Constatação diretamente verificável na fonte original do IBGE:** a *Apresentação* do documento oficial *Evolução da divisão territorial do Brasil 1872–2010: conteúdo digital*, **p. 1**, informa que os polígonos municipais históricos foram construídos por união de polígonos com base na malha de **1991** para representar a evolução das emancipações. Declara também que o produto **não apresenta precisão cartográfica**. Isso corrige a interpretação de CGEO-10: o polígono nominal 1960 de Conde é um **produto cartográfico retrospectivo**, não uma medição feita naquele ano.

Fonte oficial primária, PDF: [IBGE, apresentação do conteúdo digital](https://geoftp.ibge.gov.br/metodos_e_outros_documentos_de_referencia/outros_documentos_tecnicos/municipios_1872_1991_documentacao/Evolucao_da_divisao_territorial_do_Brasil_1872%20a%202010_apresentacao_do_conteudo_digital.pdf). Download direto em 12/11/2026; **15.484 bytes; SHA256 5886a4a481f51299818082beb5fb43d7deda60f4d2ad09a31eb598579d6e0fab**. Página 1 inspecionada visualmente. A afirmação sobre a origem na malha de 1991 aplica-se à **família do produto**, não identifica uma cadeia de cada vértice individual ou o método exato de transformação de datum.

Consequência auditável: CGEO-10 e a malha-base 1991 **não são duas observações cartográficas independentes de 1960**. O termo *sem precisão cartográfica* não fornece tolerância de 10, 100 ou 1.000 metros e **não** permite calcular erro estatístico. Não implica que todos os traçados estejam errados, mas retira qualquer justificativa para usá-los como fronteira mensurável e observada em 1963.

O [contrato JSON](ibge_1872_1991_methodology_2026-11-12.json) conecta CGEO-11 à família histórica IBGE, a malha-base 1991 à cartografia retrospectiva 1960 de Conde e esta ao limite legal latente de 1963, com a aresta **NOT_A_VALIDATED_TEMPORAL_OR_PRECISION_BRIDGE**. O [validador](../../tools/conde_ibge_lineage.py) confirma integridade da fonte e preserva nulos históricos. Reproduza:

    python3 tools/conde_ibge_lineage.py --date 1963-11-08
    python3 tools/conde_ibge_lineage.py --date 1963-11-08 --verify-pdf /tmp/apresentacao-ibge.pdf
    python3 -m unittest tests/test_conde_ibge_lineage.py -v

A verificação documental requer **o PDF real e SHA integral**; o CI offline testa o contrato e os invariantes, não substitui a aquisição. O Castor deve importar a geometria nativa de CGEO-10 apenas com etiqueta de **referência cartográfica retrospectiva sem precisão certificada**, jamais como observação de impacto, limite municipal legal de 1963, filtro de trajetória ou função de probabilidade geográfica. A documentação da lei de 1944/1953 e os atos posteriores seguem como dependências não resolvidas.

**Resultado negativo:** nenhum novo polígono de validade legal de 08/11/1963; nenhum datum/erro de uma campanha geodésica da época; nenhuma posição de reentrada inferida. Próximo teste discriminante: anexos originais dos atos de 1944/1953 e alterações até 1963, sob custódia documental da Lontra.
