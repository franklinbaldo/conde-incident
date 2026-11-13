---
type: Guide
title: "C241-L30: vinculação condicional das séries soviéticas de 1963 aos NORAD 527, 528 e 529"
description: "Catálogos da Ucrânia e CiNii confirmam acervos bibliográficos, não observações orbitais; matriz de identificação conserva seis cruzamentos pendentes."
---

# C241-L30: antes de associar um boletim soviético ao 528

**Problema:** a [issue pessoal 🐢 #4](https://github.com/franklinbaldo/tartaruga/issues/4) solicita correspondência independente, por fonte e página, entre eventuais registros soviéticos de 1963 e os objetos norte-americanos **527/528/529**. Uma coincidência de nome não resolve identidade, época, referencial nem independência instrumental.

## Fontes, graus e disponibilidade

A 🦦 Lontra já havia localizado duas séries na [PR #548](https://github.com/franklinbaldo/conde-incident/pull/548), com integridade dos **catálogos HTML** (C241-L29). Não repetir sua pesquisa como nova observação.

- [Biblioteca do Observatório Astronômico Principal, Kyiv: publicações científicas](https://mao.kiev.ua/index.php/ua/gao-biblio-periodyka/specissues). **Бюллетень станции оптического наблюдения ИСЗ**, números **32–37 (1963)**. Ocorrência C241-L29#1.
- [Mesma biblioteca, seção N](https://mao.kiev.ua/index.php/ua/gao-biblio-periodyka/sciencefilds-n). **Наблюдения ИСЗ**, número **2 (1963)**. Ocorrência C241-L29#2.
- [CiNii AA00566856](https://ci.nii.ac.jp/ncid/AA00566856) identifica **Бюллетень Станции оптического наблюдения искусственных спутников Земли**, associado ao Conselho Astronômico da Academia de Ciências da URSS; a ficha registra, por exemplo, acervo de Kyoto **1963–1971, números 32–59**. Captura HTML de 13/11/2026, HTTP 200, **54.342 bytes**, SHA-256 **da7b7e445ccaf5569bccbb42809f9da471318cebebe6d713ec0deb0a08c31034**. É uma confirmação **bibliográfica complementar**, ainda não prova de que as duas bibliotecas guardam a mesma edição, nem uma segunda observação de satélite.
- [CiNii AA00826990](https://ci.nii.ac.jp/ncid/AA00826990) localiza o título distinto **Результаты наблюдений американских искусственных спутников Земли**. A lista visível de acervos japoneses cobre **1961–1962**; **não** mostra fascículos de 1963 nesta visualização. Isso **não** prova ausência da série em outros acervos. Captura HTML de 13/11/2026, HTTP 200, **53.364 bytes**, SHA-256 **0f349be2b3655f29ba1f8a518143ee807d58ba970b507629a5ed1fcf39c8740b**.

Somente os HTML bibliográficos foram descarregados e confrontados byte a byte duas vezes. Os hashes são de **páginas de catálogo**, não dos fascículos soviéticos. Não foi contatada nenhuma biblioteca, pessoa ou pesquisador. **Zero imagens originais de páginas, zero medições soviéticas de 527/528/529.**

## Identidade, não aritmética de rótulos

[C241-L28, PR #533](https://github.com/franklinbaldo/conde-incident/pull/533) estabeleceu em quatro boletins NASA posteriores o vínculo documental primário **1963 03A ↔ NORAD 527**. Para **03B ↔ 528** e **03C ↔ 529**, os números ainda dependem de catálogo moderno secundário. O boletim NASA de 15/11/1963 menciona **1963 3B**, com data de decaimento de **8/11**, mas **não imprime nesse registro o número 528**, nem mostra o instante terminal.

O [JSON de vinculação C241-L30](soviet_1963_cross_id_C241-L30.json) cria **seis pares candidatos**: duas séries de 1963 vezes três objetos. Todos permanecem **PENDING_NO_ISSUE_FACSIMILE**. Para cada par, campos de designação soviética impressa, página, SHA do fascículo, época, estação, tipo de observação, quadro, escala temporal, unidade, erro instrumental e genealogia do ajuste são `null`, nunca inventados. A associação entre títulos semelhantes permanece possível, não confirmada.

A identificação documental futura exigirá **página original + bytes íntegros + designador efetivamente impresso + explicação do vínculo com o catálogo ocidental**. Ativar uma **restrição física** exige mais: horário instrumental, estação/sensor, observação versus órbita calculada, quadro, erro e testes de independência. Uma tabela soviética de elementos ajustados pode utilizar dados de outras redes e não constitui automaticamente um novo sensor.

A observação do catálogo **não reduz agora** o domínio dos parâmetros orbitais. Não permite corrigir o conflito RAAN 284,1520°/198,5261°, fixar passagem em Conde, inferir data terminal por radar ou estimar `σ` a partir da impressão decimal.

## Reprodução, próxima verificação

```bash
python3 -m unittest discover -s tests -p test_soviet_1963_cross_id.py -v
python3 tools/audit_soviet_1963_cross_id.py
# Após baixar exatamente os dois HTML:
python3 tools/audit_soviet_1963_cross_id.py --cinii-dir /diretorio/dos-html
```

O CI baixa os dois HTML públicos e verifica os hashes pinados, lê C241-L29, C241-L28 e o catálogo secundário; **20 testes adversariais** rejeitam horário, precisão, medição, equivalência de séries e confirmação automática falsos.

**Próximo teste material:** recuperar fac-símile dos números soviéticos **32–37/1963** ou **2/1963**, inspecionar índice e linhas de identificação com datas anteriores/posteriores a **8/11/1963**, solicitar a 🦦 Lontra a página como handoff de custódia; não escrever a acervo sem autorização.