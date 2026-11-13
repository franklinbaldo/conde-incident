"""CGEO-34: verify archival JP2 bytes and boundaries of historical claims."""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'research/geo/cgeo34_uwm_original_jp2_custody.json'

def read(path: Path)->dict:
    return json.loads(path.read_text(encoding='utf-8'))

def boxes(source: Path)->tuple[list[str],dict]:
    """Parse JP2 top-level boxes with bounded memory; read ihdr, never decode raster."""
    size=source.stat().st_size
    names=[]; identity={}; offset=0
    with source.open('rb') as fp:
        while offset<size:
            fp.seek(offset)
            hdr=fp.read(8)
            if len(hdr)!=8:raise ValueError('truncated JP2 box header')
            n,t=struct.unpack('>I4s',hdr)
            head=8
            if n==1:
                ext=fp.read(8)
                if len(ext)!=8:raise ValueError('truncated extended header')
                n=struct.unpack('>Q',ext)[0];head=16
            if n==0:n=size-offset
            if n<head or offset+n>size:raise ValueError('malformed JP2 box size')
            names.append(t.decode('latin1'))
            if t==b'jp2h':
                inner=offset+head
                while inner<offset+n:
                    fp.seek(inner);h=fp.read(8)
                    if len(h)!=8:raise ValueError('truncated jp2h inner box')
                    length,kind=struct.unpack('>I4s',h)
                    if length<8 or inner+length>offset+n:raise ValueError('malformed jp2h subbox')
                    if kind==b'ihdr':
                        if length!=22 or identity:raise ValueError('noncanonical ihdr')
                        payload=fp.read(14)
                        if len(payload)!=14:raise ValueError('truncated ihdr')
                        height,width,components,bpc,codec,unk,ipr=struct.unpack('>IIHBBBB',payload)
                        identity={'width_px':width,'height_px':height,'components':components,
                                  'bits_per_component':bpc+1,'compression':codec}
                    inner+=length
            offset+=n
    if offset!=size:raise ValueError('unparsed JP2 trailing data')
    return names,identity

def verify_manifest(d:dict, parent:dict, header:bytes)->str:
    a=d['asset'];lim=d['scientific_limits']
    if (d['id'],d['parent_occurrence'],parent['occurrence_id']) != (
            'CGEO-34','ARCH-UWM-ARACAJU-SE-10814-20261112','ARCH-UWM-ARACAJU-SE-10814-20261112'):
        raise ValueError('wrong parent')
    if d['parent_file']!='research/geo/uwm_aracaju_se_1954_1961_cartographic_custody.json':
        raise ValueError('wrong parent file')
    if parent['object']['contentdm_item_id']!=a['contentdm_item_id'] or parent['object']['original_jp2_downloaded'] is not False:
        raise ValueError('not prior unresolved acquisition')
    expected={
      'bytes':110453331,'sha256':'6637246d2a68a2e7024e07829caa35a8af0a707905e6c606109f1da52ae808b3',
      'url':'https://collections.lib.uwm.edu/digital/api/collection/agdm/id/10814/download',
      'header_bytes':103,'header_sha256':'PLACEHOLDER',
      'width_px':9603,'height_px':7783,'components':3,'bits_per_component':8,
      'format':'JP2 / JPEG 2000 Part 1','response_mime':'image/jp2',
      'acquired_original_bitstream':True,'full_image_visual_inspection_performed':False,
      'source_survey_independent_of_parent':False}
    expected.pop('source_survey_independent_of_parent')
    expected['header_sha256']=hashlib.sha256(header).hexdigest()
    if any(a.get(k)!=v for k,v in expected.items()):raise ValueError('incorrect source metadata')
    if a['header_fixture']!='research/geo/evidence/cgeo34_uwm_jp2_header.hex' or len(header)!=103:
        raise ValueError('incorrect header fixture')
    if not header.startswith(bytes.fromhex('0000000c6a5020200d0a870a')) or not d['same_physical_map_as_parent']:
        raise ValueError('incorrect JP2 signature/independence')
    if a['jp2_box_sequence']!=['jP  ','ftyp','jp2h','xml ','jp2c']:
        raise ValueError('wrong JP2 boxes')
    if (parent['object']['iiif_width_px'],parent['object']['iiif_height_px'])!=(a['width_px'],a['height_px']):
        raise ValueError('wrong IIIF crosscheck')
    if (d['map_historical_readings']['catalog_year'],d['map_historical_readings']['communications_update_year'],
        d['map_historical_readings']['map_scale']) !=(1954,1961,500000):
        raise ValueError('anachronistic map date or scale')
    if {edge['to'] for edge in d['graph_edges']}!={'CGEO-08','CGEO-33','CGEO-18'}:
        raise ValueError('broken graph')
    if any(lim[k] is not None for k in ('municipal_boundary_1963','urban_center_geometry_1963',
            'observed_reentry_location','date_of_original_aerial_capture','georeferenced_control_points','horizontal_error_m')):
        raise ValueError('fabricated historical observation')
    if any(lim[k] is not False for k in ('can_constrain_orbital_reentry','known_1963_reentry_point',
            'source_survey_independent_of_parent','original_historical_physical_map_acquired')):
        raise ValueError('falsely promoted evidence')
    return 'CGEO34_JP2_HEADER_AND_CUSTODY_PASS'

def verify_original(path:Path,d:dict,header:bytes)->str:
    a=d['asset']
    if path.stat().st_size!=a['bytes']:raise ValueError('original size mismatch')
    digest=hashlib.sha256()
    with path.open('rb') as fp:
        if fp.read(len(header))!=header:raise ValueError('original source header mismatch')
        fp.seek(0)
        for part in iter(lambda: fp.read(1<<20),b''):digest.update(part)
    if digest.hexdigest()!=a['sha256']:raise ValueError('original SHA256 mismatch')
    names,identity=boxes(path)
    if names!=a['jp2_box_sequence'] or identity!={
        'width_px':9603,'height_px':7783,'components':3,'bits_per_component':8,'compression':7}:
        raise ValueError('original JP2 boxes or dimensions mismatch')
    return 'CGEO34_FULL_ORIGINAL_JP2_REPLAY_PASS'

def main()->None:
    p=argparse.ArgumentParser();p.add_argument('--original',type=Path)
    args=p.parse_args()
    d=read(MANIFEST)
    header=bytes.fromhex((ROOT/d['asset']['header_fixture']).read_text(encoding='ascii'))
    print(verify_manifest(d,read(ROOT/d['parent_file']),header))
    if args.original:print(verify_original(args.original,d,header))

if __name__=='__main__':main()
