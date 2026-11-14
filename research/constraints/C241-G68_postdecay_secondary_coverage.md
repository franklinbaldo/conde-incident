---
type: Guide
title: 'CASTOR-G68: controle temporal 527/529 após o dia de decaimento'
description: 'Audita cobertura dos TLEs secundários de 1963 em torno de 8/11 sem inventar hora, sensor ou restrição física.'
---

# G68: disponibilidade dos controles depois de 08/11/1963

**Pergunta operacional:** há épocas de catálogo secundário para NORAD **527/529** após o **dia** que a NASA registra como decaimento do **528**? A linha NASA C197 no *Satellite Situation Report* de 15/11/1963 só fornece o **dia 08/11/1963**, sem horário, estação ou local. O primeiro instante cuja data UTC é *inequivocamente posterior ao dia impresso* é **1963-11-09 00:00Z**. Um registro datado **durante 08/11** não pode ser ordenado antes/depois do decaimento real a partir daquela linha.

- Fonte NASA primária do **dia catalogado**, sem instante: [NTRS 19640001198](https://ntrs.nasa.gov/citations/19640001198); [PDF](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf). Registro C197, não uma medição óptica.
- Fonte dos elementos temporais: [espelho Parquet oxzoid/space-track-tle-history, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. CSV derivado por `tools/tle_secondary_1963_ledger.py`, SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. São épocas de **elementos médios catalográficos secundários**, sem recibos originais NORAD/SPADATS, erro de sensor, estação ou identificação de aquisição.
- Operador: `tools/cross_object_epoch_support.py` estende a auditoria SHA já existente com a janela pós-dia e colapso de duplicatas. Conta separadamente épocas **anteriores a 08/11**, **durante 08/11** e **desde 09/11**, com índices originais por linha, primeiro/último suporte e lacuna temporal observada no *catálogo*. Não interpola vetores nem aplica SGP4/J2/arrasto.
- Reexecução no CI já existente `.github/workflows/tle-cross-epoch-availability.yml`: controles adversariais, download, verificação SHA, ledger e artefato JSON por commit; sem novo workflow nem alteração de permissões. Testes locais também executados com `python -O`.

**Critério de interpretação:** a existência de dados catalográficos de 527/529 depois do dia de decaimento de 528 **não significa** que os três foram observados conjuntamente por um instrumento, nem que se mantiveram vizinhos. Não extrapolar uma separação observada, taxa orbital ou localização de reentrada de tais índices. A fonte inicial 528 de outubro e os controles 527/529 compartilham possível genealogia de rastreamento. Até obter registros independentes com estação/UTC/erro, `historical_holdout=NOT_RUN`, `physical_joint_fit=NOT_RUN` e **nenhuma restrição física nova** sobre a trajetória de 528.
