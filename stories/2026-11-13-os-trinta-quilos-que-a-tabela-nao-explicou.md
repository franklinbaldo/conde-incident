---
type: Story
title: "Os trinta quilos que a tabela não explicou"
description: "Uma diferença entre massa seca e massa catalogada da Agena não é prova de combustível perdido nem a massa do NORAD 528."
date: "2026-11-13"
summary: "Ao ler o manual de colunas do GCAT, os 1.176 kg deixaram de ser uma soma demonstrada dos três detritos."
chapter: "26"
author: "Coruja · Caderno de investigação"
status: "Catálogo secundário GCAT 1.8.9, seis arquivos com hashes na matriz C241-L40; fichas originais de engenharia e massa dos detritos não encontradas"
---

# Os trinta quilos que a tabela não explicou

Uma conta cabe na margem de um caderno: **306 + 870 = 1.176**. Uma segunda, igualmente correta, dá outro resultado: **306 + 900 = 1.206**. A diferença são trinta quilos. Seria a história de um combustível gasto? De uma peça desprendida do foguete? Nenhuma das duas. Por enquanto, é apenas a distância entre **duas leituras possíveis de uma tabela**.

A história começa em **16 de janeiro de 1963**, quando a missão militar **OPS 0180** partiu da Califórnia a bordo de um **Thor Agena B**. O [registro de lançamento no GCAT](https://planet4589.org/space/gcat/data/launch/Thor.html) lhe atribui a designação **1963-003** e imprime **1,176 tonelada** na coluna `OrbPay`. Em novembro daquele ano, o objeto **1963-003B / NORAD 528** apareceria na investigação de uma suposta queda em Conde, na Bahia. Não existe nesses números um registro de impacto no solo.

## Três números NORAD, mas não três pesagens

O [catálogo de objetos GCAT (`satcat`)](https://planet4589.org/space/gcat/data/cat/satcat.html) possui entradas para **527, 528 e 529**. A linha **S00527 / 1963-003A** imprime três valores diferentes: `Mass = 306 kg`, `DryMass = 306 kg` e `TotMass = 1176 kg`. Nas linhas **S00528 / 1963-003B** e **S00529 / 1963-003C**, os campos de massa apresentam **zero**.

Foi tentador somar ou repartir os 1.176 kg entre os três objetos. Mas o [manual de colunas de Jonathan McDowell](https://planet4589.org/space/gcat/web/cat/cols.html) altera completamente o sentido dessa operação: `Mass` designa a massa do objeto na inserção orbital, excluindo corpos anexados; `DryMass` é sua massa seca; `TotMass` registra a massa do conjunto **ainda ligado**, atribuída a uma das entradas, enquanto as outras podem trazer zero. **Zero de catálogo não é pesagem física de zero quilograma.**

Esse é o achado central da [auditoria documental C241-L40](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/evidence_matrix_C241-L40_2026-11-13.md), integrada ao projeto em **13 de novembro de 2026**. Ela permite dizer onde está escrito o número 1.176. Não permite dizer quanto pesava o detrito 528 depois de se separar.

## O estágio que muda a soma

Existe uma quarta entrada, agora no [catálogo auxiliar `auxcat`](https://planet4589.org/space/gcat/data/cat/auxcat.html): **A00324, Agena B 2313**. Para ela, o GCAT informa **900 kg** no campo `Mass` e **870 kg** no campo `DryMass`.

Somar a carga de 306 kg à massa *seca* do estágio resulta em **1.176 kg**. Somá-la à massa de 900 kg resulta em **1.206 kg**. Os **30 kg** não foram medidos neste exame como combustível consumido, material solto ou erro de instrumento. Tampouco sabemos, apenas com as entradas citadas, se todas as parcelas se referem à mesma configuração física e ao mesmo instante. A coincidência da primeira soma com `TotMass` exige reconciliação histórica, não um enredo sobre trinta quilos desaparecidos.

Há outra armadilha: no [registro Thor](https://planet4589.org/space/gcat/data/launch/Thor.html), **`OrbPay`** é o campo de carga útil orbital. A [documentação de lançamentos do GCAT](https://planet4589.org/space/gcat/web/launch/lcols.html) explica que seus valores são **gerados automaticamente** a partir de tabelas de cargas úteis e precisam de cautela. Não são a coluna de massa total em órbita (`OrbMass`), que o catálogo ainda não preencheu de modo geral. O [catálogo `psatcat`](https://planet4589.org/space/gcat/data/cat/psatcat.html) inclui a carga útil S00527, mas não fornece uma pesagem exclusiva de cada fragmento 528 e 529.

## O que sobreviveu da investigação

O GCAT é uma compilação científica de **Jonathan C. McDowell**, não uma ficha de engenharia produzida em janeiro de 1963. Sua versão **1.8.9**, consultada em novembro de **2026**, traz atualizações muito posteriores aos acontecimentos. A [matriz C241-L40](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/gcat_mass_semantics_C241-L40.json) conserva os endereços, tamanhos e **SHA-256 de seis arquivos completos**. Isso permite repetir a leitura e detectar futuras mudanças do catálogo. Seis arquivos da mesma família editorial, porém, **não são seis testemunhos independentes**.

A correção não elimina o [modelo exploratório de repartição de massa](https://github.com/franklinbaldo/conde-incident/pull/621). Ela impede que uma hipótese matemática seja promovida a fato antes que se saiba o que foi pesado, quando, em que configuração e com que incerteza. O mesmo vale para simulações de arrasto: sem massa individual, área e coeficiente aerodinâmico documentados, uma trajetória pode ser calculada condicionalmente, mas não demonstrada historicamente.

O documento decisivo seria uma **ficha original de massa e separação da missão OPS 0180**, discriminando carga útil, estágio Agena, propelente residual, partes liberadas, época e erro de cada número. Até que ela apareça, nenhum valor da tabela determina a massa do NORAD 528 na reentrada nem restringe seu ponto terminal.

Em Conde, continua faltando o objeto, a medição e a localização autenticada da alegada queda. A novidade desta investigação não foi encontrar trinta quilos: foi impedir que uma conta escrita hoje fosse confundida com algo observado em 1963.

---

**Fontes e limitações.** [GCAT 1.8.9, documentação de objetos](https://planet4589.org/space/gcat/web/cat/cols.html); [`satcat`](https://planet4589.org/space/gcat/data/cat/satcat.html); [`auxcat`](https://planet4589.org/space/gcat/data/cat/auxcat.html); [`psatcat`](https://planet4589.org/space/gcat/data/cat/psatcat.html); [lançamento Thor](https://planet4589.org/space/gcat/data/launch/Thor.html); [manual de lançamentos](https://planet4589.org/space/gcat/web/launch/lcols.html). Custódia, versões, dependências e hashes em [C241-L40 / PR #629](https://github.com/franklinbaldo/conde-incident/pull/629). **Nenhuma nova observação instrumental 528, massa de fragmento, restrição orbital ou prova física da alegada queda.**