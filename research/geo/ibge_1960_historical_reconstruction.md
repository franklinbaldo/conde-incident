---
type: Guide
title: "CGEO-10: malha municipal retrospectiva IBGE nominal 1960, Conde/BA"
description: "Reprodução auditável da geometria nominal 1960 e veto de retroprojeção jurídica a 1963"
---

# CGEO-10 | Malha cartográfica IBGE de 1960

**Achado verificável:** o IBGE disponibiliza [ZIP histórico 05_malha_municipal_1960.zip](https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/evolucao_da_divisao_territorial_do_brasil/evolucao_da_divisao_territorial_do_brasil_1872_2010/municipios_1872_1991/divisao_territorial_1872_1991/1960/05_malha_municipal_1960.zip), no catálogo *Evolução da Divisão Territorial do Brasil 1872–2010*. **Há um polígono cartográfico para Conde (BA) de época nominal 1960.** Não é um levantamento contemporâneo de 1960 nem o polígono legal comprovado de 08/11/1963. O metadado interno registra definição de projeção em **2013**, e o índice do IBGE registra arquivo em **02/06/2016**. A data de referência da cartografia é 1960, não a época de uma medição geodésica.

**Fonte primária:** URL acima, SHA256 integral do ZIP em 12/11/2026: 261399b8557ee26c118e94b13cebf3b6b3e1c70e91b5e8438a348847b875120f. Arquivos internos com base "05-malha municipal 1960": SHP, SHX, DBF, PRJ e metadados XML. O DBF tem **2.766 registros**. Na linha índice **2448 (zero-based)**, codigo=2908606 e nome=Conde. Não confundir com Conde/PB nem São Francisco do Conde/BA.

O registro SHP (SHA256 do conteúdo do registro: 2970e4ee04d39e1c4865dbdb56ee1a21db9999d8c964ef0f08828c001783c601) contém um **polígono de anel único fechado, 47 pontos**. A projeção do PRJ original é World_Polyconic, DATUM SIRGAS_2000, elipsoide GRS_1980, meridiano central **−54°**, latitude de origem **0°**, unidade **metro**, sem código EPSG da projeção. O envelope XY nativo é [1761251.25, -1390060.375, 1795968.5, -1336775.625] em Easting/Northing. **Não são lon/lat:** não rotular como EPSG:4326 ou EPSG:4674 sem transformação explícita. O SIRGAS2000 de arquivo compilado em 2013 não certifica época, exatidão nem fronteiras de 1960.

## Exportação e contrato para Castor

O [JSON nativo](conde_ibge_1960_world_polyconic.json) contém 47 XY, fonte e hashes de ZIP/membros/registro/coordenadas, identidade DBF, parâmetros da projeção, e os nulos históricos. O [extrator](../../tools/conde_ibge_1960.py) sem dependências GIS externas reproduz esse arquivo a partir do ZIP **original**, verificando SHA integral, membros, linha DBF, registro SHP e PRJ antes de aceitar geometria. Nenhum download ocorre no CI obrigatório; reprodução online requer obtenção real de bytes da fonte original. Comandos:

    curl -fL -o /tmp/05_malha_municipal_1960.zip 'https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/evolucao_da_divisao_territorial_do_brasil/evolucao_da_divisao_territorial_do_brasil_1872_2010/municipios_1872_1991/divisao_territorial_1872_1991/1960/05_malha_municipal_1960.zip'
    python3 tools/conde_ibge_1960.py --extract /tmp/05_malha_municipal_1960.zip --output /tmp/conde1960.json
    cmp /tmp/conde1960.json research/geo/conde_ibge_1960_world_polyconic.json
    python3 tools/conde_ibge_1960.py --date 1963-11-08
    python3 -m unittest tests/test_conde_ibge_1960.py -v

**Grafo:** CGEO-10 → municipal_cartography_1960 (**reconstrução cartográfica**); CGEO-09 → legal_boundary_1963_LATENT (**continuidade normativa não resolvida**); municipal_cartography_1960 → legal_boundary_1963_LATENT (**NOT_A_VALIDATED_TEMPORAL_BRIDGE**). As edições modernas CGEO-01/02 não equivalem a medições independentes da mesma fronteira histórica; provêm da mesma família institucional.

**Veto:** o contorno de 1960 não prova perímetro legal de Conde em 08/11/1963. Permanecem desconhecidos atos intermediários, anexos históricos de 1944/1953, generalização cartográfica, precisão horizontal, época geodésica de um eventual ponto e posição independente do evento. Portanto legal_boundary_for_date=null, date_1963_membership=null, coordinate_transformation_to_event_frame=null e can_constrain_reentry=false. **Não usar para localizar queda, excluir trajetória ou calcular probabilidade de reentrada.** A matriz histórica C001–C238 permanece inalterada; este é registro complementar, com vínculo para CGEO-09.

**Resultado negativo:** o ZIP não contém uma observação física de 1963 nem validade legal específica para 08/11/1963. Não se obtiveram datum/erro de uma medição de fronteira feita em 1960. A posição XY é projetada: sem reprojeção justificada, não comparar com lon/lat de outros conjuntos.

**Próximo teste:** confronte o traçado retroconstruído com os anexos de 1944/1953 e atos de 1959–1963, quando autenticados, e estabeleça orçamento de erro antes de admitir georreferenciamento ou análise espacial histórica. Não duplicar a custódia legal atribuída à Lontra.
