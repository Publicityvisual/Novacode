"""Unit tests for Docker Pilot and Developer Tools Suite."""

import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from docker_pilot import DockerPilot
from devtools import ApiTester, NetworkPilot, SecretScanner


class TestDockerAndDevTools(unittest.TestCase):
    """Test suite for Docker Pilot and Developer Tools."""

    def test_docker_pilot_detect_stack(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_p = Path(tmp_dir)
            (tmp_p / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')
            pilot = DockerPilot()
            stack = pilot.detect_project_stack(tmp_p)
            self.assertEqual(stack["language"], "nodejs")
            self.assertEqual(stack["framework"], "react")

    def test_dockerfile_generation_and_audit(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_p = Path(tmp_dir)
            (tmp_p / "requirements.txt").write_text("fastapi\nuvicorn\n")
            pilot = DockerPilot()
            content, df_path = pilot.generate_dockerfile(tmp_p)
            self.assertTrue(df_path.exists())
            self.assertIn("FROM python:", content)

            audit = pilot.audit_dockerfile(df_path)
            self.assertTrue(audit["valid"])

    def test_network_pilot_scan(self):
        ports = NetworkPilot.scan_common_ports("127.0.0.1")
        self.assertIsInstance(ports, dict)

    def test_secret_scanner(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_p = Path(tmp_dir)
            (tmp_p / "test_file.txt").write_text("normal text without secret")
            findings = SecretScanner.scan_directory(tmp_p)
            self.assertEqual(len(findings), 0)


if __name__ == "__main__":
    unittest.main()
