"""Audit archival NOAA/GHCNd precipitation around Conde, Nov 7–9 1963.

The original .dly, station list, inventory and readme must be retrieved
and their *complete bytes* checked.  This is not a wind/trajectory model.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
REFERENCE = (-11.8641854035, -37.68935144749995)  # IBGE 2022 bbox midpoint, NOT fall position
SHA = {
    "ghcnd-stations.txt": "437ee87f0343bcad408a492cf7a02163fb69255364c541b4006d5d76055d0dc3",
    "ghcnd-inventory.txt": "3d7378c3ecad6841340b47392f10b391c42a5f47369765e6bb032704d2301125",
    "readme.txt": "0e4e6f0e6947cf1add884c328a01760f31c56ef5fb86b85ed57dd5dc4c4aeaa6",
    "BR048346820.dly": "f99557d7cb4187ea412b85b205ad2b04bf7449c0b89d27d4f546f75cbc717d53",
    "BR048345380.dly": "db6b41b580b10728366eda6b95f02a178fa700d8fb3b180b72b44eaeec7bc62e",
    "BR048441550.dly": "199e2d779d89bd7609a22ad25d7676117d95a71dcdb39cbb3492f9ac30f9e368",
    "BR048345130.dly": "1107f12859308f555b1fea9a22dac13c401e9b79e8720e22dca861842d2964b2",
    "BR048345070.dly": "071bcec32e1d365ef33b7d5c26caf4c10f5dfd0b3e41dad456f3da4dd2332f59",
    "BR001137041.dly": "eb531edda42ca95a385efea419a526d59c34121d7cbf93f95543cf38dcdfbc12",
    "BR048338870.dly": "a2951b0dc895d4a034b355aae4ca98cf19f38c175974557740acbf097247b183",
    "BR048340980.dly": "841a054af83f0b9c005744b96dfc4d0d66e8ceb55f836f9a1499bfbec0e4fa31",
    "BR001237001.dly": "aa788f7bc9697cbd9b488a904fd9f96e82a444f0f21a75fcd165373baaab9e6d",
    "BR048249490.dly": "07ff6fbcc7b6b3b967d95b58b17cd0759578747dec8664d904e54bac2752c0e8",
    "BR048158910.dly": "327a5c3f0f326a36214d7c2d37e9ecee82f676f8a6bf6e14056d82fe88673d03",
}
IDS = tuple(name[:-4] for name in SHA if name.endswith(".dly"))
DAYS = (7, 8, 9)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def checked_bytes(root, name):
    if not (root / name).is_file():
        raise ValueError("missing complete source: " + name)
    data = (root / name).read_bytes()
    if sha256(data) != SHA[name]:
        raise ValueError("source digest mismatch: " + name)
    return data


def haversine(lat, lon):
    a,b,c,d = map(math.radians, (*REFERENCE,lat,lon))
    h = math.sin((c-a)/2)**2 + math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return round(2*6371*math.asin(math.sqrt(h)), 1)


def read_station_inventory(root):
    stations={}
    for line in checked_bytes(root, "ghcnd-stations.txt").decode("ascii").splitlines():
        key=line[:11]
        if key in IDS:
            if key in stations: raise ValueError("duplicate station listing")
            stations[key] = {"name":line[41:71].strip(),"latitude":float(line[12:20]),"longitude":float(line[21:30])}
    inventory={}
    for line in checked_bytes(root, "ghcnd-inventory.txt").decode("ascii").splitlines():
        key=line[:11]
        if key in IDS and line[31:35]=="PRCP":
            if key in inventory: raise ValueError("duplicate precipitation inventory")
            inventory[key]=[int(line[36:40]),int(line[41:45])]
    if set(stations)!=set(IDS) or set(inventory)!=set(IDS):
        raise ValueError("station or PRCP inventory incomplete")
    for k in IDS:
        if not (inventory[k][0] <= 1963 <= inventory[k][1]):
            raise ValueError("1963 outside retrospective year bounds")
    return stations,inventory


def parse_november(data, station_id):
    records=[line for line in data.decode("ascii").splitlines() if line[11:17]=="196311" and line[17:21]=="PRCP"]
    if len(records)!=1: raise ValueError("expected exactly one Nov/1963 PRCP record for "+station_id)
    row=records[0]
    if len(row)!=269 or row[:11]!=station_id: raise ValueError("bad source layout / station")
    observations=[]
    for day in DAYS:
        raw=row[21+(day-1)*8:21+day*8]
        val=int(raw[:5]);m,q,s=raw[5:]
        if val==-9999 or q.strip() or not s.strip():
            raise ValueError("absent or flagged source value: "+station_id+" day "+str(day))
        if val<0: raise ValueError("negative daily precipitation")
        observations.append({"date":f"1963-11-{day:02d}","raw_eight_chars":raw,"precipitation_mm":val/10,"measurement_flag":m.strip() or None,"quality_flag":q.strip() or None,"source_flag":s})
    return observations


def audit(root):
    doc=checked_bytes(root,"readme.txt").decode("utf-8")
    if "I     = International collection" not in doc or 'PRCP' not in doc:
        raise ValueError("source-flag / PRCP documentation missing")
    stations, inventory=read_station_inventory(root)
    out=[]
    for key in IDS:
        rec=stations[key]
        observations=parse_november(checked_bytes(root,key+".dly"),key)
        if any(x["source_flag"]!="I" for x in observations):
            raise ValueError("unexpected GHCNd source lineage; review before using")
        out.append({"id":key,"station":rec["name"],"coordinate_lat_lon":[rec["latitude"],rec["longitude"]],"approx_distance_to_modern_bbox_midpoint_km":haversine(rec["latitude"],rec["longitude"]),"catalogue_prcp_year_bounds":inventory[key],"whole_file_sha256":SHA[key+".dly"],"archive_url":ARCHIVE+"all/"+key+".dly","daily":observations})
    out.sort(key=lambda x:x["approx_distance_to_modern_bbox_midpoint_km"])
    return {
        "schema":"conde.ghcnd-conde-precipitation-1963/v1",
        "id":"MET-GHCND-CONDE-19631107-09-01",
        "capture_utc_date":"2026-11-13",
        "observed_variable":"archival daily precipitation PRCP in tenths-mm; not hourly wind",
        "archival_family":"NOAA/NCEI GHCN-Daily; NOT NOAA/ISD Caravelas",
        "source_flag_I_meaning":"international collection (non-U.S. data via personal contacts); historical collector and instrument not identified",
        "source_document_urls":[ARCHIVE+"readme.txt",ARCHIVE+"ghcnd-stations.txt",ARCHIVE+"ghcnd-inventory.txt"],
        "full_source_sha256":{k:SHA[k] for k in ("readme.txt","ghcnd-stations.txt","ghcnd-inventory.txt")},
        "reference":{"kind":"modern IBGE 2022 municipality bbox midpoint, not 1963 incident site","lat_lon":list(REFERENCE),"distance_method":"haversine spherical radius 6371km"},
        "days":[f"1963-11-{d:02d}" for d in DAYS],
        "stations":out,
        "not_proved":{"observation_time_within_day":None,"historical_instrument_and_collecting_agency":None,"1963_station_coordinates_verified":None,"station_observation_independence":None,"rainfall_at_incident_site":None,"contemporary_wind_in_conde":None,"atmospheric_transfer_to_orbital_object":None,"calibrated_uncertainty":None,"active_fall_constraint":None},
        "status":"CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION"
    }


def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    obj=audit(a.source_dir)
    expected=ROOT/'research/meteorology/ghcnd_conde_precip_19631107_09.json'
    rendered=json.dumps(obj,indent=2,ensure_ascii=False)+'\n'
    if a.check:
        if expected.read_text()!=rendered: raise SystemExit("manifest differs from original GHCNd bytes")
        print('GHCNd audit PASS: 11 source-pinned stations, 33 daily values, nine non-inferences')
    else:
        expected.write_text(rendered)
        print('generated',expected)

if __name__=='__main__':main()
