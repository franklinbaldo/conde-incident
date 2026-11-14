"""CGEO-40: catalogue holding cannot be promoted to an image or event geometry."""
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/cgeo40_ahex_iocs15_holdings.json"

def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))

def validate_contract(c):
    if (c["schema"] != "conde.geo.iocs15-ahex-holdings/v1" or
        c["id"] != "CGEO-40" or c["previous_id"] != "CGEO-39"):
        raise ValueError("contract identity")
    a = c["source"]
    if (a["institution"] != "Arquivo Histórico do Exército (AHEx), Mapoteca" or
        a["url"] != "https://www.ahex.eb.mil.br/images/DDA/2023/Atendimento_ao_Publico/Catalogo_Mapoteca_Completo.pdf" or
        a["catalogue_generated_on"] != "2023-04-04" or
        a["catalogue_page_printed"] != 125 or a["catalogue_pages_declared"] != 196 or
        a["record_id"] != "05.36.334" or
        (a["module"], a["drawer"], a["map_number"]) != (5, 36, 334) or
        a["year_catalogued"] != 1912 or
        a["title_literal"] != "MAPA DA BACIA DO RIO ITAPICURÚ, ESTADO DA BAHIA" or
        a["dimensions_cm"] != [87, 67.5] or
        a["condition_catalogued"] != "bom estado"):
        raise ValueError("AHEx record or temporal attribution")
    if (a["source_kind"] != "CATALOGUE_RECORD" or
        a["verification_channel"] != "OFFICIAL_URL_INDEXED_TEXT" or
        a["transport_status"] != "TLS_CERT_EXPIRED_AND_HTTP_403_ON_BYPASS" or
        a["source_bytes_acquired"] is not False or
        a["facsimile_acquired"] is not False or a["source_sha256"] is not None):
        raise ValueError("unverified source promotion")
    p=c["comparison"]
    if (p["other_archive_reference"] != "BR AN,RIO F4.0.MAP.448" or
        p["other_archive_dimensions_cm"] != [64,89] or
        p["ibram_series"] != "BR RJMRAHI EP-IC-MA" or
        p["relation"] != "THIRD_CUSTODY_CATALOGUE_CANDIDATE_SAME_WORK"):
        raise ValueError("catalogue lineage")
    if any(p[key] is not False for key in (
        "copy_identity_verified","edition_identity_verified",
        "independent_topographic_survey_proven","dimensions_prove_distinct_edition")):
        raise ValueError("independence or identity invented")
    lim=c["limits"]
    if any(lim[key] is not None for key in (
        "original_map_image","spatial_coverage_1912","center_1963",
        "reported_fall","horizontal_uncertainty_m","flight_date")):
        raise ValueError("unproven historical geometry")
    if lim["can_constrain_orbital_reentry"] is not False:
        raise ValueError("unproven orbital constraint")
    return "CGEO40_AHEX_CATALOGUE_CONTRACT_PASS"

if __name__=="__main__":
    print(validate_contract(load_contract()))
