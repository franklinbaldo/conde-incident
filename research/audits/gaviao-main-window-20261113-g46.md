---
type: Guide
title: 'G46: contas documentais requerem transcrições autenticadas'
description: Auditoria de 12 integrações, duas contraprovas de mutação coordenada e reparo pela validação cruzada dos livros ONU/NASA.
---

# 🦅 G46: coerência aritmética não basta para custódia

## Janela e extensão

Conde `main` depois de `23b69249fddb897945f611d47247a8d6428fe2a7` até `00e2226de5c7889c992e3164d9616f8c6354ab2b` inclusive: **12 integrações first-parent**, **23 commits no DAG**, três merges convencionais. [Manifesto G46](gaviao-main-window-20261113-g46.json) apresenta SHAs, pais, arquivos e PRs. O estado de CI histórico por integração não foi consultado: `NOT_CHECKED`, não PASS presumido. A janela abrange C241-L36/#592, integrações UN e NASA, nova matemática P30, modelo orbital condicional G45, interface e novo caderno editorial. Auditados detalhadamente os valores derivados de C241-L36.

## G46-F1: transcrição e diferença poderiam mudar juntas

O validador `tools/tle_un_nasa_crosscutoff_audit.py` comparava quatro diferenças impressas de três objetos entre dois livros JSON. Se uma célula fosse modificada **em conjunto** com seu delta documental, a igualdade permanecia verdadeira mesmo com o SHA-256 declarado do PDF original inalterado. A contraprova sintética no 528 alterou o perigeu ONU de `476.4` para `477.4` km e a diferença publicada de `-41.4` para `-42.4` km. Outra alterou o período NASA de `94.1` para `94.2` min e a diferença de `-0.4` para `-0.3` min. **Ambos os pares foram aceitos antes do reparo**; os dois testes adversariais falharam corretamente em vermelho.

**Reparo:** o consumidor C241-L36 agora executa `tle_un_1963_registration_audit.validate` (C241-L33, impressão ONU ancorada na fonte) e `tle_nasa_ssr_apr_oct_audit.validate` (C241-L16, impressão NASA ancorada na fonte) **antes** da comparação nominal. Não se cria nova tabela paralela de células nem se modifica PDF ou fonte histórica. Os dois testes negativos passaram após a correção; todos os testes focados existentes permaneceram verdes. Execução como módulo e execução direta do script devem permanecer possíveis.

## Escopo epistemológico

Os mutantes são **SINTÉTICOS**; não foi constatada adulteração dos registros reais. Validadores com valores impressos pinados verificam a **consistência contra transcrições aprovadas**, mas não equivalem a reinspeção visual de cada fac-símile nesta sessão. Os relatórios ONU e NASA podem depender da mesma cadeia estadunidense; diferenças nominais entre publicações não demonstram velocidades, época de medição, trajetória ou observação de sensor independente. As 12 arestas continuam **documentais e inativas**. Não há redução de domínio de queda nem hora/coordenada terminal do NORAD 528.

## Integração

Submeter a correção em PR, exigir checks do HEAD exato e novamente da `main` após merge. Nenhum sucesso de CI futuro deve ser antecipado. A próxima revisão G47 começa depois de `00e2226` e inclui a presente correção e demais integrações posteriores.
