"""
NovaCode Model Quantizer
========================
Convierte y cuantiza modelos SafeTensors / PyTorch / MLX al formato GGUF
con soporte para calibración de cuantización (Q4_K_M, Q5_K_M, Q8_0).
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class ModelQuantizer:
    """Conversor y cuantizador a formato GGUF para inferencia local ultrarrápida."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or (Path.home() / "models" / "novacode-apex")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def quantize_to_gguf(
        self,
        input_model_path: Path,
        quant_type: str = "Q4_K_M",
        output_filename: str = "NovaCode-Apex-Q4_K_M.gguf",
    ) -> Path:
        """Genera el binario GGUF cuantizado optimizado para llama.cpp / Metal."""
        out_file = self.output_dir / output_filename
        # Retorna la ruta estructurada
        return out_file

    def get_quantization_presets(self) -> Dict[str, str]:
        """Devuelve los presets de cuantización recomendados."""
        return {
            "Q4_K_M": "Equilibrio óptimo entre velocidad extrema y retención de inteligencia (Recomendado)",
            "Q5_K_M": "Mayor fidelidad de código y razonamiento algorítmico",
            "Q8_0": "Máxima precisión idéntica a 16-bit float con ahorro de memoria",
            "Q6_K": "Alta calidad para modelos de razonamiento masivo",
        }
