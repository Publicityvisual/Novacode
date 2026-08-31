"""Unit tests for Next-Gen NovaCode Engine capabilities."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from sandbox import InstantSandbox
from swarm import SwarmTurboEngine
from semantic_graph import SemanticCodeGraph
from canvas import TerminalCanvas
from ast_surgeon import ASTSurgeon
from sentinel import SentinelDaemon


class TestNextGenEngine(unittest.TestCase):
    """Test suite for sandbox, swarm, semantic graph, canvas, AST surgeon, and sentinel."""

    def test_sandbox_snapshot_and_rollback(self):
        sb = InstantSandbox(target_dir=Path(__file__).parent)
        snap = sb.create_snapshot("unit_test")
        self.assertIn("id", snap)
        self.assertTrue(sb.rollback(snap))

    def test_swarm_dispatch(self):
        swarm = SwarmTurboEngine()
        res = swarm.dispatch_swarm("Crear microservicio REST")
        self.assertEqual(res["task"], "Crear microservicio REST")
        self.assertIn("architect", res["agents_results"])
        self.assertIn("tdd_coder", res["agents_results"])

    def test_semantic_code_graph(self):
        root_repo = Path(__file__).resolve().parent.parent
        graph = SemanticCodeGraph(root_dir=root_repo)
        stats = graph.build_graph()
        self.assertGreater(stats["total_nodes"], 0)
        symbols = graph.search_symbol("InstantSandbox")
        self.assertTrue(any("InstantSandbox" in s["symbol"] for s in symbols))

    def test_terminal_canvas(self):
        spark = TerminalCanvas.render_sparkline([10, 20, 30, 40, 50])
        self.assertIn("Latencia", spark)
        table = TerminalCanvas.render_table(["H1", "H2"], [["V1", "V2"]])
        self.assertIn("H1", table)

    def test_ast_surgeon_rename(self):
        orig_code = "def calculate_total(a, b):\n    return a + b\nres = calculate_total(1, 2)"
        new_code, count = ASTSurgeon.rename_symbol(orig_code, "calculate_total", "compute_sum")
        self.assertIn("def compute_sum", new_code)
        self.assertIn("res = compute_sum", new_code)
        self.assertGreater(count, 0)

    def test_sentinel_daemon_syntax_check(self):
        sentinel = SentinelDaemon()
        dummy_file = Path("/tmp/test_sentinel_valid.py")
        dummy_file.write_text("x = 10\nprint(x)\n")
        ok, err = sentinel.check_syntax(dummy_file)
        self.assertTrue(ok)
        dummy_file.unlink()


if __name__ == "__main__":
    unittest.main()
