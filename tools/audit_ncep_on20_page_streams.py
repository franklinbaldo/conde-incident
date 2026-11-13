"""Offline, exact-byte PDF page-tree/CCITT ledger for NMC Office Note 20.

The PDF is intentionally not committed. A valid ledger does not transcribe text,
validate a 1963 format, or mean a scanned folio is an independent publication.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


class AuditError(ValueError):
    pass


def _require(condition, message):
    if not condition:
        raise AuditError(message)


def extract_pages(source, expected_pages=23):
    """Return PDF page-order image-stream fingerprints; no OCR or PDF rendering."""
    markers = list(re.finditer(rb'\r(\d+) 0 obj\r', source))
    objects = {}
    for index, match in enumerate(markers):
        number = int(match.group(1))
        _require(number not in objects, 'duplicate object')
        stop = markers[index + 1].start() if index + 1 < len(markers) else len(source)
        objects[number] = source[match.end():stop]
    _require(len(objects) >= expected_pages, 'missing PDF objects')

    def one(pattern, payload, label):
        match = re.search(pattern, payload, re.S)
        _require(match is not None, 'missing ' + label)
        return match

    def walk(object_number):
        obj = objects[object_number]
        if re.search(rb'/Type\s*/Page\b', obj):
            return [object_number]
        _require(re.search(rb'/Type\s*/Pages\b', obj), 'invalid page tree')
        content = one(rb'/Kids\s*\[(.*?)\]', obj, 'Kids').group(1)
        children = [int(m.group(1)) for m in re.finditer(rb'(\d+)\s+0\s+R', content)]
        pages = [page for child in children for page in walk(child)]
        _require(int(one(rb'/Count\s+(\d+)', obj, 'Count').group(1)) == len(pages), 'page-tree count mismatch')
        return pages

    root = [i for i, obj in objects.items() if re.search(rb'/Type\s*/Pages\b', obj) and b'/Parent' not in obj]
    _require(len(root) == 1, 'ambiguous PDF pages root')
    pages = walk(root[0])
    _require(len(pages) == expected_pages and len(set(pages)) == expected_pages, 'unexpected page count')
    result = []
    for position, page_number in enumerate(pages, 1):
        page = objects[page_number]
        xobject_ref = int(one(rb'/XObject\s+(\d+)\s+0\s+R', page, 'XObject reference').group(1))
        index, image_ref = (int(v) for v in one(rb'/Im(\d+)\s+(\d+)\s+0\s+R', objects[xobject_ref], 'image reference').groups())
        _require(index == position - 1, 'image index disagrees with page tree')
        image = objects[image_ref]
        head = image.split(b'stream', 1)[0]
        _require(b'/CCITTFaxDecode' in head and b'/K -1' in head, 'unsupported image compression')
        _require(int(one(rb'/Name\s*/Im(\d+)', head, 'image name').group(1)) == index, 'image name mismatch')
        width = int(one(rb'/Width\s+(\d+)', head, 'width').group(1))
        height = int(one(rb'/Height\s+(\d+)', head, 'height').group(1))
        length_ref = int(one(rb'/Length\s+(\d+)\s+0\s+R', head, 'stream length ref').group(1))
        length = int(one(rb'^\s*(\d+)', objects[length_ref], 'stream length').group(1))
        stream_offset = one(rb'stream\r\n', image, 'stream marker').end()
        payload = image[stream_offset:stream_offset + length]
        _require(len(payload) == length and image[stream_offset + length:].startswith(b'\rendstream'), 'stream length or boundary mismatch')
        result.append(dict(pdf_page=position, page_object=page_number, image_object=image_ref,
                           width=width, height=height, ccitt_bytes=length,
                           ccitt_sha256=hashlib.sha256(payload).hexdigest()))
    return result


def verify(pdf, manifest):
    source = Path(pdf).read_bytes()
    expected = json.loads(Path(manifest).read_text(encoding='utf-8'))
    _require(hashlib.sha256(source).hexdigest() == expected['pdf_sha256'], 'PDF SHA-256 mismatch')
    _require(len(source) == expected['pdf_bytes'], 'PDF size mismatch')
    actual = extract_pages(source)
    _require(actual == expected['page_streams'], 'page tree, image streams or hashes differ')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', required=True, help='Downloaded complete ON20 Wayback PDF')
    parser.add_argument('--manifest', default='research/meteorology/ncep_on20_page_audit_20261112.json')
    args = parser.parse_args()
    pages = verify(args.pdf, args.manifest)
    print(f'PASS: {len(pages)} page-tree-linked CCITT streams and PDF SHA-256; NOT an OCR or 1963 validation')


if __name__ == '__main__':
    main()
