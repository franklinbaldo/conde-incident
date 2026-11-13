---
type: Guide
title: "C197: modelo da precisão histórica da data de decaimento do NORAD 528"
description: "Separação rastreável entre precisão de radar, ajuste orbital, previsão e data publicada, sem criar erro temporal fictício."
---

# Registro de precisão do dia de decaimento 528

**Fonte documental:** C197#1 e C241-L11, NASA/Goddard, Satellite Situation Report, vol. 3 nº 22, 15/11/1963, [NTRS 19640001198](https://ntrs.nasa.gov/citations/19640001198), [PDF oficial](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), página impressa 8, índice PDF 9. Na tabela de adições de objetos decaídos consta "1963 3B", com "8 NOV 63". A identidade NORAD 528 depende da correspondência catalográfica C241-L10. SHA-256 da captura já auditada em C241-L11: 0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674. Esta nova fatia não revalida pixels nem afirma recuperação de fichas instrumentais originais.

**Resultado demonstrado:** houve publicação em 15/11/1963 de uma data catalográfica atribuída de 08/11/1963. São sete dias de calendário entre essas datas. Isso não mede o atraso interno da NASA/NORAD nem a precisão real de ocorrência do evento.

## Camadas distintas que não podem ser confundidas

- **Sensor do 528:** precisão em distância e ângulo de cada observação. Estação, instante e erro: desconhecidos.
- **Ajuste orbital do 528:** covariância dos elementos e época de referência observacional. Desconhecidos.
- **Previsão de decaimento:** método de arrasto, horizonte da previsão e erro real das previsões. Desconhecidos.
- **Catalogação:** dia civil escrito em documento contemporâneo, mas sem metadados de fuso, instante terminal, mecanismo de classificação, revisão ou erro temporal.

O dia civil é **resolução do campo impresso**, não sigma de uma observação nem demonstração de que ocorreu uma reentrada dentro de um intervalo UTC exato.

## Contraste histórico de capacidade

O [registro NORAD original de 14/11/1963](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/08.pdf), já catalogado como **MOR-NOR-20261112-03**, descreve uma janela reportada entre 22:10Z e 24:00Z do dia 12/11/1963 para o **SPADATS 688**. Demonstra capacidade histórica de relatar intervalos subdiários para *outro objeto*. Não autoriza atribuir ao 528 o mesmo intervalo, erro de duas horas, sistema de vigilância ou método. A janela reportada do 688 também não é estimativa estatística de erro.

O [modelo tipado](../constraints/nasa_528_decay_precision_C197_20261113.json) preserva a comparação sem transposição entre objetos, em conjunto com a [auditoria prévia de ausências](../statistics/raan_catalog_day_missingness_C241.json). A família de dados NASA/Goddard e NORAD pode compartilhar rastreamento: não multiplicar contagens como sensores independentes.

## Relações e restrições

Grafo: fonte C197#1 -> data catalogada -> processo de observação/classificação desconhecido -> instante real latente -> futuro simulador calibrado. A equação observacional candidata é uma função da data publicada condicionada ao instante real, cobertura da rede, ajuste orbital, erro de previsão, regra de classificação e latência administrativa. Sem esses insumos, não existe verossimilhança numérica justificada.

**Somente como premissa futura**, se houvesse prova de que o dia 08/11 representa exatamente o dia UTC do evento físico, teríamos 08/11/1963 00:00Z <= instante real < 09/11/1963 00:00Z. O PDF não documenta essa hipótese. O predicado permanece **inativo**.

O caso 528 recebe cinco arestas novas, mas **zero medições instrumentais adicionais, zero redução física demonstrada do domínio, zero probabilidade histórica e zero conclusão sobre hora ou local em Conde**. Estado CONNECTED_PENDING_CALIBRATION. Não transformar a ausência de linhas TLE entre outubro e novembro em prova de ausência de radar ou detecção negativa.

## Recuperações necessárias

Documentos NORAD/SPADATS de 07–09/11/1963 sobre o objeto 528, última estação e época UTC com quadro/erro, cálculo ou boletim de determinação de decaimento, registro de revisões, convenção histórica de dia/fuso e avaliação independente do erro de previsão de reentrada. A recuperação desse material permitiria decidir se uma restrição temporal poderia ser promovida a Lean 4.35.0.

## Verificação reproduzível

Executar no HEAD:

    python3 -m unittest discover -s tests -p test_nasa_528_decay_precision_audit.py -v
    python3 tools/nasa_528_decay_precision_audit.py --output /tmp/nasa-528-decay-precision.json

O auditor confronta diretamente o registro JSON com C241-L11, com o documento NORAD comparativo e com a auditoria de ausências. Os testes adversariais rejeitam a fabricação de precisão, horário pontual, probabilidades e transferência indevida do SPADATS 688.
