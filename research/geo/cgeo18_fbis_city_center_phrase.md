---
type: Guide
title: "CGEO-18: o que o FBIS realmente chamou de centro da cidade"
description: "Custódia literal de expressão espacial em versão inglesa de uma transmissão da Rádio Tupi de 8/11/1963 e veto de geocodificação não sustentada"
---

# CGEO-18 — Centro da cidade é expressão, não coordenada

A pergunta geográfica surgida após [CGEO-17](cgeo17_1958_urban_toponym_crosswalk.md) agora possui um documento verbal diretamente inspecionado: o [fac-símile FBIS, folha única](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf). A reprodução digital disponível vem de **ondisclosure.org**, não diretamente do arquivo custodiador original. O documento visível traz carimbo de desclassificação e o identificador **NND 968063**; não verificamos a cadeia arquivística anterior à cópia digital.

**Aquisição binária em 13/11/2026:** 126.624 bytes; SHA-256 `63654bcd90c0515f30e31ed511a12a05f170ff4470e3d8a6f40fca12012a1adb`. A página única foi inspecionada visualmente. Não se infere daí autenticidade de áudio original, velocidade do objeto, cratera real ou identidade da pessoa mencionada.

## As duas expressões distintas do fac-símile

O cabeçalho impresso é `RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 2330 8 NOV 63 W`. O texto FBIS, **em inglês**, situa a fonte dos relatos com `REPORTS FROM THE MUNICIPALITY OF CONDE` e emprega `FELL IN THE CENTER OF THE CITY`. O rodapé impresso diz `9 NOV 111A RWS/GY`.

A distinção é essencial: a transmissão atribuída à Tupi era *em português*, mas a cópia acessível oferece **uma versão em inglês do FBIS**, não a gravação ou a transcrição literal em português. Portanto, ainda não está verificado que alguém pronunciou exatamente a expressão portuguesa “centro da cidade”, nem que nomeou praça, rua, coordenada ou testemunha ocular.

O campo `2330` pertence à **identificação da transmissão**, sem fuso confirmado nesta custódia; **não é o horário da suposta queda**. A linha de 9 de novembro pode ser processamento do boletim, mas seu significado não foi estabelecido e não se usa como hora física do evento.

## Consequência espacial

“Center of the city” é **descrição informal transmitida em relato indireto**; não equivale ao centróide geométrico da malha municipal do IBGE, nem prova que a Praça Severiano Lima do [álbum IBGE 1958](ibge_1958_conde_photo_custody.json) fosse o local referido. Cidade, município, sede administrativa, Vila do Conde histórica e Sítio do Conde não podem ser permutados por uma tradução.

O [contrato JSON CGEO-18](cgeo18_fbis_city_center_phrase.json) registra a dependência da mesma linha Tupi/FBIS de **C01**, a ligação contextual ao CGEO-17 e os campos geográficos explicitamente nulos. Nenhum novo testemunho independente foi criado. A frase é evidência da **circulação da afirmação**, não da ocorrência alegada. O fluxo da simulação recebe `can_constrain_orbital_reentry=false`.

Reprodução: `python3 -m tools.cgeo18_fbis_city_center` valida o registro offline; `python3 -m tools.cgeo18_fbis_city_center --verify-pdf /caminho/para/pdf` compara, **se presentes**, os bytes verdadeiros com o SHA congelado. `python3 -m unittest tests.test_cgeo18_fbis_city_center -v` executa contraprovas de tentativas de introduzir localização, hora, língua original ou evidência independente.

**Próximo teste discriminante:** localizar a gravação/transcrição portuguesa original ou jornal brasileiro contemporâneo que permita conferir a formulação da localização; depois procurar planta urbana/aerofoto de 1950–1963 e atos de nomeação de praças. Sem essas pontes, o “centro” permanece um topônimo narrativo, não uma região medida.
