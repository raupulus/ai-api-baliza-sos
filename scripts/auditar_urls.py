#!/usr/bin/env python3
"""Audita las URLs de docs/rag/*.md: extrae, desduplica y comprueba el estado HTTP."""
from __future__ import annotations

import glob
import re
import urllib.error
import urllib.request
from collections import defaultdict
from typing import Any

URL_RE = re.compile(r"https?://[^\s\)\]\}\"`'<>]+")


def extract_urls() -> defaultdict[str, list[str]]:
    urls: defaultdict[str, list[str]] = defaultdict(list)
    for path in sorted(glob.glob("docs/rag/*.md")):
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for m in URL_RE.findall(line):
                    url = str(m).rstrip(".,;:")
                    urls[url].append(f"{path}:{i}")
    return urls


def check(url: str, timeout: int = 12) -> tuple[Any, Any]:
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; rag-audit/1.0)",
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, url
    except urllib.error.URLError as e:
        return f"ERR:{e.reason}", url
    except Exception as e:  # noqa: BLE001 - último recurso del auditor
        return f"ERR:{type(e).__name__}", url


def main() -> None:
    urls = extract_urls()
    ordered = sorted(urls.items(), key=lambda kv: kv[0])
    print(f"TOTAL URLs únicas: {len(ordered)}\n")
    results: dict[str, tuple[Any, Any, list[str]]] = {}
    for url, refs in ordered:
        status, final = check(url)
        results[url] = (status, final, refs)
        flag = "OK" if isinstance(status, int) and status < 400 else "FAIL"
        print(f"[{flag}] {status}  {url}")
    print("\n--- RESUMEN ---")
    ok = sum(1 for v in results.values() if isinstance(v[0], int) and v[0] < 400)
    print(f"OK: {ok} / {len(results)}")
    print("\n--- FALLOS / REDIRECTS ---")
    for _url, (status, final, refs) in results.items():
        if not (isinstance(status, int) and status < 400):
            print(f"\n{status} -> {final}")
            for r in refs:
                print(f"    {r}")


if __name__ == "__main__":
    main()
