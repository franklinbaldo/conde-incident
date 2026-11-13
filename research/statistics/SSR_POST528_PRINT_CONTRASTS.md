---
type: Guide
title: '🦌 Cervo: contrastes documentais NASA SSR posteriores à data catalogada do 528'
description: 'Auditoria de diferenças exatas entre oito relatórios contemporâneos, preservando a ausência de calibração orbital.'
---

# Contrastes documentais da série NASA SSR 1963, objetos 527/528/529

## Pergunta discriminante

As tabelas contemporâneas da NASA/Goddard, já reunidas na custódia documental C241-L12/L16/L17/L18/L19, permitem **separar mudanças impressas nos controles 527 e 529** sem lhes atribuir épocas instrumentais? Sim, apenas no espaço de **valores compilados publicados**, e sob uma hipótese explícita de arredondamento decimal. Não provam por si mesmas trajetórias, velocidades de decaimento, forças compartilhadas ou a reentrada do 528.

O script tools/ssr_post528_print_contrasts.py carrega os oito relatórios de 30/04, 31/07, 15/08, 15/10, 15/11, 30/11, 15/12 e 31/12/1963, com os SHA-256 dos PDFs já catalogados, identifica linhas pela designação internacional e **não inventa linhas para o 528** em novembro/dezembro. São 20 células de período impressas no conjunto (três objetos em quatro edições, dois objetos nas quatro seguintes). Todos os documentos pertencem à família de compilação NASA/Goddard potencialmente dependente da mesma rede NORAD, sem comprovar sensores independentes entre edições.

## Resultado reproduzível

| Designação | 15 out. | 15 nov. | 30 nov. | 15 dez. | 31 dez. |
|---|---:|---:|---:|---:|---:|
| 1963-003A (527) | 94,6 | 94,6 | 94,6 | 94,6 | 94,6 |
| 1963-003B (528) | 92,4 | Não consta | Não consta | Não consta | Não consta |
| 1963-003C (529) | 93,3 | 92,6 | 92,2 | 91,6 | 89,2 |

Unidade: minuto de **período nodal impresso**. A célula de dezembro para 3C é **89,2**, após retificação documental C241-L18/C227, não 89,6. A ausência da linha 3B na tabela orbital posterior à data catalogada de 08/11/1963 não é um relatório de não detecção de radar, muito menos uma hora ou posição terminal.

Se, apenas para uma análise de sensibilidade documental, cada número impresso com uma casa decimal for resultado de **arredondamento ao décimo mais próximo**, cada valor de origem está em centro ± 0,05 minuto. Logo, uma diferença entre **duas células** tem margem de até ± 0,10 minuto. A diferença entre as **mudanças de dois objetos**, com quatro células distintas, tem margem de até ± 0,20 minuto:

\[
D_{C,A}(t_1,t_2) =
(P_{C,t_1}-P_{C,t_2})-(P_{A,t_1}-P_{A,t_2}).
\]

Entre os relatórios de 15/10 e 31/12, o contraste documental 3C versus 3A é **4,1 minutos**, com intervalo condicional **[3,9; 4,3] minutos** somente para arredondamento. Os quatro intervalos adjacentes de 3C têm quedas impressas de 0,7, 0,4, 0,6 e 2,4 minutos, com bandas [0,6;0,8], [0,3;0,5], [0,5;0,7] e [2,3;2,5]. A nova edição de 15/12 (C241-L21; NASA NTRS 19640003479, SHA-256 d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f, página PDF 7) divide o antigo intervalo entre relatórios de 30/11 e 31/12, **sem criar uma época instrumental**. Para 3A, cada contraste adjacente é 0,0, banda [−0,1;0,1], sem sinal definido. A soma das bandas adjacentes não deve tratar células compartilhadas como independentes; o programa recalcula o contraste outubro-dezembro **diretamente dos quatro extremos**.

Esses limites não são intervalos de confiança, incerteza do sensor, erro de efeméride nem limite sobre o valor orbital real. Mesmo a suposição de arredondamento, em lugar de truncamento ou outro processamento editorial, não foi confirmada. Os relatórios podem incorporar épocas instrumentais distintas ou propagação interna não documentada.

## Como usar sem contaminar a inferência

O resultado é uma **fatia de discriminação entre alegações documentais**, útil para verificar transcrição, controle de identidade e possível divergência entre um futuro modelo físico e dados compilados. A tabela de dezembro já foi examinada, portanto qualquer previsão agora confrontada com ela é retrospectiva, não um holdout cego. Não usar a diferença entre datas de publicação como denominador de taxa física. Não introduzir o valor ausente do 528 como zero, queda observada ou censura de sensor sem política de detecção.

A próxima passagem à inferência precisaria de registros instrumentais próprios com época UTC, referencial, operador de medição, erro/covariância, genealogia e modelo de seleção. Os controles 527 e 529 poderiam testar a parcela **compartilhada** de um operador físico do Castor; não identificam automaticamente parâmetros específicos do 528. Sem tais entradas, a redução da região admissível, a verossimilhança de não detecção, o MCMC histórico e a exclusão geográfica continuam **NOT_RUN / NOT_AUTHORIZED**.

Reprodução independente do backend e sem rede:

    python3 tools/ssr_post528_print_contrasts.py --check
    python3 -m unittest discover -s tests -p 'test_ssr_post528_print_contrasts.py' -v

O JSON adjacente é derivado somente dos livros documentais custodiados, verificados por referências, hashes e designações. Testes adversariais rejeitam deriva de hash, edição de data, linhas 528 inventadas, duplicação, precisão decimal adulterada e reversão da errata 89,2.
