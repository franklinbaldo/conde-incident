#!/usr/bin/env python3
"""Authenticated Space-Track.org 1963 audit for NORAD 527, 528, 529, 637.

Reads SPACETRACK_IDENTITY and SPACETRACK_PASSWORD from environment variables
(never written to disk or stdout). Queries gp_history, satcat, and decay, then
summarizes epoch coverage and compares against the pinned oxzoid mirror.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request

BASE = 'https://www.space-track.org'
DEFAULT_IDS = '527,528,529,637'
OXZOID_LAST_528 = '1963-10-27T14:40:16'


def make_opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def login(opener: urllib.request.OpenerDirector, identity: str, password: str) -> None:
    payload = urllib.parse.urlencode({'identity': identity, 'password': password}).encode('utf-8')
    req = urllib.request.Request(f'{BASE}/ajaxauth/login', data=payload, method='POST')
    with opener.open(req, timeout=30) as resp:
        body = resp.read().decode('utf-8', errors='replace')
        if resp.status != 200 or 'Login Failed' in body or '"Login":"Failed"' in body:
            raise RuntimeError('Space-Track login failed (check SPACETRACK_IDENTITY / SPACETRACK_PASSWORD)')


def fetch_json(opener: urllib.request.OpenerDirector, path: str) -> tuple[list[dict], str]:
    req = urllib.request.Request(f'{BASE}{path}', method='GET')
    with opener.open(req, timeout=60) as resp:
        raw = resp.read()
    digest = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw.decode('utf-8'))
    if not isinstance(data, list):
        raise RuntimeError(f'Unexpected Space-Track response for {path}')
    return data, digest


def summarize_gp(rows: list[dict], norad_ids: list[int]) -> dict:
    by_id: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        nid = int(r['NORAD_CAT_ID'])
        by_id[nid].append(r)

    summary = {}
    for nid in norad_ids:
        recs = sorted(by_id.get(nid, []), key=lambda x: x.get('EPOCH', ''))
        epochs = [r.get('EPOCH', '') for r in recs]
        distinct_epochs = sorted(set(epochs))
        post_oct27 = [
            {
                'EPOCH': r.get('EPOCH'),
                'MEAN_MOTION': r.get('MEAN_MOTION'),
                'ECCENTRICITY': r.get('ECCENTRICITY'),
                'INCLINATION': r.get('INCLINATION'),
                'RA_OF_ASC_NODE': r.get('RA_OF_ASC_NODE'),
                'ARG_OF_PERICENTER': r.get('ARG_OF_PERICENTER'),
                'BSTAR': r.get('BSTAR'),
                'ELEMENT_SET_NO': r.get('ELEMENT_SET_NO'),
            }
            for r in recs
            if nid == 528 and (r.get('EPOCH') or '') > OXZOID_LAST_528
        ]
        summary[str(nid)] = {
            'total_rows': len(recs),
            'distinct_epochs': len(distinct_epochs),
            'first_epoch': distinct_epochs[0] if distinct_epochs else None,
            'last_epoch': distinct_epochs[-1] if distinct_epochs else None,
            'last_record_summary': (
                {
                    'EPOCH': recs[-1].get('EPOCH'),
                    'MEAN_MOTION': recs[-1].get('MEAN_MOTION'),
                    'ECCENTRICITY': recs[-1].get('ECCENTRICITY'),
                    'INCLINATION': recs[-1].get('INCLINATION'),
                    'RA_OF_ASC_NODE': recs[-1].get('RA_OF_ASC_NODE'),
                    'BSTAR': recs[-1].get('BSTAR'),
                    'TLE_LINE1': recs[-1].get('TLE_LINE1'),
                    'TLE_LINE2': recs[-1].get('TLE_LINE2'),
                }
                if recs else None
            ),
            'post_oct27_new_records': post_oct27 if nid == 528 else [],
        }
    return summary


def format_markdown(report: dict) -> str:
    lines = [
        '# Space-Track 1963 Official Audit Summary',
        '',
        f"- **Queried NORAD IDs:** `{report['norad_ids']}`",
        f"- **gp_history SHA-256:** `{report['sha256']['gp_history']}`",
        f"- **satcat SHA-256:** `{report['sha256']['satcat']}`",
        f"- **decay SHA-256:** `{report['sha256']['decay']}`",
        '',
        '## gp_history (1963)',
        '',
        '| NORAD | Rows | Distinct Epochs | First Epoch | Last Epoch | Post-Oct-27 (528)? |',
        '|---:|---:|---:|---|---|---:|',
    ]
    for nid, info in report['gp_summary'].items():
        new_n = len(info['post_oct27_new_records'])
        lines.append(
            f"| {nid} | {info['total_rows']} | {info['distinct_epochs']} | "
            f"`{info['first_epoch']}` | `{info['last_epoch']}` | {new_n} |"
        )

    lines.extend(['', '## satcat', ''])
    for r in report['satcat']:
        lines.append(
            f"- **NORAD {r.get('NORAD_CAT_ID')}** (`{r.get('INTLDES')}`, `{r.get('SATNAME')}`): "
            f"launch=`{r.get('LAUNCH')}`, decay=`{r.get('DECAY')}`, period=`{r.get('PERIOD')}`, "
            f"inc=`{r.get('INCLINATION')}`, rcs=`{r.get('RCS_SIZE')}`"
        )

    lines.extend(['', '## decay table', ''])
    if not report['decay']:
        lines.append('- *(0 rows returned in `class/decay`)*')
    else:
        for r in report['decay']:
            lines.append(
                f"- **NORAD {r.get('NORAD_CAT_ID')}**: decay_epoch=`{r.get('DECAY_EPOCH')}`, "
                f"source=`{r.get('SOURCE')}`, msg_epoch=`{r.get('MSG_EPOCH')}`, "
                f"precedence=`{r.get('PRECEDENCE')}`"
            )

    new_528 = report['gp_summary'].get('528', {}).get('post_oct27_new_records', [])
    if new_528:
        lines.extend(['', '## NEW NORAD 528 records after 1963-10-27T14:40:16!', ''])
        for r in new_528:
            lines.append(
                f"- `{r['EPOCH']}` | n=`{r['MEAN_MOTION']}` | e=`{r['ECCENTRICITY']}` | "
                f"i=`{r['INCLINATION']}` | RAAN=`{r['RA_OF_ASC_NODE']}` | B*=`{r['BSTAR']}`"
            )
    else:
        lines.extend([
            '',
            '## NORAD 528 post-Oct-27 check',
            '- **0 new epochs after `1963-10-27T14:40:16`** in official Space-Track `gp_history`.',
        ])
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit official Space-Track 1963 records.')
    parser.add_argument('--norad-ids', default=DEFAULT_IDS)
    parser.add_argument('--summary-json', type=Path, required=True)
    parser.add_argument('--summary-md', type=Path, required=True)
    args = parser.parse_args()

    identity = os.environ.get('SPACETRACK_IDENTITY', '').strip()
    password = os.environ.get('SPACETRACK_PASSWORD', '').strip()
    if not identity or not password:
        raise SystemExit('Missing SPACETRACK_IDENTITY or SPACETRACK_PASSWORD env vars')

    ids_list = [int(x.strip()) for x in args.norad_ids.split(',') if x.strip()]
    ids_csv = ','.join(str(x) for x in ids_list)

    opener = make_opener()
    login(opener, identity, password)

    gp_path = (
        f'/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{ids_csv}'
        f'/EPOCH/1963-01-01--1964-01-01/orderby/NORAD_CAT_ID%20asc,EPOCH%20asc/format/json'
    )
    gp_rows, gp_sha = fetch_json(opener, gp_path)
    time.sleep(2)
    satcat_rows, satcat_sha = fetch_json(
        opener, f'/basicspacedata/query/class/satcat/NORAD_CAT_ID/{ids_csv}/format/json'
    )
    time.sleep(2)
    decay_rows, decay_sha = fetch_json(
        opener, f'/basicspacedata/query/class/decay/NORAD_CAT_ID/{ids_csv}/format/json'
    )

    report = {
        'norad_ids': ids_list,
        'sha256': {'gp_history': gp_sha, 'satcat': satcat_sha, 'decay': decay_sha},
        'gp_summary': summarize_gp(gp_rows, ids_list),
        'satcat': satcat_rows,
        'decay': decay_rows,
    }
    md = format_markdown(report)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    args.summary_md.write_text(md, encoding='utf-8')
    print(md)


if __name__ == '__main__':
    main()
