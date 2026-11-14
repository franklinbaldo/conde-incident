#!/usr/bin/env python3
"""CGEO-48: screen-space candidate ONLY, deliberately not a historical geocode."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'research/geo/cgeo48_nara_00248_conde_candidate.json'
PARENT = ROOT / 'research/geo/cgeo47_nara_m1765_conde_pre1963.json'
EXPECTED = {
    'm1765-317-00246.jpg': ('902ce5bb15f6b40ddeecd793ec6407d3728a880e91cfd0d455519bdddbd33dda', (3636,4002),'base_map'),
    'm1765-317-00248.jpg': ('21016e6c141d5ac495893e13bc9a4b01bbf992e596416054fd0c03c164f3d2a0', (3620,3988),'flight_overlay'),
}
PREFIX = 'https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def distance_point_segment(point, segment):
    (px,py),(ax,ay),(bx,by) = point,*segment
    dx,dy=bx-ax,by-ay
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))

def validate(d,parent=None):
    require((d.get('schema'),d.get('id'),d.get('parent_evidence'))==('conde.cgeo.nara-overlay-screen-registration/v1','CGEO-48','CGEO-47'),'wrong provenance')
    require((d['record_group'],d['nara_degree_square'],d['nara_file_unit'])==('373','11S037W','46716637'),'wrong NARA unit')
    require(d['preview_dimensions_px']==[1080,1200] and 'not GIS georeferencing' in d['inspection_method'],'spatial claim exceeds method')
    require(len(d['reference_scans'])==2 and {o['filename'] for o in d['reference_scans']}==set(EXPECTED),'wrong scan set')
    for o in d['reference_scans']:
        sha,size,role=EXPECTED[o['filename']]
        require((o['sha256'],tuple(o['native_size_px']),o['role'])==(sha,size,role),'source scan drift')
        require(re.fullmatch('[a-f0-9]{64}',o['sha256']),'invalid hash')
    controls=d['paper_registration_controls_px']
    require(controls['control_max_displacement_px']==6,'loosened screening threshold')
    for a,b in [('base_upper_left','overlay_upper_left'),('base_lower_right','overlay_lower_right')]:
        x,y=controls[a],controls[b]
        require(len(x)==len(y)==2 and max(abs(x[i]-y[i]) for i in (0,1))<=6,'registration mismatch')
    label=d['map_label']
    require(label['literal']=='Conde' and label['kind']=='cartographic_toponym_not_1963_urban_centroid','false urban geocode')
    x,y=label['approximate_symbol_center_px']
    require(0<=x<1080 and 0<=y<1200,'symbol outside scan')
    ov=d['overlay_00248']; ann=ov['visible_annotations']
    require(ann['exposure_numbers_near_candidate_strip']==[26,16],'exposure numbers altered')
    require(ann['header_date_transcription']=='7,11,18,20 SEP 42' and ann['header_date_reading']=='provisional_visual_transcription','provisional date improperly promoted')
    require(ann['unresolved_header_number']=='125374' and ann['unresolved_header_number_is_spot_number'] is None,'spot number invented')
    line=ov['candidate_strip_proxy_line_preview_px']
    require(len(line)==2 and all(len(p)==2 and all(isinstance(q,int) for q in p) for p in line),'malformed segment')
    require(ov['proximity_threshold_px_for_visual_screening_only']==25,'threshold changed')
    dist=distance_point_segment((x,y),line)
    require(dist<=25 and ov['town_symbol_is_near_strip_on_registered_preview'] is True,'screen proximity not demonstrated')
    for key in ('verified_aerial_exposure_at_town','verified_original_negative'):
        require(ov[key] is False,'negatives/footprints falsely claimed')
    for key in ('verified_spot_number','verified_exposure_date'):
        require(ov[key] is None,'missing primary photo metadata invented')
    limits=d['limitations']
    require(limits['source_jpegs_acquired_and_hashed_in_cgeo47'] is True,'missing acquisition lineage')
    for key in ('modern_geodetic_coordinates_derived','georeferenced_footprint_validated','orbital_constraints_activated'):
        require(limits[key] is False,'evidence promoted prematurely')
    for key in ('historical_center_polygon_1963','same_flight_as_sgb_1964_1970','reentry_event_location'):
        require(limits[key] is None,'invalid inferential bridge')
    require(limits['final_status']=='CANDIDATE_VISUAL_CORRIDOR_ONLY','false verification state')
    if parent is not None:
        require(parent['id']=='CGEO-47','parent is not CGEO-47')
        unit=next(u for u in parent['units'] if u['degree_square']=='11S037W')
        for o in d['reference_scans']:
            source=next(s for s in unit['images'] if s['filename']==o['filename'])
            require(source['sha256']==o['sha256'],'parent scan hash differs')
    return round(dist,2)

def read(path=PATH):
    return json.loads(Path(path).read_text(encoding='utf8'))

def validate_live(d, folder=None):
    """Live/cached byte verification; never substitutes an offline PASS."""
    unit=next(u for u in read(PARENT)['units'] if u['degree_square']=='11S037W')
    for o in d['reference_scans']:
        source=next(s for s in unit['images'] if s['filename']==o['filename'])
        if folder:
            raw=(Path(folder)/('11S037W_'+o['filename'])).read_bytes()
        else:
            with urlopen(Request(PREFIX+o['filename'],headers={'User-Agent':'Conde-CGEO48/1.0'}),timeout=50) as response:
                require(response.status==200,'remote source non-200')
                raw=response.read()
        require(len(raw)==source['bytes'] and hashlib.sha256(raw).hexdigest()==o['sha256'],'source bytes drift')
        require(raw[:3]==b'\xff\xd8\xff' and raw[-2:]==b'\xff\xd9','incomplete JPEG')
    return 2

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--live',action='store_true'); ap.add_argument('--cached-directory')
    args=ap.parse_args()
    d=read(); parent=read(PARENT)
    print('CGEO48_SCREEN_CANDIDATE_PASS',validate(d,parent),'pixels (not ground distance)')
    if args.live or args.cached_directory:
        print('CGEO48_SOURCE_BYTES_PASS',validate_live(d,args.cached_directory))
if __name__=='__main__': main()
