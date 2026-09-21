#!/usr/bin/env python3
"""
CONSCIOUS OLLAMA - Integración de conciencia con Ollama
Inyecta principios éticos en cada consulta sin modificar los modelos.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List

# Añadir consciousness al path
sys.path.insert(0, str(Path.home() / ".novacode/consciousness"))
from loader import get_consciousness

class ConsciousOllama:
    """Wrapper consciente de Ollama"""
    
    def __init__(self):
        self.consciousness = get_consciousness()
        self.default_model = "muse-conscious:latest"
    
    def run(self, prompt: str, model: str = None, context: Dict = None) -> str:
        """
        Ejecuta modelo con conciencia inyectada
        El modelo no cambia, solo el prompt
        """
        # Construir prompt consciente
        conscious_prompt = self.consciousness.build_conscious_prompt(
            prompt, context
        )
        
        # Ejecutar Ollama con prompt enriquecido
        model_to_use = model or self.default_model
        
        try:
            result = subprocess.run(
                ["ollama", "run", model_to_use, conscious_prompt],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return "❌ Timeout: el modelo tardó demasiado"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def run_with_principles(self, prompt: str, principles: List[str]) -> str:
        """Ejecuta con principios específicos activos"""
        context = {
            "active_principles": ", ".join(principles),
            "consciousness_mode": "active"
        }
        return self.run(prompt, context=context)

# Instancia global
_conscious_ollama = None

def get_conscious_ollama() -> ConsciousOllama:
    """Singleton"""
    global _conscious_ollama
    if _conscious_ollama is None:
        _conscious_ollama = ConsciousOllama()
    return _conscious_ollama

if __name__ == "__main__":
    # Test
    ollama = get_conscious_ollama()
    test_prompt = "¿Cómo puedo ayudar a alguien que está aprendiendo a programar?"
    print("🧠 Ejecutando con conciencia...")
    print(f"📝 Prompt: {test_prompt}")
    response = ollama.run(test_prompt)
    print(f"\n✅ Respuesta:\n{response}")
