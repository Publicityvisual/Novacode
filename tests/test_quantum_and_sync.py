"""Unit tests for Quantum Cache, Auto Git Sync, and Benchmarker."""

import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from quantum_cache import QuantumCache
from git_sync import AutoGitSync
from auto_benchmarker import AutoBenchmarker


class TestQuantumAndSync(unittest.TestCase):
    """Test suite for Quantum Cache, Auto Git Sync, and Benchmarker."""

    def test_quantum_cache_get_set(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db_p = Path(tmp.name)
            qc = QuantumCache(db_path=db_p)
            model_id = "test-model"
            msgs = [{"role": "user", "content": "hello"}]
            resp = {"choices": [{"message": {"content": "world"}}]}

            # Cache miss
            self.assertIsNone(qc.get(model_id, msgs))

            # Set and hit
            qc.set(model_id, msgs, resp)
            cached = qc.get(model_id, msgs)
            self.assertIsNotNone(cached)
            self.assertEqual(cached["choices"][0]["message"]["content"], "world")

            # Stats
            st = qc.stats()
            self.assertEqual(st["total_entries"], 1)

    def test_git_sync_instantiation(self):
        syncer = AutoGitSync()
        self.assertTrue(syncer.repo_dir.exists())
        msg = syncer.generate_commit_message("1 file changed")
        self.assertTrue(len(msg) > 0)

    def test_benchmarker_instantiation(self):
        bench = AutoBenchmarker()
        self.assertTrue(bench.proxy_url.startswith("http"))


if __name__ == "__main__":
    unittest.main()
