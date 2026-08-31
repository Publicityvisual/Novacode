"""
NovaCode Model Merger
=====================
Orquesta la fusión de modelos de lenguaje y visión utilizando arquitecturas
SLERP, TIES, DARE y FrankMoE para combinar las mejores capacidades de múltiples
modelos base en un único super modelo NovaCode.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ModelMerger:
    """Configurador y ejecutor de fusiones de modelos (MergeKit)."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or (Path.home() / ".novacode" / "merges")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_slerp_config(
        self,
        base_model: str,
        target_model: str,
        output_name: str = "NovaCode-Apex-Slerp",
        t_param: float = 0.5,
    ) -> Path:
        """Crea una configuración SLERP (Spherical Linear Interpolation) para fusionar dos modelos."""
        config: Dict[str, Any] = {
            "merge_method": "slerp",
            "base_model": base_model,
            "models": [
                {"model": base_model, "parameters": {"weight": 1.0 - t_param}},
                {"model": target_model, "parameters": {"weight": t_param}},
            ],
            "parameters": {
                "t": [
                    {"filter": "self_attn", "value": [0.0, 0.5, 0.3, 0.7, 1.0]},
                    {"filter": "mlp", "value": [1.0, 0.5, 0.7, 0.3, 0.0]},
                    {"value": 0.5},
                ]
            },
            "dtype": "bfloat16",
        }

        config_path = self.output_dir / f"{output_name}_config.yaml"
        lines = [
            f"merge_method: slerp",
            f"base_model: {base_model}",
            f"dtype: bfloat16",
            f"models:",
            f"  - model: {base_model}",
            f"    parameters:",
            f"      weight: {1.0 - t_param}",
            f"  - model: {target_model}",
            f"    parameters:",
            f"      weight: {t_param}",
            f"parameters:",
            f"  t:",
            f"    - filter: self_attn",
            f"      value: [0.0, 0.5, 0.3, 0.7, 1.0]",
            f"    - filter: mlp",
            f"      value: [1.0, 0.5, 0.7, 0.3, 0.0]",
            f"    - value: 0.5",
        ]
        config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return config_path

    def create_moe_config(
        self,
        base_model: str,
        experts: List[Dict[str, str]],
        output_name: str = "NovaCode-Apex-MoE-4x8B",
    ) -> Path:
        """Crea una configuración Mixture of Experts (MoE) uniendo múltiples especialistas."""
        config_path = self.output_dir / f"{output_name}_config.yaml"
        lines = [
            f"base_model: {base_model}",
            f"gate_mode: hidden",
            f"dtype: bfloat16",
            f"experts:",
        ]
        for exp in experts:
            lines.append(f"  - source_model: {exp['model']}")
            lines.append(f"    positive_prompts:")
            for p in exp.get("prompts", ["code", "reasoning"]):
                lines.append(f"      - \"{p}\"")

        config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return config_path
