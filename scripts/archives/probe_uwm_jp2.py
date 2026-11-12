#!/usr/bin/env python3
"""Check a bounded JP2 signature from UWM CONTENTdm, never claim full-file fixity."""
from __future__ import annotations

import argparse
import json
import urllib.request

DEFAULT_URL = "https://collections.lib.uwm.edu/digital/api/collection/agdm/id/10814/download"
JP2_MAGIC = bytes.fromhex("0000000c6a5020200d0a870a")


def probe(url: str, prefix_bytes: int = 32, timeout: float = 20.0) -> dict:
    if not 12 <= prefix_bytes <= 4096:
        raise ValueError("prefix_bytes must be between 12 and 4096")
    if not url.startswith("https://collections.lib.uwm.edu/digital/api/collection/agdm/id/"):
        raise ValueError("download must come from the custodial UWM endpoint")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Lontra-archival-access-audit/1",
                 "Range": f"bytes=0-{prefix_bytes-1}"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read(prefix_bytes)
        status = response.status
        content_range = response.headers.get("Content-Range")
        content_type = response.headers.get("Content-Type")
    if status not in (200, 206):
        raise ValueError("unexpected HTTP status")
    if not data.startswith(JP2_MAGIC):
        raise ValueError("unexpected JP2 signature")
    return {
        "url": url, "status": status, "content_type": content_type,
        "range_header_requested": f"bytes=0-{prefix_bytes-1}",
        "content_range": content_range,
        "range_support_observed": status == 206 and content_range is not None,
        "bytes_of_body_read": len(data), "body_prefix_hex": data.hex(),
        "jp2_magic_header_confirmed": True,
        "full_body_sha256": None, "full_body_byte_count": None,
        "partial_response_only": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--prefix-bytes", type=int, default=32)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    print(json.dumps(probe(args.url, args.prefix_bytes, args.timeout), indent=2))
