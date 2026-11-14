---
type: Guide
title: "C241: massa nominal Ferret de 1500 kg não identifica o 528"
description: "Auditoria de uma fonte secundária externa divergente do GCAT e critérios para qualificá-la como evidência física."
---

# Ferret 3: a listagem de 1500 kg frente aos campos GCAT

Em 14/11/2026, uma consulta à página [Ferret, Astronautix (Mark Wade)](https://astronautix.com/f/ferret.html) encontrou **1500 kg** na entrada **OPS 0180 / Ferret 3 / Agena B 2313**, identificada como **NORAD 527 / 1963-003A**. O corpo HTML obtido contém **53.630 bytes**, SHA-256 `70fa299371bad0efd27ce920ea05bac60be38412521d9a6a3ead3162aaa20b63`. O registro de custódia resumido, sem copiar os bytes integrais, está em `research/tle_custody/ferret_1500_crosssource_C241.json`. A versão histórica da página, a referência original do valor e o método de apuração não foram determinados.

A mesma página escreve exatamente **1500 kg** para **Ferret 1 / NORAD 242** e **Ferret 2 / NORAD 308**. A repetição em missões distintas é compatível com um valor **nominal de classe ou de configuração de lançamento**. Não comprova que três massas tenham sido medidas independentemente, nem que 1500 kg descreva o inventário orbital no instante de fragmentação.

Em contraste, o [GCAT C241-L40](../tle_custody/gcat_mass_semantics_C241-L40.json) registra **`S00527 Mass=306 kg`, `TotMass=1176 kg`**, e **`A00324 Mass=900 kg`, `DryMass=870 kg`**. A simples subtração produz **324 kg** em relação ao campo `TotMass` e **294 kg** em relação à soma nominal 306+900. São **diferenças entre descrições de bases desconhecidamente compatíveis**, não discrepâncias instrumentais, combustível consumido, fragmentos perdidos, incertezas ou medidas dos objetos 528/529. Astronautix e GCAT são famílias editoriais distintas, mas a independência dos dados subjacentes está **não demonstrada**.

## Identificabilidade e próxima observação discriminante

O vetor físico `(m527,m528,m529,X)` na época de separação continua com **posto histórico 0/4**, porque nenhuma das duas listagens oferece equação de inventário na mesma época com composição verificada. Mesmo se uma ficha de engenharia comprovasse o total de um inventário fechado, seria **1/4**, deixando três direções indeterminadas. Os 1500 kg **não entram** como prior, likelihood, total de massa ou validação independente de massa.

A próxima peça realmente discriminante é uma **ficha de engenharia específica do voo OPS 0180/Ferret 3/Agena 2313**, com instante e convenção wet/dry, composição fisicamente enumerada, massas/erros e relação com os três registros NORAD. Uma ficha genérica de Ferret ou uma página que replique 1500 kg não basta. Uma medição independente do 528 com época, instrumento, incerteza e geometria aerodinâmica poderia reduzir outros graus de liberdade, mas `B=CdA/m` sozinho não identifica massa.

**Estado:** `historical_constraint_active=false`, `historical_mcmc=NOT_RUN`, `historical_mass_posterior=null`, `geographical_domain_reduction=false`. O resultado não estima massa do 528 nem local ou hora de reentrada, e não desbloqueia as drafts [#634](https://github.com/franklinbaldo/conde-incident/pull/634) e [#641](https://github.com/franklinbaldo/conde-incident/pull/641).

Reproduzir: `python3 -m unittest discover -s tests -p test_ferret_mass_crosssource_C241.py -v` e `python3 -m tools.ferret_mass_crosssource_C241`. A auditoria deliberadamente não consulta uma página volátil em tempo de CI; verifica o extrato de custódia e o GCAT versionados.
