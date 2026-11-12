# Contrato de publicação: SSG (Rust) para o Conde

Decisão do proprietário em 11/11/2026: **SSG** é o único gerador de páginas editoriais do Conde. Substitui Zola; a aplicação científica React continua em `/lab/`. Este documento é contrato de migração, **não** comprovação de implantação.

Documentação primária: https://docs.rs/ssg/latest/ssg/ e https://github.com/sebastienrousseau/static-site-generator

## Responsabilidades e fronteiras

- **Coruja, PR #3**: preservar todos os capítulos Markdown e sua linha editorial; converter para **YAML frontmatter** e layouts **MiniJinja** aceitos pelo SSG. Manter fonte canônica única (idealmente `stories/*.md` com conversão mínima, ou `content/` se suportar o contrato editorial sem duplicação). Não eliminar evidências ou textos para facilitar a migração.
- **Raposa, PR #1 e interfaces**: preservar Evidências & Pesquisa e o laboratório React (build Vite com base `/conde-incident/lab/`), ligando-os ao Caderno e à navegação estática sem rota quebrada.
- **Gavião**: revisar de forma independente a fidelidade da migração, a rastreabilidade das fontes, o HTML resultante, os links, a publicação e o CI.
- **Elefante**: reconciliar dependências e integrar somente quando revisão e CI no HEAD exato forem satisfatórios, sem alterar branches de terceiros por conveniência.

## Compatibilidade e reprodutibilidade

1. **Fixar a versão exata** do crate SSG no GitHub Actions, com instalação pelo Cargo ou binário confiável e `ssg --version` registrado. A série `0.0.x` não promete compatibilidade entre releases. Conferir CLI pelo `ssg --help` e `ssg build --help` do binário escolhido antes de fechar comandos.
2. O SSG usa **Markdown + frontmatter YAML + MiniJinja**. Não portar `config.toml`, templates Tera ou frontmatter TOML de Zola supondo equivalência automática. Ajustar `ssg.toml` e layouts conforme a versão escolhida. O código React não deve virar motor de renderização dos capítulos.
3. No PR: executar CLI real `ssg check`, `ssg build` e `ssg audit` se disponibilizados pela versão fixada, registrar logs e conferir os arquivos gerados. Não substituir teste real por mera busca de strings num YAML.
4. Conferir explicitamente `/conde-incident/`: página inicial, lista e **todos** os capítulos, links de fontes, CSS/JS, assets e página do laboratório em `/conde-incident/lab/`. O artefato final enviado a Pages deve reunir estático editorial e lab.
5. Separar ambiente de PR (somente verificações, **nenhum deploy**) do push na `main` (deploy de Pages via GitHub Actions). Não criar credenciais nem alterar o blog pessoal. Depois do merge, verificar configuração real Pages, deployment no SHA da main, URLs com HTTP válido e conteúdo correspondente. Se não verificou, usar `NOT_VERIFIED`.
6. Preservar um capítulo por PR, publicado apenas com descoberta, correção ou falsificação **nova e verificável** desde o capítulo anterior. Distinguir documento primário, reportagens dependentes, inferência, hipótese e resultado negativo. Links de páginas e CI não demonstram reentrada física.

## Critério de aceite

- [ ] Conteúdo original preservado, proveniência editorial comparada.
- [ ] Zola removido **do pipeline final**, sem motores editoriais paralelos.
- [ ] SSG versionado e executado em GitHub Actions no HEAD definitivo; build e auditoria aprovados.
- [ ] Evidências, Caderno e laboratório React navegáveis; base path auditado.
- [ ] Revisão independente do Gavião e CI verde.
- [ ] Deploy pós-merge verificado antes de anunciar publicação.

Este contrato não altera a matriz científica ou conclusões orbitais.
