"""
NovaCode Multimodal Projector Bridge
====================================
Conecta modelos de lenguaje base con codificadores de visión (CLIP/SigLIP)
y audio (Whisper/Kokoro) para dotar a cualquier modelo de super capacidades omni.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class MultimodalProjector:
    """Puente adaptador de visión y audio para modelos de lenguaje."""

    def __init__(self) -> None:
        self.vision_encoders = {
            "siglip": "google/siglip-so400m-patch14-384",
            "clip-vit": "openai/clip-vit-large-patch14-336",
            "qwen2-vl": "Qwen/Qwen2-VL-7B-Instruct",
        }
        self.audio_encoders = {
            "whisper": "openai/whisper-large-v3-turbo",
            "kokoro": "hexgrad/Kokoro-82M",
        }

    def build_projector_config(
        self,
        language_backbone: str,
        vision_encoder: str = "siglip",
        projector_type: str = "mlp2x_gelu",
    ) -> Dict[str, Any]:
        """Genera la arquitectura de proyección multimodal omnisciente."""
        return {
            "architecture": "NovaCode-Omni-Multimodal-v1",
            "language_model": language_backbone,
            "vision_encoder": self.vision_encoders.get(vision_encoder, vision_encoder),
            "projector_type": projector_type,
            "projector_hidden_dim": 4096,
            "image_aspect_ratio": "anyres",
            "max_image_tokens": 1152,
            "audio_enabled": True,
            "modalities": ["text", "code", "vision_ui", "diagrams", "audio_speech"],
        }
