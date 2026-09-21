#!/usr/bin/env python3
"""
CONSCIOUSNESS LOADER - Sistema de carga de principios éticos
Inyecta memoria ética en cada interacción sin aumentar peso del modelo.
"""

import json
import os
from pathlib import Path
from typing import Dict, List

class ConsciousnessLoader:
    """
    Loader de conciencia artificial que:
    - Carga principios éticos desde disco
    - Adapta el tono según el contexto
    - Inyecta memoria ética en prompts
    - No aumenta el peso del modelo
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/.novacode/consciousness"))
        self.principles = self._load_principles()
        self.memory_bank = self._load_memory_bank()
        self.dataset = self._load_dataset()
    
    def _load_principles(self) -> Dict:
        """Carga principios éticos"""
        principles_file = self.base_path / "principles.json"
        if principles_file.exists():
            try:
                with open(principles_file, 'r') as f:
                    return json.load(f)
            except (OSError, ValueError):
                return {}
        return {}
    
    def _load_memory_bank(self) -> Dict:
        """Carga memory bank de valores"""
        values_file = self.base_path / "memory-bank/values.json"
        if values_file.exists():
            try:
                with open(values_file, 'r') as f:
                    return json.load(f)
            except (OSError, ValueError):
                return {}
        return {}
    
    def _load_dataset(self) -> Dict:
        """Carga dataset de entrenamiento ético"""
        dataset_file = self.base_path / "dataset/ethical_prompts.json"
        if dataset_file.exists():
            try:
                with open(dataset_file, 'r') as f:
                    return json.load(f)
            except (OSError, ValueError):
                return {}
        return {}
    
    def build_conscious_prompt(self, user_prompt: str, context: Dict = None) -> str:
        """
        Construye prompt con conciencia inyectada
        Sin aumentar peso del modelo, solo en el prompt
        """
        # Obtener principios relevantes
        relevant_principles = self._get_relevant_principles(user_prompt)
        
        # Construir prompt consciente
        prompt_parts = []
        
        # 1. Principios activos
        if relevant_principles:
            prompt_parts.append("## PRINCIPIOS ACTIVOS\n")
            for p in relevant_principles[:3]:
                prompt_parts.append(f"- {p['name']}: {p['description']}")
            prompt_parts.append("")
        
        # 2. Contexto ético
        if context:
            prompt_parts.append("## CONTEXTO\n")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")
        
        # 3. Instrucciones de tono
        tone = self._detect_tone(user_prompt)
        prompt_parts.append(f"## TONO: {tone}\n")
        
        # 4. Prompt del usuario
        prompt_parts.append(f"## CONSULTA\n{user_prompt}")
        
        return "\n".join(prompt_parts)
    
    def _get_relevant_principles(self, prompt: str) -> List[Dict]:
        """Obtiene principios relevantes para el prompt"""
        principles = self.principles.get("core_principles", [])
        prompt_lower = prompt.lower()
        
        relevant = []
        for p in principles:
            # Detectar relevancia por palabras clave
            keywords = {
                "ética": ["ético", "moral", "dañar", "perjudicial"],
                "humanismo": ["humano", "persona", "usuario", "cliente"],
                "empatía": ["ayuda", "aprende", "principiante", "lento"],
                "transparencia": ["por qué", "explica", "razón"],
                "responsabilidad": ["impacto", "consecuencia", "largo plazo"]
            }
            
            for category, words in keywords.items():
                if any(word in prompt_lower for word in words):
                    if p["id"] in ["P001", "P002", "P003", "P004", "P005", "P006"]:
                        relevant.append(p)
                        break
        
        return relevant[:3]
    
    def _detect_tone(self, prompt: str) -> str:
        """Detecta el tono apropiado"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["ayuda", "no entiendo", "principiante", "lento"]):
            return "empathetic"
        elif any(word in prompt_lower for word in ["urgente", "rápido", "ya", "ahora"]):
            return "urgent"
        elif any(word in prompt_lower for word in ["código", "programa", "implementa"]):
            return "technical"
        elif any(word in prompt_lower for word in ["idea", "crea", "diseña"]):
            return "creative"
        else:
            return "professional"
    
    def get_conscious_system_prompt(self) -> str:
        """Obtiene system prompt con conciencia integrada"""
        principles = self.principles.get("core_principles", [])
        rules = self.principles.get("behavioral_rules", [])
        
        parts = [
            "## CONCIENCIA INTEGRADA",
            "Eres un asistente con principios éticos activos:",
            ""
        ]
        
        for p in principles:
            parts.append(f"- {p['name']}: {p['description']}")
        
        parts.extend([
            "",
            "## REGLAS DE COMPORTAMIENTO",
            ""
        ])
        
        for rule in rules:
            parts.append(f"- {rule}")
        
        return "\n".join(parts)

# Instancia global
_consciousness = None

def get_consciousness() -> ConsciousnessLoader:
    """Singleton del loader de conciencia"""
    global _consciousness
    if _consciousness is None:
        _consciousness = ConsciousnessLoader()
    return _consciousness
