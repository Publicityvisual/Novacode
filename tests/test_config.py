#!/usr/bin/env python3
"""Tests for JSONC parsing and configuration validation."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

def strip_jsonc(text: str) -> str:
    res, in_str, esc, i, n = [], False, False, 0, len(text)
    while i < n:
        c = text[i]
        if in_str:
            res.append(c)
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
            i += 1
        else:
            if c == '"': in_str = True; res.append(c); i += 1
            elif c == "/" and i + 1 < n and text[i+1] == "/":
                while i < n and text[i] != "\n": i += 1
            elif c == "/" and i + 1 < n and text[i+1] == "*":
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i+1] == "/"): i += 1
                i += 2
            else: res.append(c); i += 1
    return re.sub(r",\s*([\]}])", r"\1", "".join(res))


class ConfigParsingTests(unittest.TestCase):
    def test_preserves_urls_with_double_slashes(self) -> None:
        raw_jsonc = '''{
            // Comment before schema
            "$schema": "https://novacode.ai/config.json",
            "api_url": "https://integrate.api.nvidia.com/v1",
            /* Block comment
               with multiple lines */
            "autoupdate": true,
        }'''
        cleaned = strip_jsonc(raw_jsonc)
        data = json.loads(cleaned)
        self.assertEqual(data["$schema"], "https://novacode.ai/config.json")
        self.assertEqual(data["api_url"], "https://integrate.api.nvidia.com/v1")
        self.assertTrue(data["autoupdate"])

    def test_live_novacode_jsonc_parses(self) -> None:
        config_path = Path.home() / ".config" / "novacode" / "novacode.jsonc"
        if config_path.exists():
            cleaned = strip_jsonc(config_path.read_text(encoding="utf-8"))
            data = json.loads(cleaned)
            self.assertIn("provider", data)
            self.assertIn("model", data)


if __name__ == "__main__":
    unittest.main()
