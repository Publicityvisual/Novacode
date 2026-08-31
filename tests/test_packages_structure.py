import unittest
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestPackagesStructure(unittest.TestCase):
    def test_package_imports(self):
        from packages.cli.launcher import find_native_engine
        engine = find_native_engine()
        self.assertIsInstance(engine, str)

        from packages.core.engine import NovaHyperEngine
        self.assertIsNotNone(NovaHyperEngine)

        from packages.agents.autonomous_pilot import AutonomousGoalPilot
        self.assertIsNotNone(AutonomousGoalPilot)

        from packages.tools.ast_surgeon import ASTSurgeon
        self.assertIsNotNone(ASTSurgeon)

        from packages.tools.doctor import main as doctor_main
        self.assertIsNotNone(doctor_main)

    def test_cli_launcher_routing(self):
        from packages.cli.main import NOVACODE_NATIVE_COMMANDS
        self.assertIn("models", NOVACODE_NATIVE_COMMANDS)
        self.assertIn("providers", NOVACODE_NATIVE_COMMANDS)
        self.assertIn("mcp", NOVACODE_NATIVE_COMMANDS)
        self.assertIn("web", NOVACODE_NATIVE_COMMANDS)
        self.assertIn("session", NOVACODE_NATIVE_COMMANDS)

if __name__ == "__main__":
    unittest.main()
