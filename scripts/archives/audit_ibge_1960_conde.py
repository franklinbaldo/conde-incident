#!/usr/bin/env python3
"""Audit official IBGE 1960 retrospective municipal mesh, without claiming a 1963 legal boundary.

No dependency other than Python stdlib. This deliberately does not reproject,
convert to RFC 7946 GeoJSON, or export a 1963 polygon. ZIP remains at source.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import struct
import zipfile

URL = ("https://geoftp.ibge.gov.br/organizacao_do_territorio/"
       "estrutura_territorial/evolucao_da_divisao_territorial_do_brasil/"
       "evolucao_da_divisao_territorial_do_brasil_1872_2010/"
       "municipios_1872_1991/divisao_territorial_1872_1991/1960/"
       "05_malha_municipal_1960.zip")
ZIP_SHA = "261399b8557ee26c118e94b13cebf3b6b3e1c70e91b5e8438a348847b875120f"
SHAPE_SHA = "6258845cd887418a078fb507dda4b462dc12b44145f929775199cc80f5681b65"
DBF_SHA = "9487b8851864b5a66edcf49290dfff0e208a7aea649364f30d0b6bd22619fea2"
NAME = "05-malha municipal 1960"
COUNT = 2766
CODE = "2908606"
INDEX = 2448
CRS = "World_Polyconic, GCS_SIRGAS_2000, central meridian -54, meters"
FIELDS = (("codigo", "N", 7), ("nome", "C", 100))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_dbf(dbf: bytes) -> tuple[int, bytes]:
    if digest(dbf) != DBF_SHA:
        raise ValueError("DBF hash mismatch")
    if len(dbf) < 97:
        raise ValueError("truncated DBF")
    n, header_len, rec_len = struct.unpack_from("<IHH", dbf, 4)
    if (n, header_len, rec_len) != (COUNT, 97, 108):
        raise ValueError("DBF length/record-count mismatch")
    if len(dbf) < header_len+n*rec_len:
        raise ValueError("DBF truncated records")
    for i, (field, typ, width) in enumerate(FIELDS):
        offset = 32+32*i
        entry = dbf[offset:offset+32]
        if (entry[:11].split(b"\0")[0].decode("ascii"),chr(entry[11]),entry[16]) != (field,typ,width):
            raise ValueError("DBF schema mismatch")
    if dbf[96] != 0x0d:
        raise ValueError("DBF field delimiter mismatch")
    found = []
    for i in range(n):
        r = dbf[header_len+i*rec_len:header_len+(i+1)*rec_len]
        if r[0] != 0x20:
            continue
        if r[1:8].decode("ascii").strip() == CODE:
            found.append((i, r))
    if len(found) != 1:
        raise ValueError("ambiguous or absent IBGE code 2908606")
    idx, record = found[0]
    if idx != INDEX or record[8:108].decode("latin-1").strip() != "Conde":
        raise ValueError("wrong Conde attribute row")
    return idx, record


def parse_record(record: bytes) -> dict:
    if digest(record) != SHAPE_SHA:
        raise ValueError("Conde SHP record hash mismatch")
    if len(record) < 52:
        raise ValueError("truncated polygon record")
    ordinal, content_words = struct.unpack_from(">II",record,0)
    if ordinal != INDEX+1 or len(record) != 8+content_words*2:
        raise ValueError("SHP index ordinal or record length mismatch")
    shape_type = struct.unpack_from("<I",record,8)[0]
    if shape_type != 5:
        raise ValueError("expected Polygon SHP type 5")
    bbox = list(struct.unpack_from("<dddd",record,12))
    parts, points = struct.unpack_from("<II",record,44)
    if (parts,points)!=(1,47):
        raise ValueError("unexpected polygon topology")
    if len(record)!=52+4*parts+16*points:
        raise ValueError("SHP coordinate payload length mismatch")
    starts = struct.unpack_from("<"+"I"*parts,record,52)
    if starts!=(0,):
        raise ValueError("unexpected part offsets")
    xy=[struct.unpack_from("<dd",record,52+4*parts+16*i) for i in range(points)]
    if xy[0]!=xy[-1] or not all(bbox[0]<=x<=bbox[2] and bbox[1]<=y<=bbox[3] for x,y in xy):
        raise ValueError("open polygon or invalid bounds")
    if any(not (-1e8<x<1e8 and -1e8<y<1e8) for x,y in xy):
        raise ValueError("impossible coordinates")
    # Diagnostic only: planar shoelace in meter-based *reconstruction* CRS,
    # not a legal 1963 area, a geodetic area or an observed surface.
    area=abs(sum(xy[i][0]*xy[i+1][1]-xy[i+1][0]*xy[i][1]
                 for i in range(points-1)))/2e6
    return {
        "shapefile_record_1based": ordinal,
        "dbf_record_index_0based": INDEX,
        "record_bytes": len(record),
        "record_sha256": digest(record),
        "shape_type": shape_type,
        "part_count": parts,
        "vertex_count_including_closure": points,
        "ring_closed": True,
        "projected_bbox_m": bbox,
        "planar_shoelace_area_km2_diagnostic_only": round(area,6),
    }


def parse_archive(data: bytes) -> dict:
    if digest(data)!=ZIP_SHA:
        raise ValueError("IBGE ZIP checksum mismatch")
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        file_names=z.namelist()
        if len(file_names)!=7 or len(set(file_names))!=len(file_names):
            raise ValueError("unexpected ZIP inventory")
        for ext in (".shp",".shx",".dbf",".prj",".shp.xml",".sbn",".sbx"):
            if NAME+ext not in file_names:
                raise ValueError("missing component "+ext)
        shp=z.read(NAME+".shp")
        shx=z.read(NAME+".shx")
        dbf=z.read(NAME+".dbf")
        prj=z.read(NAME+".prj").decode("ascii")
        xml=z.read(NAME+".shp.xml").decode("utf-8")
        if "GCS_SIRGAS_2000" not in prj or "World_Polyconic" not in prj or "Central_Meridian\",-54" not in prj:
            raise ValueError("unexpected CRS")
        if "20130410" not in xml or "20130319" not in xml:
            raise ValueError("missing 2013 ArcGIS provenance")
        idx,dbf_rec=parse_dbf(dbf)
        shx_count=(len(shx)-100)//8
        if (len(shx)-100)%8 or shx_count!=COUNT:
            raise ValueError("SHX index count mismatch")
        off,words=struct.unpack_from(">II",shx,100+idx*8)
        rec=shp[off*2:off*2+8+words*2]
        if len(rec)!=8+words*2:
            raise ValueError("SHP record truncated")
        shape=parse_record(rec)
        return {
          "source_zip_sha256":digest(data),
          "source_zip_bytes":len(data),
          "source_components":{name:{"bytes":z.getinfo(name).file_size,
                                     "sha256":digest(z.read(name))}
                               for name in sorted(file_names)},
          "dbf_total_records":COUNT,
          "municipality_code":CODE,
          "municipality_name":dbf_rec[8:108].decode("latin-1").strip(),
          "dbf_record_sha256":digest(dbf_rec),
          "crs_wkt":prj,
          "shp_record_base64":base64.b64encode(rec).decode("ascii"),
          **shape,
        }



def validate_manifest(report: dict, real_record: bytes) -> None:
    """Offline validation against original 808-byte SHP record."""
    source=report["source"]
    binary=source["binary"]
    limits=report["method_and_limits"]
    if (report["record_id"]!="CGEO-10" or
        binary["source_zip_sha256"]!=ZIP_SHA or binary["source_zip_bytes"]!=2222445 or
        binary["dbf_total_records"]!=COUNT or binary["municipality_code"]!=CODE or
        binary["municipality_name"]!="Conde"):
        raise ValueError("source catalog identity mismatch")
    if (binary["record_sha256"]!=SHAPE_SHA or
        binary["record_bytes"]!=len(real_record) or
        binary["dbf_record_index_0based"]!=INDEX):
        raise ValueError("archival record identity mismatch")
    exact=parse_record(real_record)
    for key,expected in exact.items():
        if binary.get(key)!=expected:
            raise ValueError("source geometry mismatch: "+key)
    if (limits["admissible_historical_boundary_1963"] is not False or
        limits["orbital_constraint_activated"] is not False or
        limits["source_legal_boundary_1963"] is not None or
        limits["horizontal_accuracy_m"] is not None or
        limits["verified_intervening_legal_changes_1960_1963"] is not False or
        limits["geographic_status"]!="RETROSPECTIVE_COARSE_PROXY_ONLY"):
        raise ValueError("unjustified 1963 historical certainty")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("zip",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    d=parse_archive(args.zip.read_bytes())
    if args.out:
        args.out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    else:
        print(json.dumps(d,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
