#!/usr/bin/env python3
"""Tests to verify that all shell scripts have valid syntax and executable bits."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"

class ScriptSyntaxTests(unittest.TestCase):
    def test_all_shell_scripts_syntax(self) -> None:
        sh_files = list(SCRIPTS_DIR.glob("*.sh"))
        self.assertTrue(len(sh_files) > 0, "No shell scripts found")
        for sh in sh_files:
            res = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Syntax error in {sh.name}: {res.stderr}")
            self.assertTrue(os.access(sh, os.X_OK), f"Script not executable: {sh.name}")


if __name__ == "__main__":
    unittest.main()
