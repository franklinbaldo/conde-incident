---
type: Guide
title: "C241-L49: fonte secundária FTV 2313 e geometria condicional"
description: "Distingue metadados do NORAD 527 de medições e calcula sensibilidade contrafactual da área projetada."
---

# C241-L49: rótulos de massa, objeto, época e atitude

A [página FTV 2313 da GMspazio](https://findyourobject.gmspazio.com/en/en/obj/14/699/ftv-2313.aspx), consultada por texto indexado em 14/11/2026, descreve **NORAD 527 / COSPAR 1963-003A**, lista **Mass (kg): 1176**, diâmetro **1,5 m**, altura **7,99 m** e forma **Cyl + Irr**. A mesma página conta que a missão 7153 encerrou operações após dois dias por falha de bateria e contém um rótulo **Lifetime: 6–10 days**. Não afirmamos que ambos representem o mesmo relógio físico. A tentativa direta de recuperar bytes da página falhou por certificado TLS; portanto, não há hash binário nem versão histórica validada. O [registro](../tle_custody/ftv2313_gmspazio_secondary_C241.json) preserva explicitamente esse limite.

O valor **1176 kg** coincide com o **TotMass** do objeto S00527 no [GCAT C241-L40](../tle_custody/gcat_mass_semantics_C241-L40.json). A fonte GMspazio usa apenas o rótulo **Mass**, sem demonstrar equivalência de campo, mesma época, inventário físico ou independência dos dados de origem. Essa coincidência não cria uma segunda medição independente. Tampouco atesta massa/forma do **NORAD 528**, que é outro objeto.

## Contrafactual geométrico, não um limite físico histórico

Para um cilindro circular direito perfeito, sem apêndices, diâmetro \(D=1,5\,m\) e comprimento \(L=7,99\,m\), sua área projetada a um ângulo \(\theta\) entre o eixo e a linha de visada seria:

\[
A(\theta) = \frac{\pi D^2}{4} |\cos\theta| + DL |\sin\theta|.
\]

Área axial **1,7671 m²**, lateral **11,9850 m²**, máximo idealizado **12,1146 m²**. A razão entre máximo e axial é **6,8554**, mesmo mantendo constantes as dimensões ficticiamente exatas. O máximo é ligeiramente superior ao valor lateral por incluir parte da tampa.

Esses números são somente uma **sensibilidade de orientação para um cilindro ideal**. A própria descrição secundária é **Cyl + Irr**, e não possuímos geometria completa, atitude, coeficiente aerodinâmico, identificação da peça 528, nem erros instrumentais. Portanto, não se trata de intervalo de área certificado sequer para o 527, e muito menos para o 528. Não o converter em massa, coeficiente balístico ou localização de reentrada.

**Observações discriminantes:** ficha de engenharia específica do Agena 2313 e carga OPS 0180 com composição e época wet/dry; identificação documentada de peças 528/529; desenho da geometria real e orientação temporal; rastreio primário com referencial, época UTC, sensor, covariâncias e publicação datada. Uma página secundária que repete **1176 kg** não é substituto para elas.

Resultado: **0** novas medições independentes de massa, posto histórico da partição **0/4**, MCMC histórico **NOT_RUN**, nenhum domínio geográfico restringido. Não desbloqueia as PRs [#634](https://github.com/franklinbaldo/conde-incident/pull/634) e [#641](https://github.com/franklinbaldo/conde-incident/pull/641).

Reproduzir com Python unittest sobre tests/test_ftv2313_secondary_geometry_C241.py e execução do módulo tools.ftv2313_secondary_geometry_C241. Os testes não consultam a página volátil em CI.
