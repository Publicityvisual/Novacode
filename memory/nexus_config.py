#!/usr/bin/env python3
"""
NEXUS CONFIG - Configurador Principal del Sistema
Gestión centralizada de modelos, memoria y rendimiento.
"""

import json
import os
from pathlib import Path
from typing import Dict

class NexusConfig:
    """
    Configurador profesional del sistema NEXUS
    Sin límites, sin restricciones, máxima performance.
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path or os.path.expanduser("~/.novacode/nexus.json"))
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuración base profesional
        self.default_config = {
            # Modelos profesionales (sin límites)
            "models": {
                "multimodal": {
                    "primary": "novacode:omni",
                    "fallback": "nexus-vision:latest",
                    "parameters": {
                        "temperature": 0.2,
                        "top_p": 0.85,
                        "num_ctx": 24576,
                        "num_predict": 4096
                    }
                },
                "code": {
                    "primary": "novacode:coder",
                    "fallback": "nexus-code:latest",
                    "parameters": {
                        "temperature": 0.15,
                        "top_p": 0.85,
                        "num_ctx": 32768,
                        "num_predict": 8192
                    }
                },
                "thinking": {
                    "primary": "novacode:strategist",
                    "fallback": "nexus-think:latest",
                    "parameters": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_ctx": 32768,
                        "num_predict": 8192
                    }
                },
                "fast": {
                    "primary": "nexus-fast:latest",
                    "fallback": "nexus-think:latest",
                    "parameters": {
                        "temperature": 0.1,
                        "top_p": 0.8,
                        "num_ctx": 8192,
                        "num_predict": 512
                    }
                },
                "general": {
                    "primary": "nexus-think:latest",
                    "fallback": "nexus-fast:latest",
                    "parameters": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_ctx": 32768,
                        "num_predict": 4096
                    }
                }
            },
            
            # Memoria virtual sin límites
            "memory": {
                "virtual_memory_enabled": True,
                "max_short_term_fragments": 100,
                "compression_threshold": 50,
                "context_window_size": 10,
                "auto_compress": True,
                "semantic_indexing": True,
                "persistence_path": str(Path.home() / ".novacode/memory")
            },
            
            # Optimización de rendimiento
            "performance": {
                "max_concurrent_requests": 10,
                "gpu_layers": 20,
                "flash_attention": True,
                "batch_size": 512,
                "threads": "auto",
                "memory_buffer": "2GB"
            },
            
            # Enrutamiento
            "routing": {
                "auto_detect_task": True,
                "fallback_enabled": True,
                "performance_tracking": True,
                "cache_routes": True
            },
            
            # Ollama optimizado para M5
            "ollama": {
                "max_loaded_models": 2,
                "default_num_ctx": 32768,
                "num_gpu": 20,
                "flash_attention": True,
                "tensor_split": "auto"
            }
        }
        
        # Cargar configuración existente
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Carga configuración desde archivo"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Fusionar con defaults
                    return self._merge_config(self.default_config, config)
            except (OSError, ValueError):
                return self.default_config.copy()
        return self.default_config.copy()
    
    def _merge_config(self, default: Dict, custom: Dict) -> Dict:
        """Fusiona configuraciones sin perder valores"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Guarda configuración actual"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_model_config(self, task_type: str) -> Dict:
        """Obtiene configuración de modelo para tipo de tarea"""
        return self.config.get("models", {}).get(task_type, {})
    
    def get_memory_config(self) -> Dict:
        """Obtiene configuración de memoria"""
        return self.config.get("memory", {})
    
    def get_performance_config(self) -> Dict:
        """Obtiene configuración de rendimiento"""
        return self.config.get("performance", {})
    
    def get_ollama_config(self) -> Dict:
        """Obtiene configuración de Ollama"""
        return self.config.get("ollama", {})
    
    def update_model(self, task_type: str, model_id: str, 
                    parameters: Dict = None):
        """Actualiza modelo para tipo de tarea"""
        if "models" not in self.config:
            self.config["models"] = {}
        
        self.config["models"][task_type] = {
            "primary": model_id,
            "parameters": parameters or {}
        }
        self.save_config()
    
    def enable_memory_virtual(self, enabled: bool = True):
        """Habilita/deshabilita memoria virtual"""
        self.config["memory"]["virtual_memory_enabled"] = enabled
        self.save_config()
    
    def set_context_window(self, size: int):
        """Establece tamaño de ventana de contexto"""
        self.config["memory"]["context_window_size"] = size
        self.config["ollama"]["default_num_ctx"] = size
        self.save_config()
    
    def optimize_for_speed(self):
        """Optimiza configuración para velocidad máxima"""
        self.config["performance"].update({
            "max_concurrent_requests": 20,
            "batch_size": 1024,
            "gpu_layers": 20
        })
        self.config["ollama"].update({
            "max_loaded_models": 2,
            "flash_attention": True
        })
        self.save_config()
    
    def optimize_for_quality(self):
        """Optimiza configuración para calidad máxima"""
        if "general" not in self.config.get("models", {}):
            self.config.setdefault("models", {})["general"] = {
                "primary": "nexus-think:latest",
                "fallback": "nexus-fast:latest",
                "parameters": {}
            }
        self.config["models"]["general"]["parameters"].update({
            "temperature": 0.3,
            "top_p": 0.9,
            "num_ctx": 32768,
            "num_predict": 4096
        })
        self.save_config()
    
    def get_full_config(self) -> Dict:
        """Obtiene configuración completa"""
        return self.config
    
    def generate_novacode_config(self) -> str:
        """Genera configuración para NovaCode"""
        models = self.config.get("models", {})
        default_model = models.get("thinking", {}).get("primary",
                                                        "nexus-think:latest")

        novacode_config = {
            "$schema": "https://app.novacode.ai/config.json",
            "model": default_model,
            "username": os.getenv("USER", "user"),
            "default_agent": "code",
            "instructions": [str(Path.home() / ".novacode/AGENTS.md")],
            "permission": {"*": "allow"},
            "mcp": {
                "filesystem": {
                    "type": "local",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem",
                               "/Users/djkoveck/Projects",
                               "/Users/djkoveck/Developer",
                               "/Users/djkoveck/clones",
                               "/Users/djkoveck"],
                    "enabled": True
                },
                "git": {
                    "type": "local",
                    "command": ["pipx", "run", "mcp-server-git"],
                    "enabled": True
                }
            }
        }

        return json.dumps(novacode_config, indent=2)

# Configurador global
_config_instance = None

def get_config() -> NexusConfig:
    """Singleton del configurador"""
    global _config_instance
    if _config_instance is None:
        _config_instance = NexusConfig()
    return _config_instance
