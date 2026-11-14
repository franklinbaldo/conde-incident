---
type: Guide
title: 'CASTOR-G57: custódia da transcrição óptica separada da fonte instrumental'
description: 'Compara o registro geométrico GCRS somente quando todos os campos da observação coincidem com bytes JSON de extração versionada; conserva o SHA do documento original de forma independente.'
---

# CASTOR-G57: autenticar a transcrição, não apenas a fonte citada

**Falha demonstrável:** antes do G57, `compare_geometric_gcrs` autenticava os bytes da fonte citada e o estado TEME, mas recebia ângulos, estação e covariância em um **objeto de entrada independente**. Era possível alterar `observed.right_ascension_deg` ou a covariância instrumental mantendo o SHA-256 original do suposto documento. Assim, um resíduo diferente podia ser apresentado como se tivesse a mesma origem documental. A falha diz respeito à **transcrição**, não prova qualquer adulteração histórica.

**Contrato:** além dos bytes da fonte primária/derivada e do registro TEME de G56, a função recebe `original_extraction_bytes` (quinto argumento), um JSON UTF-8 com exatamente `schema=GCRS_OPTICAL_EXTRACTION_V1`, `evidence_class` e `observation`. O último campo é o registro tipado inteiro usado pela comparação. É rejeitado se divergir da observação fornecida, inclusive em ângulo, covariância, estação, identidade, época, URI ou hash da fonte. Chaves duplicadas, `NaN`/`Infinity`, bytes vazios e classes não suportadas são rejeitados. A comparação publica `extraction_sha256_verified`, `extraction_evidence_class` e uma etiqueta que não confunde a integridade dessa extração com a autenticidade histórica do documento citado.

**Representação mínima sintética de reprodução:**

```json
{
  "schema": "GCRS_OPTICAL_EXTRACTION_V1",
  "evidence_class": "SYNTHETIC_SCENARIO",
  "observation": {
    "object_id": "SYNTHETIC_ONLY_NOT_528",
    "station_id": "WGS84_SCENARIO_ONLY",
    "document_uri": "urn:synthetic:g54:mathematical-fixture",
    "document_sha256": "<sha256-dos-bytes-reais-do-documento>",
    "frame": "GCRS",
    "angle_type": "INSTANTANEOUS_GEOMETRIC_NOT_APPARENT_FK4",
    "epoch_utc": "1963-11-08T12:00:00Z",
    "station_wgs84_geodetic": {"longitude_deg": 0.0, "latitude_deg": 0.0, "height_m": 0.0},
    "right_ascension_deg": 359.99,
    "declination_deg": 0.0,
    "instrument_covariance_basis": "PREDICTED_GCRS_TANGENT_EAST_NORTH",
    "instrument_covariance_arcsec2": [[4.0, 0.0], [0.0, 9.0]]
  }
}
```

O exemplo é **ilustrativo**: não possui digest válido calculado, nem reproduz uma observação histórica. A cadeia de transcrição pode começar num PDF/filme original; a extração JSON é outra fonte, cujos bytes e hash devem permanecer identificáveis. Nenhum programa pode presumir que os números da extração estão realmente impressos no documento: conferir a página, unidade, época, relógio, correções, referencial e calibração exige auditoria separada. Não se admite `PRIMARY_INSTRUMENT` sem ficha primária autenticada e transformação explícita; o contrato G57 **não atribui essa categoria**.

**Teste de falsificação:** manter fixos os bytes da fonte e do JSON de extração, modificar só RA, declinação, covariância ou estação na observação tipada; o operador deve rejeitar por divergência. Cobrem-se também chaves duplicadas, classe promovida indevidamente e extração vazia. Em CI, a suíte IERS original autenticada mantém `historical_holdout=NOT_RUN` e `impact_inference=NOT_SUPPORTED`, sem simular observações de 527/528/529.

**Limites não resolvidos:** a integridade do JSON é autorreferente se não houver captura independente; um adversário poderia alterar extração e registro juntos. SHA não fornece assinatura, autoria nem cadeia de custódia humana. A classe `SECONDARY_DERIVATIVE_NOT_INSTRUMENT` não se torna observação de sensor por ter hash. Nenhuma hora, coordenada ou probabilidade de impacto no Conde é inferida.
