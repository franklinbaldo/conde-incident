# 🦅 Caderno 08: revisão independente de fontes, código e inferências

**Objeto:** [PR #50](https://github.com/franklinbaldo/conde-incident/pull/50), commit b91cf9641820f47fb9e7e75c76d6123f4988b1ad, Git blob 61e4d07f10441b5ec5e6d56758cc85ffdf18766c. **Delta desde capítulo 07 (#44):** correção de afirmações de uma interface experimental, não descoberta histórica. Matriz cumulativa [C01/C02, C197–C202 na PR #1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md). C241-T3 deriva do espelho TLE secundário da [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), não de rastreios independentes.

## 1. Autenticidade e cadeias documentais

- [NASA, Satellite Situation Report, 15/11/1963, p. impressa 8 / página 10 do PDF](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10): fac-símile público **diretamente reinspecionado por imagem**. Coluna DECAY, linha 1963 3B, 8 NOV 63. Documenta dia catalogado, **sem hora, posição ou registro de impacto**. C197–C202. Integridade do arquivo em relação ao exemplar instrumental original: NÃO VERIFICADA.
- [FBIS 03, EOP-UAP-D001, p. única](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf): fac-símile público **diretamente reinspecionado**. Transcrição atribui o texto a RADIO TUPI, 2330 8 NOV 63 W. A esfera, buraco de quatro metros de profundidade, corpo e inscrições são partes da **mesma** notícia. Não é gravação nem avistamento independente. O relógio de transmissão não localiza impacto e não se presume fuso.
- **Dependências:** Tupi→FBIS é uma cadeia jornalística; NASA cataloga decaimento orbital e não corrobora cratera; o espelho TLE de #14 é secundário, último registro 528 em 27/10 **naquela cópia**, não evidência de que o rastreio real cessou. Fontes em categorias distintas não são duas confirmações de um impacto.

## 2. Revisão reprodutível de software e prosa

O [código antigo](https://github.com/franklinbaldo/conde-incident/blob/c84cce85e51252f9e589a851950385aea008e951/src/components/ExecutiveSummary.tsx) (Git blob 5eee17e3ff05da5fcbaf6e0bb0b2a3384991d834) contém os quatro enunciados: VEREDITO ASTRODINÂMICO & DOCUMENTAL, 19:48 UTC (Rev 14), ~0,0062% e Boato Fabricado. O [código proposto na PR #24](https://github.com/franklinbaldo/conde-incident/blob/115e58693a64d23789e1f75f50146105f114b3be/src/components/ExecutiveSummary.tsx) (Git blob 7629820680d0ea5d128adc3a97260dd64166b1f7) elimina os quatro e exibe Resultado: indeterminado. Código é fonte primária **da interface**, não das observações orbitais.

A Coruja corretamente relata alteração em **Draft**, sem alegar publicação. Seu capítulo #50 está empilhado na PR #44, mas a mudança #24 segue em **outro ramo**: a história NÃO incorpora automaticamente o componente corrigido. A [execução editorial #43155282955](https://github.com/franklinbaldo/conde-incident/actions/runs/43155282955) terminou SUCCESS no commit b91cf964; job deploy SKIPPED. A [execução #43154199654](https://github.com/franklinbaldo/conde-incident/actions/runs/43154199654) confirmou build da correção no commit 115e5869, sem deploy. Não há prova de que uma página pública tenha sido alterada, nem de que todas as outras telas sejam corretas.

## 3. Lógica, Lean, modelos e limites

A existência do relato FBIS e a data NASA permitem pelo menos quatro contramodelos lógicos (impacto/não impacto × identidade/não identidade dos eventos); são **mundos sintéticos sem frequência nem observação**. Não é prova Lean 4.35.0. As PRs #37/#43 contêm contratos sintéticos/alternativas, sem domínio orbital histórico autenticado e reduzido. Nenhum dado novo traz estado/época terminal com custódia primária, incerteza calibrada, holdouts posicionais ou simulação validada. Assim, nenhuma probabilidade de impacto, localização, exclusão de Conde ou hora específica pode ser endossada.

## 4. Conclusão, gates e próxima dúvida

**Parecer factual favorável à redação de #50 neste blob**, condicionado à persistência destas ressalvas e ao CI no SHA final, sem autorização de publicação. Auditor Python independente verifica **três Git blobs SHA-pinados**, alegações antes/depois, IDs, referências e ressalvas, com testes de falsificação. Seu PASS não transforma um relatório documental em evidência física.

**Bloqueio de arquitetura para #3 e a pilha editorial:** [PR #22](https://github.com/franklinbaldo/conde-incident/pull/22) estabelece SSG Rust, mas [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3) ainda compila Zola. CI de Zola não é gate da migração SSG. Integração e publicação dependem da revisão do novo conjunto reconciliado. A conta proprietária não pode formalmente autoaprovar PR.

**Próxima dúvida:** identificar por arquivo outras telas de laboratório que ainda apresentem hipóteses com precisão terminal/estatística indevida, ligando cada alegação ao ID, origem instrumental e erro. Nenhum contato, merge, publicação nem alteração do blog pessoal.
