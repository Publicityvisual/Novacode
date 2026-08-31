"""Unit tests for NovaCode Hyper-Engine Core."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from engine_core import AutoDependencyManager, SmartPrivilegeEscalator, NovaHyperEngine


class TestEngineCore(unittest.TestCase):
    """Test suite for NovaHyperEngine execution and auto-healing."""

    def test_dependency_resolver(self):
        self.assertEqual(AutoDependencyManager.resolve_package_name("cv2"), "opencv-python")
        self.assertEqual(AutoDependencyManager.resolve_package_name("PIL"), "pillow")
        self.assertEqual(AutoDependencyManager.resolve_package_name("requests"), "requests")

    def test_hyper_engine_eval(self):
        engine = NovaHyperEngine()
        ok, res, err = engine.execute_hybrid("2 ** 8 + 44")
        self.assertTrue(ok)
        self.assertEqual(res, 300)

    def test_hyper_engine_shell_magic(self):
        engine = NovaHyperEngine()
        ok, res, err = engine.execute_hybrid("!echo 'NovaCode Hyper-Engine Shell'")
        self.assertTrue(ok)
        self.assertEqual(res, 0)

    def test_hyper_engine_exec(self):
        engine = NovaHyperEngine()
        scope = {}
        ok, res, err = engine.execute_hybrid("x = 42; y = x * 2", globals_dict=scope)
        self.assertTrue(ok)
        self.assertEqual(scope.get("y"), 84)


if __name__ == "__main__":
    unittest.main()
