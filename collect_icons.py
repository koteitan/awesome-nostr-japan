#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
import time
from typing import Any, cast
from urllib.parse import urljoin, urlparse

try:
    import tomllib  # type: ignore[import-not-found, import-untyped]
except ImportError:
    import toml as tomllib  # type: ignore[import-untyped]

import toml
import requests
from bs4 import BeautifulSoup


def get_favicon_url(address: str) -> str | None:
    """Fetch favicon URL from a website."""
    if not address:
        return None

    # Skip non-http URLs
    if not address.startswith(('http://', 'https://')):
        return None

    parsed = urlparse(address)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(address, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find favicon in various link tags
        icon_links = soup.find_all('link', rel=lambda x: x and any(
            r in x for r in ['icon', 'shortcut icon', 'apple-touch-icon']
        ))

        for link in icon_links:
            href = link.get('href')
            if href:
                icon_url = urljoin(address, href)
                # Verify the icon exists
                try:
                    icon_resp = requests.head(icon_url, headers=headers, timeout=5, allow_redirects=True)
                    if icon_resp.status_code == 200:
                        return icon_url
                except:
                    pass

        # Try default favicon.ico
        favicon_url = f"{base_url}/favicon.ico"
        try:
            favicon_resp = requests.head(favicon_url, headers=headers, timeout=5, allow_redirects=True)
            if favicon_resp.status_code == 200:
                return favicon_url
        except:
            pass

        # Fallback to Google Favicon API
        return f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=64"

    except Exception as e:
        print(f"  Error fetching {address}: {e}", file=sys.stderr)
        # Fallback to Google Favicon API
        return f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=64"


def main():
    mode = "rb" if sys.version_info >= (3, 11) else "r"
    encoding = None if mode == "rb" else "utf-8"

    with open("awesome-nostr-japan.toml", mode, encoding=encoding) as f:
        data: dict[str, Any] = cast(Any, tomllib.load(f))

    skip_sections = ['awesome-nostr-japan', 'License', 'Author']

    total_items = 0
    processed = 0

    # Count total items
    for section_key, section_data in data.items():
        if section_key in skip_sections:
            continue
        if not isinstance(section_data, dict):
            continue
        for item_key, item in section_data.items():
            if isinstance(item, dict) and 'address' in item:
                total_items += 1

    print(f"Processing {total_items} items...")

    for section_key, section_data in data.items():
        if section_key in skip_sections:
            continue
        if not isinstance(section_data, dict):
            continue

        for item_key, item in section_data.items():
            if not isinstance(item, dict) or 'address' not in item:
                continue

            processed += 1
            address = item['address']
            name = item.get('name', address)
            print(f"[{processed}/{total_items}] {name}...", end=" ", flush=True)

            icon_url = get_favicon_url(address)
            if icon_url:
                item['icon_url'] = icon_url
                print(f"OK")
            else:
                print(f"No icon")

            # Rate limiting
            time.sleep(0.5)

    # Write back to TOML
    with open("awesome-nostr-japan.toml", "w", encoding="utf-8") as f:
        toml.dump(data, f)

    print(f"\nDone! Updated awesome-nostr-japan.toml")


if __name__ == "__main__":
    main()
