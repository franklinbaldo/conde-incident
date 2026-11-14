---
type: Page
title: "Auditoria de TLEs"
description: "Sintaxe, checksum e custódia de elementos orbitais."
layout: index
language: pt-BR
page_kind: "experiment"
canonical_route: "/conde-incident/simulacoes/tles/"
---

# Auditoria de TLEs

Um checksum TLE válido verifica somente a estrutura da linha examinada. Não autentica a origem histórica, o instrumento, a época nem a consistência de sua associação ao objeto.

[Inspecionar o par TLE secundário do 528, seus checksums e sua proveniência, sem JavaScript](/conde-incident/simulacoes/tles/custodia/)

## Verificador local de checksum

Insira **duas linhas de sua escolha**, cada uma com exatamente 69 caracteres. Você pode colar as duas linhas juntas no campo **Linha 1**: o formulário as separa sem modificar os caracteres internos; confira as duas antes de verificar. Esta ferramenta roda no navegador, sem enviar o texto a serviços externos, e reproduz apenas as verificações mínimas de comprimento, prefixo/NORAD e dígito módulo 10 do laboratório legado. Ela não autentica TLE histórico, sensor, época, parâmetros orbitais ou local de reentrada.

<form id="ssg-tle-audit" class="tle-audit" hidden>
  <label for="ssg-tle-line1">Linha 1</label>
  <textarea id="ssg-tle-line1" name="line1" rows="2" wrap="off" spellcheck="false" autocapitalize="off" autocomplete="off" required aria-describedby="ssg-tle-instructions"></textarea>
  <label for="ssg-tle-line2">Linha 2</label>
  <textarea id="ssg-tle-line2" name="line2" rows="2" wrap="off" spellcheck="false" autocapitalize="off" autocomplete="off" required aria-describedby="ssg-tle-instructions"></textarea>
  <p id="ssg-tle-instructions">Espaços e quebras contam. Nenhuma linha é corrigida automaticamente. O resultado é local e não é armazenado.</p>
  <button type="submit" aria-label="Verificar duas linhas">Verificar duas linhas</button>
  <div id="ssg-tle-results" class="tle-audit-results" role="status" aria-live="polite" tabindex="-1"></div>
</form>
<script type="module" src="/conde-incident/js/ssg-tle-syntax.mjs"></script>

O formulário aparece quando JavaScript está disponível. A [ficha estática de custódia](/conde-incident/simulacoes/tles/custodia/) continua acessível sem scripts, e o laboratório legado preserva a inspeção dos seus conjuntos incorporados.

[Abrir auditoria TLE interativa no laboratório anterior](/conde-incident/lab/#/tles)

Os elementos disponíveis no laboratório podem incluir linhas secundárias ou ilustrativas. É preciso separar integridade sintática, custódia, referencial e validação orbital para os objetos 527, 528 e 529.

[Mapa](/conde-incident/mapa/) · [Comparação dos objetos](/conde-incident/simulacoes/triangulacao/) · [Simulações](/conde-incident/simulacoes/)
