---
type: Guide
title: "CGEO-21: cronologia das travessias do Itapicuru entre Centro e Vila"
description: "Separação temporal de passarela, proposta de ponte, obra e relato de ponte nova, sem geocódigo de 1963"
---

# CGEO-21: uma passarela de 2014 não é automaticamente a ponte de 2024

O [blog local de 26/03/2014](https://condebahia.wordpress.com/2014/03/26/) chama de *passarela* a ligação de Conde à Vila sobre o Rio Itapicuru. A publicação demonstra a **atribuição editorial em 2014**, não a data de construção da estrutura, seu tipo exato, sua posição medida ou sua existência em 1963. É a mesma família documental BLOG14 usada em CGEO-20, **não** um novo testemunho.

Em 06/02/2015 a [Assembleia Legislativa da Bahia, IND/20.904/2015](https://www.al.ba.gov.br/atividade-legislativa/proposicao/IND-20.904-2015), registrou uma **indicação para construir uma ponte** sobre o Rio Itapicuru em Conde. A tramitação consta em índice oficial, mas o texto integral da indicação não foi adquirido. Uma proposta para construir uma ponte em 2015 **não prova** que não havia qualquer travessia anterior.

O [PNCP, controle 14126692000123-1-000022/2024](https://pncp.gov.br/app/editais/14126692000123/2024/22), reproduzido com link à fonte por [registro de licitação](https://licitapncp.com.br/licitacao/licitanet-contratacao-de-empresa-especializada-em-engenharia-para-a-14126692000123-1-000022-2024), publicou em 29/05/2024 contratação para **complemento da ponte de concreto** sobre o rio, localizada no *Centro* do município. Isso comprova a descrição da contratação, não a data inicial de obra nem a conclusão física.

[Notícia de 29/12/2024](https://www.politicalivre.com.br/2024/$12/prefeitura-do-conde-inaugura-ponte-afrisio-vieira-lima-nesta-segunda-30) anuncia inauguração no dia 30/12 da ponte Afrísio Vieira Lima, entre sede e Vila. Anúncio futuro não é ata ou fotografia autenticada da inauguração efetiva. Em [16/07/2025](https://conde.portaldacidade.com/noticias/achados-e-perdidos/chaves-sao-encontradas-em-ponte-que-liga-centro-e-vila-1939), reportagem local refere-se à *nova ponte* que conecta Centro e comunidade de Vila do Conde. São fontes editoriais separadas, mas nenhuma é medição geodésica.

## Consequência cartográfica

Há **dois candidatos de infraestrutura**: passarela descrita em 2014 e ponte de concreto descrita em 2024/2025. Identidade física entre eles **não demonstrada**. Há uma conexão espacial nomeada Centro–Vila no discurso documental recente, conectada a CGEO-20; a referência à travessia do Itapicuru acrescenta uma relação topológica *contemporânea*, não um polígono de 1963. Mesmo a notícia posterior de ponte nova não localiza a frase inglesa do FBIS/Tupi de 1963 (*center of the city*). Não se pode concluir a margem do rio, ponto de impacto ou que a passarela/ponte existia ou inexistia em 1963. A fotografia de 1958 e as imagens alegadas de 1959 continuam fontes visuais distintas (CGEO-17/19).

O [manifesto JSON](cgeo21_itapicuru_crossings_2014_2025.json) contém a cronologia, URLs originais, linhagens e variáveis latentes para o grafo cumulativo. **Delta:** cinco ocorrências de quatro linhagens novas mais a família BLOG14 já existente; duas entidades candidatas de travessia; arestas a CGEO-17/18/19/20. O status é `CONNECTED_PENDING_HISTORICAL_SPATIAL_BRIDGE`, e não ocorreu contração admissível do domínio orbital.

**Replay offline:** `python3 -m tools.cgeo21_itapicuru_crossings` e `python3 -m unittest tests.test_cgeo21_itapicuru_crossings -v`. Os testes adversariais rejeitam data retroprojetada, fusão de ativos, conclusão de obra por anúncio e geometrias arbitrárias.

**Pendente:** planta ou levantamento urbano de 1950–1963 que identifique as duas margens, eventual travessia com data de construção, e a transcrição portuguesa original da Rádio Tupi. Nenhuma imagem, datum, hash de PDF ou coordenada de 1963 foi inventado.
