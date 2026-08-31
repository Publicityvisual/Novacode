"""Unit tests for Autonomous Goal Pilot."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from autonomous_pilot import AutonomousGoalPilot


class TestAutonomousPilot(unittest.TestCase):
    """Test suite for AutonomousGoalPilot."""

    def test_goal_decomposition_fallback(self):
        pilot = AutonomousGoalPilot()
        steps = pilot.decompose_goal("Crear un scraper en Python")
        self.assertIsInstance(steps, list)
        self.assertGreaterEqual(len(steps), 3)

    def test_goal_execution_loop(self):
        def fake_ai(prompt, system):
            return "def main():\n    print('Hello World')\n"

        pilot = AutonomousGoalPilot(ai_client=fake_ai, max_iterations=3)
        res = pilot.execute_goal("Crear microservicio")
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["steps_count"], 0)
        self.assertEqual(len(res["history"]), res["steps_count"])


if __name__ == "__main__":
    unittest.main()
