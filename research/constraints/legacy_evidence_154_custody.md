# Custódia do `Evidence.lean` prévio, 154 linhas e colisão de IDs tardios

**Questão falsificável:** a antiga biblioteca de evidências (154 registros / 151 rótulos, com duas ocorrências de C44–C46) pode voltar a compilar em Lean 4.35.0 e seus IDs ser resolvidos sem ambiguidades para a matriz C001–C238 atual?

**Resultado auditável:** foi localizado no disco do ambiente Jatobá um arquivo `conde-lean-Evidence.lean` preservado em 11/11/2026, tamanho **102.677 bytes**, SHA-256 **`ac2c1982f2f9bc66d31f3d39cc0247dd02e8815bfef457c5d7ff5a8d6eb6f3ee`**. A árvore original de origem, o ZIP anterior, o registro de `lake build` daquele pacote e a assinatura/custódia de quem o produziu **não foram localizados**. Ele é identificado estritamente como **candidato local preservado, sem atribuição de autenticidade ao ZIP**. Seu conteúdo foi copiado sem alteração em `formal/Conde1963/Evidence.lean`. `Core.lean` recebe apenas o tipo compatível `Outcome`, ausente no núcleo reduzido. O `formal/Conde1963.lean` passa a importá-lo para compilação obrigatória.

## Confrontação com o corpus atual

Fonte A: snapshot recuperado local (arquivo bytes/hash acima), 154 linhas `EvidenceRow`, IDs C01–C151, com variantes `C44.1/.2`, `C45.1/.2`, `C46.1/.2`; as classificações opcionais do arquivo são **avaliações humanas legadas**, não prova de estado físico.

Fonte B: [matriz cumulativa C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), Git blob **`a7978c3a75a153b16ab70118a92c434bba674cb7`**: 241 ocorrências, 238 IDs, C44–C46 com duas variantes cada. Esta matriz é uma compilação documental de relatos, catálogos secundários, observações e modelos; não constitui outra origem instrumental independente.

A auditoria compara os **textos literais de `sourceRow`**, não apenas a coincidência numérica dos IDs. Assim:

| Ocorrências | Interseção semântica | Interpretação |
|---|---:|---|
| C01–C143, contando C44–C46 duas vezes | 146/146 textos idênticos | Custódia de transcrição verificável contra a matriz atual; não valida o conteúdo das fontes subjacentes |
| C144–C151 | **0/8 textos idênticos** | O mesmo ID foi atribuído a proposições diferentes em revisões distintas |
| Total | **146/154 textos idênticos** | Nunca usar `C151` isolado como referência histórica universal |

Exemplos decisivos: `C144` no arquivo local descreve **123 TLE / 119 épocas únicas**; na matriz atual C144 identifica a carta sinótica da **Marinha**. `C148` antigo descreve comparativo de precessão **J2**; C148 atual é um registro da **UFRJ** sobre a edição de *O Jornal*. `C151` antigo descreve **limitações da triangulação orbital**; C151 atual é o perfil de **ventos IGRA Recife**. Assim, importar esta biblioteca sem controlar versões produziria falsa atribuição de fontes e uma restrição orbital incorretamente ancorada em dados meteorológicos.

**Política de identidade:** para os registros recuperados C144–C151, usar `legacy-154:C144`...`legacy-154:C151`, qualificados por SHA-256; para a matriz viva usar `matrix-a7978c3:C144#1`...`matrix-a7978c3:C151#1`. C44–C46 mantêm rótulo **e ocorrência**; equivalência de texto não dispensa avaliação de independência nem proveniência. Não adicionar links do site que apontem para códigos legados reutilizados como se fossem os atuais.

## Controles físicos e teste de aceite

- NASA/Goddard, *Satellite Situation Report*, 15/11/1963, p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf): a matriz C131/C197 documenta a **data** de decaimento de 1963-003B, sem hora nem local. A página não foi reinspecionada nesta PR. Mesma cadeia de rastreamento NASA/NORAD, não duas fontes independentes.
- TLE 528 C179#1 e C25#1: espelho secundário com época 1963-10-27T14:40:16.132512Z, RAAN 198,5261°; o histórico do site continha RAAN 284,1520° sem fonte; a auditoria de origem encontra o valor no código legado, **não** em um instrumento. Nenhum conflito foi arbitrado por média.
- Parâmetros antes/depois: **nenhum novo filtro físico**. Domínio orbital Θ permanece Θ (**0 exclusões**), não-vazio condicionado ao mesmo conjunto anterior; erro terminal (km/graus) e validação holdout **NOT_RUN** porque reidentificar registros textuais não determina posição orbital nem erro de rastreamento. Preserva o controle adversarial C147 antigo, quadrático **0,01412** vs. conjunto H60 **0,02595 rev/dia**, como **registro histórico sem validação nova**, não como dado independente.
- Dados ainda necessários para restringir Θ: linhas TLE **originais** datadas e com proveniência para NORAD 00528 (após 27/10 se existirem), frame/época de geração, covariância ou envelope observacional, além de séries 527/529 coépocas para holdout. Uma observação de localização/tempo de reentrada exigiria sensor coevo independente e incerteza. Sem isso, **Conde continua indeterminado**.

### Reproduzir

```bash
python3 formal/scripts/audit_legacy_154.py
python3 -m unittest discover -s formal/tests -p 'test_legacy_evidence.py' -v
cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean
```

Compilação Lean e auditoria de axiomas devem passar no workflow `lean-core.yml` no SHA exato da PR. O script retorna erro se arquivo restaurado/matriz perderem hash, cardinalidade, variantes C44–C46 ou a lista **exata** de oito aliases. **Fazer o build não autentica o ZIP desaparecido nem prova a queda.**
