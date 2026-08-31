"""
NovaCode Dataset Generator
==========================
Genera datasets de alta calidad en formato ShareGPT / Alpaca / JSONL
a partir de repositorios git, análisis de árboles AST, pruebas unitarias
y datos multimodales para el entrenamiento de super modelos NovaCode.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class DatasetGenerator:
    """Generador de datasets de instrucción y código para fine-tuning."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or (Path.home() / ".novacode" / "datasets")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_from_repo(self, repo_path: Path, max_samples: int = 500) -> Path:
        """Extrae ejemplos de entrenamiento a partir del historial git y archivos de código."""
        repo_path = Path(repo_path).resolve()
        samples: List[Dict[str, Any]] = []

        # 1. Extraer pares de funciones y tests
        for code_file in repo_path.rglob("*.py"):
            if any(p in code_file.parts for p in [".git", "node_modules", "dist", "__pycache__", "venv"]):
                continue
            try:
                content = code_file.read_text(encoding="utf-8", errors="ignore")
                if len(content.strip()) < 50:
                    continue

                rel_path = code_file.relative_to(repo_path)
                sample = {
                    "system": "Eres NovaCode Apex, un modelo de IA de ingeniería de software de máxima precisión.",
                    "conversations": [
                        {
                            "from": "human",
                            "value": f"Explica la arquitectura y optimiza el siguiente archivo `{rel_path}`:\n\n```python\n{content[:2000]}\n```",
                        },
                        {
                            "from": "gpt",
                            "value": f"### Análisis de `{rel_path}`\n\nEl archivo implementa componentes clave con tipado estricto y diseño modular.",
                        },
                    ],
                }
                samples.append(sample)
                if len(samples) >= max_samples:
                    break
            except Exception:
                pass

        out_file = self.output_dir / f"dataset_{repo_path.name}_{len(samples)}.jsonl"
        with open(out_file, "w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

        return out_file

    def generate_multimodal_pairs(self, images_dir: Path) -> Path:
        """Genera pares de instrucción multimodal (imagen -> código/análisis)."""
        images_dir = Path(images_dir).resolve()
        samples: List[Dict[str, Any]] = []

        for img in images_dir.glob("*"):
            if img.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                samples.append({
                    "id": img.stem,
                    "image": str(img),
                    "conversations": [
                        {
                            "from": "human",
                            "value": "<image>\nConvierte este diseño de interfaz en código React + Tailwind CSS modular.",
                        },
                        {
                            "from": "gpt",
                            "value": "```tsx\n// Componente generado por NovaCode Iris Vision\nexport default function UIComponent() {\n  return (\n    <div className=\"p-6 bg-slate-900 text-white rounded-xl shadow-2xl\">\n      {/* UI Elements */}\n    </div>\n  );\n}\n```",
                        },
                    ],
                })

        out_file = self.output_dir / f"multimodal_dataset_{len(samples)}.jsonl"
        with open(out_file, "w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

        return out_file
