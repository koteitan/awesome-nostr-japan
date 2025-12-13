#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from typing import Any, cast

try:
    import tomllib  # type: ignore[import-not-found, import-untyped]
except ImportError:
    import toml as tomllib  # type: ignore[import-untyped]


def convert() -> None:
    mode = "rb" if sys.version_info >= (3, 11) else "r"
    encoding = None if mode == "rb" else "utf-8"

    with open("awesome-nostr-japan.toml", mode, encoding=encoding) as toml_in:
        toml_data: dict[str, Any] = cast(Any, tomllib.load(toml_in))

    with open("data.json", "w", encoding="utf-8") as json_out:
        json.dump(toml_data, json_out, ensure_ascii=False, indent=2)

    print("Generated data.json")


if __name__ == "__main__":
    convert()
