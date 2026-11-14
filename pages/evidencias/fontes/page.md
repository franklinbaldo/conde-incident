---
type: Page
title: "Fontes e ocorrências: consulta reversa"
description: "Consultar fontes curadas e verificar as ocorrências documentais associadas, sem inferir testemunhas independentes."
layout: index
language: pt-BR
page_kind: "document"
canonical_route: "/conde-incident/evidencias/fontes/"
---

# Fontes e ocorrências

## Consultar por identificador

<p id="source-lookup-status" role="status" aria-live="polite">O índice dinâmico requer JavaScript. Você pode consultar o arquivo estático abaixo.</p>
<form id="source-lookup-form" hidden>
  <label for="source-lookup-id">Fonte documental</label>
  <select id="source-lookup-id" name="source" required aria-describedby="source-lookup-help">
    <option value="">Escolha uma fonte</option>
  </select>
  <p id="source-lookup-help">Selecione um identificador para ver as ocorrências e seus vínculos. A URL é atualizada para compartilhar a fonte ou voltar à seleção anterior. Nenhum dado é enviado a serviços de terceiros.</p>
</form>
<section id="source-lookup-results" aria-label="Referências da fonte selecionada"></section>

Uma fonte pode aparecer em várias fichas; isso **não significa múltiplas observações físicas independentes**. Este índice reúne apenas referências curadas da matriz, não todas as fontes que possam existir. Uma ocorrência ainda não mapeada não é prova de ausência de documento. A listagem é derivada de arquivos JSON versionados e sua integridade é conferida no navegador antes de qualquer resultado.
<button type="button" id="source-lookup-retry" hidden>Recarregar índice verificado</button>
<script type="module" src="/conde-incident/js/ssg-source-lookup-ui.mjs"></script>

## Navegação sem JavaScript

[Consultar os identificadores de fontes e suas fichas estáticas](/conde-incident/evidencias/arquivo/fontes/).

[Percorrer as ocorrências e famílias no arquivo documental estático](/conde-incident/evidencias/arquivo/).

[Consultar a matriz integral, inclusive ocorrências sem ficha](/conde-incident/evidencias/matriz/). O catálogo reverso não inclui vínculos pós-matriz como observações verificadas e não atribui probabilidades nem localização de queda.

[Evidências](/conde-incident/evidencias/) · [Caderno](/conde-incident/stories/) · [Laboratório anterior](/conde-incident/lab/#/documents)
