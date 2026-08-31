"""Tests for NovaCode Model Forge suite."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from forge.dataset import DatasetGenerator
from forge.merger import ModelMerger
from forge.trainer import ModelTrainer
from forge.quantizer import ModelQuantizer
from forge.projector import MultimodalProjector


class TestModelForge(unittest.TestCase):
    """Test suite for proprietary model forge modules."""

    def test_dataset_generator(self):
        gen = DatasetGenerator()
        self.assertTrue(gen.output_dir.exists())

    def test_model_merger_slerp(self):
        merger = ModelMerger()
        cfg_path = merger.create_slerp_config("model-a", "model-b", output_name="test_merge")
        self.assertTrue(cfg_path.exists())
        self.assertIn("merge_method: slerp", cfg_path.read_text(encoding="utf-8"))
        cfg_path.unlink()

    def test_model_trainer(self):
        trainer = ModelTrainer()
        res = trainer.train_lora("base-model", Path("/tmp/data"), iters=100)
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["iterations"], 100)

    def test_model_quantizer(self):
        quant = ModelQuantizer()
        presets = quant.get_quantization_presets()
        self.assertIn("Q4_K_M", presets)

    def test_multimodal_projector(self):
        proj = MultimodalProjector()
        cfg = proj.build_projector_config("nova-backbone")
        self.assertEqual(cfg["architecture"], "NovaCode-Omni-Multimodal-v1")
        self.assertIn("vision_ui", cfg["modalities"])


if __name__ == "__main__":
    unittest.main()
