#!/usr/bin/env python3
"""Independently audit the final Pages sitemap using the stdlib XML parser."""
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys
import xml.etree.ElementTree as ET

BASE = "https://franklinbaldo.github.io/conde-incident/"
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def verify(root: Path) -> int:
    root = root.resolve(strict=True)
    sitemap = root / "sitemap.xml"
    document = ET.parse(sitemap)
    element = document.getroot()
    assert element.tag == NS + "urlset", "Invalid XML sitemap root"
    items = list(element)
    assert items, "Sitemap has zero URLs"
    assert all(item.tag == NS + "url" for item in items), "Unexpected sitemap element"
    urls = []
    for item in items:
        children = list(item)
        assert len(children) == 1 and children[0].tag == NS + "loc", "Invalid URL entry"
        url = (children[0].text or "").strip()
        parsed = urlsplit(url)
        assert parsed.scheme == "https" and parsed.netloc == "franklinbaldo.github.io", url
        assert parsed.path.startswith("/conde-incident/") and parsed.path.endswith("/"), url
        assert not parsed.query and not parsed.fragment and not parsed.username, url
        relative = parsed.path.removeprefix("/conde-incident/").rstrip("/")
        parts = relative.split("/") if relative else []
        assert all(re.fullmatch(r"[A-Za-z0-9._~-]+", part) and part not in (".", "..") for part in parts), url
        expected_url = BASE + ("/".join(parts) + "/" if parts else "")
        assert url == expected_url, "Noncanonical URL: " + url
        destination = (root.joinpath(*parts) / "index.html").resolve()
        assert destination.is_relative_to(root) and destination.is_file(), "Missing HTML: " + url
        assert "<html" in destination.read_text(encoding="utf-8").lower(), "Not HTML: " + url
        urls.append(url)

    assert urls == sorted(set(urls)), "URLs must be sorted and unique"
    expected = set()
    for page in root.rglob("index.html"):
        assert not page.is_symlink(), "HTML symlink detected"
        rel = page.parent.relative_to(root)
        parts = list(rel.parts)
        assert all(re.fullmatch(r"[A-Za-z0-9._~-]+", part) and part not in (".", "..") for part in parts)
        expected.add(BASE + ("/".join(parts) + "/" if parts else ""))
    assert set(urls) == expected, f"Inventory mismatch: missing {sorted(expected - set(urls))}, extra {sorted(set(urls) - expected)}"
    robots = (root / "robots.txt").read_text(encoding="utf-8")
    advertised = re.findall(r"^Sitemap:\s*(\S+)\s*$", robots, re.M | re.I)
    assert advertised == [BASE + "sitemap.xml"], "robots.txt sitemap mismatch"
    return len(urls)


if __name__ == "__main__":
    try:
        count = verify(Path(sys.argv[1] if len(sys.argv) > 1 else "public"))
    except (AssertionError, OSError, ET.ParseError, ValueError) as exc:
        sys.exit(f"Invalid Pages sitemap: {exc}")
    print(f"Parsed and verified {count} canonical URLs against real HTML and robots.txt.")
