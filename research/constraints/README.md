# Conexões cumulativas entre documentos e modelos

A pesquisa do caso Conde é um **grafo de conhecimentos em evolução**, não uma sequência de tentativas isoladas de reduzir agora a região orbital admissível. Informações novas devem se conectar às equações e permanecer disponíveis para interpretações futuras.

## Exemplo operacional: boletins NASA de 15 e 30/11/1963

Arquivo: `ssr_1963_observable_graph.json`. Foram associados 16 valores documentais (período nodal, inclinação, apogeu, perigeu, para os objetos 527 e 529 em dois boletins) a estados orbitais individuais, observáveis previstos, épocas de observação **latentes** e relações de forças compartilhadas. Oito diferenças entre **valores publicados** conectam os boletins no tempo.

A diferença nominal de período entre as publicações do NORAD 529 é `92,2 - 92,6 = -0,4 minuto`. Isso **não é** uma medição da derivada temporal do período: os relatórios não fornecem aqui a época específica de observação nem a covariância ou possível atualização das soluções orbitais. O observável está conectado ao grafo para uso posterior.

**Fonte e grau:** relatórios NASA/Goddard contemporâneos, respectivamente [15/11](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) e [30/11](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf). Números transcritos da inspeção visual de rodada anterior, sujeitos a conferência da linha original no novo fluxo. A fonte é **primária da publicação do catálogo**; não é observação radar independente feita pela NASA. Ambos pertencem à mesma família de dados de rastreamento e não contam como duas redes independentes.

Matriz local: `ORB-DA-20261112-01/02` na PR #42; **ainda precisa de reconciliação de ID/ocorrência** com a matriz global. Nunca reutilizar um ID C sem verificar colisões. Essa ponte de dados não altera os arquivos originais nem as fontes primárias.

### Estados da informação

- `CONNECTED_PENDING_CALIBRATION`: ligação preservada, unidade e equação identificadas, mas época/covariância/operador precisam de dados adicionais. **É avanço de conectividade**, ainda não é uma restrição física ativada.
- `CANDIDATE_NOT_ACTIVATED`: candidato que poderá futuramente definir predicado `C_i(θ)` em Lean, com hipóteses explícitas. `null` significa desconhecido.
- `ACTIVE` (não usado neste exemplo): só depois de autenticar observação, fixar convenção e tolerâncias defensáveis, validar o observador físico e o integrador/holdouts. Só restrições ativas participam do domínio `Θ_n`.
- `CONFLICTING`: cenários rivais com proveniências separadas; nem descartar nem misturar prematuramente.

Os dados jornalísticos também geram variáveis, por exemplo *veículo, testemunha, origem editorial, hora da publicação, tipo da alegação, independência da apuração*. Isso pode restringir uma árvore de dependência narrativa, **não automaticamente a órbita**. Da mesma forma, uma não localização em pesquisa de arquivo é observação do processo de busca, não prova da ausência de queda.

### Caminho de integração posterior

1. 🦉 Coruja ou 🐢 Tartaruga recuperam o documento, identificam ocorrência e medição; preservam hash, época, incerteza, unidades, local, canal e genealogia.
2. Polvo liga `measurement_id` → operador físico verificável → variáveis livres, com hipótese condicional em Lean 4.35.0. Não precisa inventar prova ou reduzir o domínio no mesmo commit.
3. Castor estima operadores diante dos estados 527/528/529, modelos de arrasto/gravitacionais e épocas efetivas; produz resíduos, limites de erro, validação fora da amostra e, **quando houver base**, restringe o domínio.
4. Novos documentos podem completar campos ausentes e ativar restrições antigas. A inferência sobre Conde emerge da **conjunção** de restrições justificadas, nunca de exigir que cada documento sozinho decida a localização.

### Contrato executável

```bash
python3 -m unittest discover -s tests -p 'test_cumulative_constraints.py' -v
python3 formal/scripts/check_cumulative_connections.py \
  --output /tmp/conde-connected-handoff.json
```

O resultado registra número de observações, vínculos derivados e fontes **efetivamente distintas** e exporta as variáveis com unidades normalizadas. O status `PENDING_CALIBRATION_NOT_DISCARDED` é intencional, **não** uma falha.

**Métricas separadas de progresso:** `delta_links` (grafo expandido, conexões e dependências explicitadas) e `delta_feasible_domain` (contração numérica demonstrada *quando possível*). O primeiro pode aumentar enquanto o segundo permanece desconhecido ou ainda não avaliado.

O grafo não afirma passagem terminal do NORAD 528 sobre Conde, não fabrica distribuição de probabilidade, e não prova que uma esfera ou cratera existiu.
