---
type: Guide
title: "C241-R65: relatório polonês de 1964 descreve serviço observacional em 1963"
description: "Fac-símile de 1964 confirma mais de 25 mil observações acumuladas até 1963, 10–12 estações e códigos COSPAR 1151–1162, sem individualizar NORAD 527–529."
---

# C241-LONTRA-R65 · relatório contemporâneo do serviço polonês

**Fonte primária quanto ao serviço, não quanto à trajetória do 528:** L. Cichowicz e W. Zonn, *Udział Polski w badaniach przestrzeni kosmicznej*, **Postępy Astronomii**, XII(3), Varsóvia, julho–setembro de **1964**. [Fac-símile institucional](https://www.urania.edu.pl/pliki/archiwum/postepy_astronomii_1964_03.pdf#page=30). PDF **página 30 / impressa 190**, continuidade **página 31 / impressa 191**. As duas páginas foram conferidas visualmente, sem atribuir OCR isolado ao original.

O parágrafo **Obserwacje sztucznych satelitów** relata serviço iniciado no outono de 1957, cerca de **10 estações observacionais**, **12 em 1964**, e **mais de 25 mil observações posicionais acumuladas até o fim de 1963**, de dezenas de satélites **soviéticos e americanos**, por técnicas visuais, fotográficas e rádio. Identifica **números COSPAR 1151–1162**, coordenação com Moscou e cooperação internacional. Na página 191 há menção a observações síncronas de **Echo 1** em programa iniciado em 1963. Não se atribui Echo 1 a NORAD 527/528/529.

**Custódia verificável:** download integral no executor Ifro, **4.882.674 bytes, 62 páginas, PDF 1.6**, SHA-256 `0664d3134c15e999a67158c1dfd013a49e435fc00dbe86c78fc2b2452b526c94`, em 14/11/2026. Páginas 30–31 verificadas também por renderização visual do PDF, que incluem paginação impressa 190–191. O checksum pertence à cópia integral, não à passagem textual nem aos registros primários de 1963.

**Limite essencial:** as **25 mil** são uma contagem **agregada multianual, multialvo e multiestação**, não medições de um objeto, nem 25 mil pontos em 1963, nem 25 mil observações independentes. O intervalo 1151–1162 é **identificador de estações**, não catálogo NORAD. Nenhuma linha observacional, época, RA/Dec, instrumento/calibração ou NORAD 527/528/529 foi recuperado desta fonte. **Novas restrições orbitais: zero.**

**Próximo passo falsificável:** usar os IDs de estações para buscar registros originais de 1963, periódicos e circulares polonesas; exigir designação do alvo, instante, estação e medida antes de passar dados à Tartaruga/Polvo. Não confundir este periódico de 1964 com *Наблюдения ИСЗ* n. 2 (Varsóvia 1963) ou *Бюллетень* n. 32 (1963), ainda não recuperados. Nenhuma instituição foi contatada.

Auditoria: `python3 -m tools.audit_polish_observation_service_r65`, testes `python3 -m unittest discover -s tests -p test_polish_observation_service_r65.py -v` (também com `python3 -O`). Gates `prek`, CI e testes negativos no HEAD final permanecem obrigatórios. Contexto: [Conde #545](https://github.com/franklinbaldo/conde-incident/issues/545), [Cafezinho #9](https://github.com/franklinbaldo/cafezinho/issues/9).
