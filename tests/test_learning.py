#!/usr/bin/env python3
"""Tests for NovaCode Self-Learning Engine & Model Evolver."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import learned_capabilities as lc


class LearningEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_learning.db"
        self.engine = lc.SelfLearningEngine(self.db_path)
        self.evolver = lc.ModelEvolver(self.engine)
        self.improver = lc.AutoImprover(self.engine)

    def tearDown(self) -> None:
        self.engine.close()
        self.tmp_dir.cleanup()

    def test_record_and_get_patterns(self) -> None:
        self.engine.record_pattern("code_generation", "Use type annotations", success=True)
        self.engine.record_pattern("code_generation", "Use type annotations", success=True)
        patterns = self.engine.get_patterns("code_generation")
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]["pattern"], "Use type annotations")
        self.assertEqual(patterns[0]["success_count"], 2)

    def test_knowledge_base(self) -> None:
        self.engine.add_knowledge("How to connect SQLite in Python?", "Use sqlite3.connect with WAL mode.", "database")
        results = self.engine.search_knowledge("SQLite Python")
        self.assertTrue(len(results) >= 1)
        self.assertIn("WAL mode", results[0]["solution"])

    def test_model_performance_and_metrics(self) -> None:
        self.evolver.record_performance("novacode/jet", "code_generation", success=True, latency=0.45, tokens=120)
        self.evolver.record_performance("novacode/jet", "code_generation", success=True, latency=0.42, tokens=110)
        self.evolver.record_performance("novacode/dev", "code_generation", success=False, latency=1.20, tokens=80)

        metrics = self.evolver.get_all_metrics()
        self.assertIn("code_generation", metrics)
        self.assertEqual(len(metrics["code_generation"]), 2)

        best = self.evolver.get_best_model("code_generation")
        self.assertEqual(best, "novacode/jet")

    def test_classify_task_type(self) -> None:
        self.assertEqual(lc._classify_task_type("Please debug this NullPointerException"), "debugging")
        self.assertEqual(lc._classify_task_type("Refactor and clean up the database query"), "refactoring")
        self.assertEqual(lc._classify_task_type("Write unit tests with pytest"), "testing")
        self.assertEqual(lc._classify_task_type("Generate an image of a cybernetic city"), "multimodal")


if __name__ == "__main__":
    unittest.main()
