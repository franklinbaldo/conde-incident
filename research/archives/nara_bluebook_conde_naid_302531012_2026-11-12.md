# Conde, Bahia, novembro de 1963: unidade original do Project Blue Book (NARA 302531012)

**Responsável:** 🦦 Lontra · **auditoria:** 12/11/2026 · **escopo:** arquivo, conteúdo e proveniência, não conclusão sobre a queda · **issue:** [#105](https://github.com/franklinbaldo/conde-incident/issues/105).

## Achado e identidade custodial

Foi recuperado no **inventário em lote publicado pelo National Archives and Records Administration (NARA)** o registro de **unidade documental `naId: 302531012`**, título exatamente **`Conde, Bahia, BRAZIL, November 1963`**, nível de descrição **`fileUnit`**. A unidade integra **RG 341**, série sanitizada de arquivos de casos do Project Blue Book **`naId: 597821`**. O inventário indica **microfilme T1206, rolo 49** (início do arquivo), sem exigir inferência por proximidade de datas.

- Ficha NARA: <https://catalog.archives.gov/id/302531012>.
- Página oficial dos lotes UAP, seção **Textual Records and Microfilm**: <https://www.archives.gov/research/catalog/catalog-bulk-downloads/uap-bulk-download>.
- Inventário JSON **oficial**: <https://catalog.archives.gov/medialz/bulk-downloads/uaps/JSON/catalog-export-597821.json> (90.778.944 bytes, SHA-256 `f5070879f0a55cfc07bdaf003d253e60315a11429aab51e9553fbf288cff429d` no download de 12/11/2026).
- `onlineResources` do próprio registro menciona Fold3 como colaborador da digitalização, **não** como testemunha independente de 1963. `accessRestriction` e `useRestriction` constam como `Unrestricted`.
- Origem dos três objetos: `https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/`.

| Página da unidade | objectId NARA | Arquivo original e URL | Bytes efetivamente baixados | SHA-256 |
|---|---:|---|---:|---|
| 1 | 302531013 | [0809.jp2](https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/0809.jp2) | 1.756.950 | `4e8e460cfe8dfa0f0d6ea6b02017e6ff63915935dc5be5bde8e96f52faf6f326` |
| 2 | 302531014 | [0810.jp2](https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/0810.jp2) | 1.865.459 | `136be026e23acdd5e7ff0a5307e04bef799249b48346072a43cae1506be37ce9` |
| 3 | 302531015 | [0811.jp2](https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/0811.jp2) | 1.852.266 | `f9c55ab0b14d6e121a4419bef72519a68db29a9ceea6c5bca5ea31fb826cdce7` |

**Teste de custódia realmente executado:** requisições públicas GET retornaram HTTP 200 para todos os objetos, com `Content-Type: image/jp2`, cabeçalho JPEG 2000 (`0000000c6a5020200d0a870a00000014`), comprimentos iguais ao inventário e hashes calculados do corpo binário. A identificação do original pelo hash garante reprodução dos bytes obtidos nesta sessão, não autentica por si só as afirmações da USAF.

## Leitura visual das imagens, sem OCR como fonte

As **três imagens de digitalização NARA foram abertas em visões reduzidas**. As linhas particularmente relevantes das mensagens foram ampliadas para inspeção. Não há numeração impressa de páginas do dossiê; `0809`, `0810` e `0811` são nomes sequenciais dos objetos digitalizados, **não páginas impressas 809–811**.

**Imagem 1, `0809.jp2`:** ficha com título `PROJECT 10073 RECORD CARD`, data **8 Nov 1963**, `Conde, Bahia, Brazil`, fonte assinalada `Civilian`, fotografia marcada `No`, conclusão em `Other` com anotação **`Hoax`**. O resumo registra a história de globo metálico e pessoa dentro; comentários atribuem a conclusão a notícia de imprensa sem fatos e aparente fabricação no Rio. **É uma classificação administrativa posterior à alegação, não exame do local nem depoimento independente**.

**Imagem 2, `0810.jp2`:** mensagem **USAIRA Rio de Janeiro → TDAOS, Wright-Patterson AFB**, com referência temporal no cabeçalho **14 NOV 1963** (`141955Z`; conferir código de transmissão e horário antes de uso quantitativo). É **a pista jornalística nova desta rodada**: o remetente identifica notícia no jornal **`O GLOBO` de 8 de novembro de 1963**, dizendo ter recebido de Salvador a informação de um grande globo metálico que teria caído em Conde. O mesmo emissor afirma não conseguir confirmar o objeto e que o cônsul mencionara a possibilidade de balão. Há referência a conversa com Capitão Cole e Coronel Kalb e a possibilidade de investigação posterior. **O exemplar de O Globo NÃO foi recuperado, a expressão do telegrama é notícia relatada por terceiros e a hora da edição não é conhecida**. Logo, não se afirma que o jornal antecedeu a Rádio Tupi às 23h30 nem que sua fonte de Salvador fosse independente.

**Imagem 3, `0811.jp2`:** segunda mensagem da **USAIRA Rio**, cabeçalho **21 NOV 1963** (`211430Z`), referência interna **`C-116`** e ao telegrama anterior **`C-113`**, reproduz o parecer do consulado de Salvador: alegação aparentemente fabricada no Rio, ausência de confirmação por repórteres e balão hipotético não verificado. Trata-se **da mesma cadeia informacional do consulado/Midkiff, e não de uma nova inspeção ou testemunha**.

## Relações com a matriz preexistente

- **C232–C238:** antes havia uma classificação Blue Book em um índice **sem fac-símile de dossiê** e uma pista de catálogo externo para três páginas. Agora o registro **NARA custodiante, com NAID individualizado e as três imagens oficiais lidas**, fecha essa lacuna específica. O número externo `9737078` **não foi provado** correspondente ao NAID 302531012 por concordância de imagens; não presumir equivalência de identificação de base externa.
- **C01–C03:** a ficha policial é posterior e recicla o enredo do globo, não eleva o grau de confirmação da queda, cratera, cadáver ou inscrições.
- **C05–C10 / A-628:** as mensagens USAIRA são **documentos institucionais distintos** e confirmam a circulação administrativa da apuração, mas a mensagem 21/11 é **dependente do parecer consular já documentado**. Não multiplicar testemunhas.
- **Novo elo documental `NARA-BB-CONDE-20261112-01`:** a referência literal a **O Globo (8/11/1963)** cria um alvo verificável anterior ou contemporâneo à Tupi, sem estabelecer a ordem de publicação. A prioridade é recuperar a página original com edição, data, caderno, página e crédito/teletipo.

**Status dos efeitos:** precisão da custódia documental **aumentou** (3 fac-símiles primários e localização NARA fechada), hipótese de genealogia editorial **refinada**, histórico físico/orbital e provas Lean **inalterados**. A classe `HOAX` não substitui investigação sobre a verdade material.

## Limites técnicos e próximo experimento

- A imagem `0811.jp2` produziu erro de *decoder* JPEG 2000 em uma visualização estrita reduzida; a visualização com tolerância de fluxo truncado em outro nível de redução tornou o corpo legível. Isso **não comprova que o arquivo NARA está truncado**. Hash, tamanho e cabeçalho correspondem ao inventário; grafias manuais e caracteres rasurados devem permanecer sujeitos a dupla conferência. Não foi feita transcrição OCR automática.
- Os carimbos `UNCLASSIFIED` e hora de recepção nos fac-símiles não devem ser confundidos com data/hora do alegado evento (8/11). A contagem de três arquivos é de **objetos digitais da mesma unidade**, não de três testemunhos.
- Recuperar **O Globo de 8/11/1963** em fac-símile e conferir crédito, caderno, edição, página, menção a Salvador e se antecede ou segue a transmissão Tupi. Repasse à 🦉 Coruja; à 🐙 Polvo, indicar **nova ocorrência de documento no grafo, com aresta de dependência provável**, sem mudança de domínio físico.

### Reprodução independente

No terminal com acesso público e Python 3, baixar o JSON oficial, conferir SHA-256, localizar a unidade com `naId=302531012` e verificar `digitalObjects`. Para cada JP2 usar o endereço literal da tabela e calcular `sha256sum`; inspeção visual requer decodificador JPEG 2000 (Pillow compilado com OpenJPEG, por exemplo). Não redistribuir interpretações OCR como se fossem os fac-símiles. Nenhuma correspondência ou pedido foi enviado a arquivo/pessoa e o blog não foi modificado.
