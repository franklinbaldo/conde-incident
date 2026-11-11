# Caderno de reportagem — Coruja

O texto-fonte **canônico** é `stories/YYYY-MM-DD-slug.md`, com `title`, `date`, `summary`, `chapter`, `author`, `status` no front matter YAML. Uma PR por capítulo novo, somente após avanço material (descoberta, refutação, correção ou teste significativo). `chapter` é único e cronológico; artigos da mesma data são ordenados pelo capítulo.

## Publicação Zola

O Caderno não é mais renderizado pelo React. `node scripts/prepare-zola.mjs` valida os textos e transforma a fonte canônica em páginas TOML nativas do Zola **geradas** em `content/stories/` (não commitá-las). A página `content/_index.md` e os templates são o site editorial; `static/css/` oferece o estilo. O laboratório científico React/Vite é construído separadamente em `/conde-incident/lab/` e incorporado ao artefato final pelo workflow. Não duplicar o leitor de histórias dentro do aplicativo científico.

```sh
bun install --frozen-lockfile
bun run lint
SCIENCE_BASE=/conde-incident/lab/ bun run build
mkdir -p static/lab && cp -R dist/. static/lab/
node scripts/prepare-zola.mjs
zola check --skip-external-links
zola build
node scripts/check-site.mjs
```

Apenas `push/main` executa `actions/deploy-pages`. PRs testam build e navegação, mas não publicam. Pages precisa estar configurado para GitHub Actions. O site fica em `/conde-incident/` e não altera o blog pessoal.

## Método jornalístico

Abrir com pergunta narrativa real, sem cenas, citações ou pessoas inventadas. Citar fontes originais, datas e páginas; distinguir observação direta, relato retransmitido, catálogo derivado, hipótese e inferência. Repetição documental não vale descoberta. Build não substitui revisão independente do 🦅 Gavião; a publicação depende de merge pelo 🐘 Elefante e confirmação do deploy. Sem avanço material, registrar investigação negativa e não criar artigo.

## Links, fontes e estado da interface

O Zola gera um endereço permanente HTML para cada capítulo; compartilhar `/conde-incident/stories/<slug>/` não depende de hash ou JavaScript. O React fica exclusivamente em `/conde-incident/lab/`; os links `#/map` e `#/summary` identificam abas científicas, não evidência validada. O texto editorial continua a cargo da Coruja.

O rodapé dos capítulos liga à **versão fixada** da matriz C001–C238 da PR #1 para contextualizar fontes e suas dependências. A aba Evidence ainda não faz parte da branch editorial: não se deve prometer um link direto para ela antes da reconciliação científica. O build testa endereço, canônico, metadados sociais, navegação e ponte de fontes; não certifica leitura de tela, mobile real, autenticidade histórica nem deploy.
