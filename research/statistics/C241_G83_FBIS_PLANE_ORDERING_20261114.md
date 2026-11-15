---
type: Experiment
title: "C241 G83: cruzamento mecânico de janelas do plano com relógios condicionais"
description: "Tabela exaustiva dos NORAD 528 e 637 contra carimbos FBIS sem autenticação; nenhum vínculo histórico inferido."
experiment_id: C241-G83
verification_status: CLOCK_UNRESOLVED_CONDITIONAL_ORDERING_ONLY
---

# G83: janelas do plano e o limite condicional da transmissão

**Problema:** o Elefante solicitou em [Conde #870](https://github.com/franklinbaldo/conde-incident/issues/870) uma linha por raiz geométrica 528/637, dois ramos orbitais, Bahia UTC−3 e os possíveis limites superiores do relato vindos de [#886](https://github.com/franklinbaldo/conde-incident/issues/886). A hora independente de [#871](https://github.com/franklinbaldo/conde-incident/issues/871) permanece desconhecida.

**Insumos versionados:** os quatro `research/statistics/c241_plane_{528,637}_{constant_a,decaying_a_last_secant}.json` da PR #892, calculados para uma **câmera moderna de 2022**, e `research/constraints/fbis_1963_clock_branches.json` do Polvo (PR #940). O JSON G83 guarda SHA-256 dos cinco arquivos de entrada. O script G83 só compara timestamps existentes; não faz propagação orbital, reconstrução, ajuste ou reamostragem.

| Objeto e ramo orbital | Raízes | `2330` = GMT: antes / depois de 08/11 23h30Z | `2330` = hora Guanabara: antes / depois de 09/11 01h30Z |
|---|---:|---:|---:|
| 528, semieixo constante | 9 | 6 / 3 | 7 / 2 |
| 528, secante de decaimento | 9 | 6 / 3 | 7 / 2 |
| 637, semieixo constante | 8 | 6 / 2 | 6 / 2 |
| 637, secante de decaimento | 8 | 6 / 2 | 6 / 2 |

**Linha decisiva:** a raiz do plano do 528 em 08/11 às aproximadamente 23h43 UTC fica depois do limite `GMT` e antes do limite `RIO_LOCAL`. Isso é **apenas ordenação condicional**, não exclusão real do satélite, porque o relógio FBIS é `UNRESOLVED`, o carimbo refere-se à transmissão e a geometria do plano **não** informa a fase ou posição do veículo. Outras raízes, inclusive as posteriores ao dia de decaimento catalogado, continuam no ledger para inspeção, mas aparecem com os dois flags de corte NASA; esses cortes são fins de dia hipotéticos, **não horas medidas de reentrada**.

**Regra de decisão:** `OTHER_UNVERIFIED=null`, `independent_event_time_871=null`, `active_constraint=false`, `orbit_exclusion_licensed=false`, `posterior=false` e `impact_probability=null`. Sob uma transmissão hipoteticamente válida, as raízes posteriores à emissão não podem ser identificadas com o evento noticiado, mas isso **não** descarta a órbita, nem cria uma hora para o evento, nem licencia inferir probabilidade de queda.

**Reprodução sem download:** `python3 tools/c241_fbis_plane_ledger_g83.py --repo . --check`. A suíte `tests/test_c241_fbis_plane_ledger_g83.py` testa replay de bytes, contagens, raiz discriminante, rejeição de relógio artificialmente autenticado, carimbo para ramo desconhecido, horário Bahia corrompido e raiz repetida. O teste negativo não requer nova modelagem. Quando chegar um fac-símile com relógio independente, o responsável deve revisar o contrato antes de atualizar o ledger; até lá, não repetir análises de massa ou geografia.
