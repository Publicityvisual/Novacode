import unittest
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestComprehensivePackages(unittest.TestCase):
    def test_packages_web_server_exists(self):
        from packages.web.server import WEB_DIR
        self.assertTrue(WEB_DIR.exists())
        self.assertTrue((WEB_DIR / "index.html").exists())
        self.assertTrue((WEB_DIR / "logo.svg").exists())

    def test_packages_forge_trainer_dataset(self):
        from packages.forge.dataset import DatasetGenerator
        gen = DatasetGenerator()
        self.assertTrue(gen.output_dir.exists())

    def test_packages_media_generator_policy(self):
        from packages.media.generator import policy_check, detect_kind
        self.assertIsNone(policy_check("Cyberpunk city neon illustration"))
        self.assertEqual(detect_kind("create an image of a cat", None), "image")

    def test_packages_agents_swarm(self):
        from packages.agents.swarm import SwarmTurboEngine
        swarm = SwarmTurboEngine()
        res = swarm.dispatch_swarm("audit security and design architecture")
        self.assertEqual(res["task"], "audit security and design architecture")
        self.assertIn("architect", res["agents_results"])

if __name__ == "__main__":
    unittest.main()
