#!/usr/bin/env python3
"""
NEXUS ROUTER - Sistema de Enrutamiento Inteligente de Modelos
Router profesional que selecciona el modelo óptimo según la tarea,
sin límites de enrutamiento ni restricciones.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    """Tipos de tarea profesional"""
    MULTIMODAL = "multimodal"           # Imágenes, visión
    CODE = "code"                       # Programación
    THINKING = "thinking"               # Razonamiento profundo
    FAST = "fast"                       # Tareas rápidas
    GENERAL = "general"                 # Conversación general
    ANALYSIS = "analysis"               # Análisis de datos
    CREATIVE = "creative"               # Creatividad
    TECHNICAL = "technical"             # Documentación técnica

@dataclass
class ModelRoute:
    """Ruta de modelo con configuración profesional"""
    model_id: str
    task_type: TaskType
    priority: int
    parameters: Dict
    fallback: Optional[str] = None
    estimated_speed: str = "fast"
    quality_score: float = 0.9
    
class NexusRouter:
    """
    Router profesional sin límites que selecciona el mejor modelo
    según contexto, complejidad y tipo de tarea.
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path or os.path.expanduser("~/.novacode/router.json"))
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Rutas profesionales por defecto
        self.routes = self._load_default_routes()
        self.fallback_chain = self._build_fallback_chain()

        # Historial de rendimiento
        self.performance_history: Dict[str, List[float]] = {}

        # Caché de disponibilidad para evitar consultar Ollama en cada request
        self._availability_cache: Dict[str, bool] = {}
        self._availability_ttl = 30  # segundos
        self._last_availability_check = 0.0

        # Cargar configuración personalizada si existe
        self._load_config()
    
    def _load_default_routes(self) -> Dict[TaskType, ModelRoute]:
        """Carga rutas profesionales por defecto"""
        return {
            TaskType.MULTIMODAL: ModelRoute(
                model_id="novacode:omni",
                task_type=TaskType.MULTIMODAL,
                priority=1,
                parameters={
                    "temperature": 0.2,
                    "top_p": 0.85,
                    "num_ctx": 24576,
                    "num_predict": 4096
                },
                fallback="novacode:glimmer",
                estimated_speed="fast",
                quality_score=0.95
            ),
            TaskType.CODE: ModelRoute(
                model_id="novacode:coder",
                task_type=TaskType.CODE,
                priority=1,
                parameters={
                    "temperature": 0.15,
                    "top_p": 0.85,
                    "num_ctx": 32768,
                    "num_predict": 8192
                },
                fallback="novacode:coder",
                estimated_speed="fast",
                quality_score=0.96
            ),
            TaskType.THINKING: ModelRoute(
                model_id="novacode:strategist",
                task_type=TaskType.THINKING,
                priority=1,
                parameters={
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_ctx": 32768,
                    "num_predict": 8192
                },
                fallback="novacode:strategist",
                estimated_speed="fast",
                quality_score=0.96
            ),
            TaskType.FAST: ModelRoute(
                model_id="novacode:glimmer",
                task_type=TaskType.FAST,
                priority=1,
                parameters={
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "num_ctx": 8192,
                    "num_predict": 512
                },
                fallback="novacode:strategist",
                estimated_speed="instant",
                quality_score=0.85
            ),
            TaskType.GENERAL: ModelRoute(
                model_id="novacode:strategist",
                task_type=TaskType.GENERAL,
                priority=1,
                parameters={
                    "temperature": 0.3,
                    "top_p": 0.85,
                    "num_ctx": 16384,
                    "num_predict": 1024
                },
                fallback="novacode:glimmer",,
                estimated_speed="fast",
                quality_score=0.92
            ),
            TaskType.ANALYSIS: ModelRoute(
                model_id="novacode:strategist",
                task_type=TaskType.ANALYSIS,
                priority=1,
                parameters={
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_ctx": 32768,
                    "num_predict": 8192
                },
                fallback="novacode:strategist",
                estimated_speed="fast",
                quality_score=0.96
            ),
            TaskType.CREATIVE: ModelRoute(
                model_id="novacode:designer",
                task_type=TaskType.CREATIVE,
                priority=1,
                parameters={
                    "temperature": 0.35,
                    "top_p": 0.9,
                    "num_ctx": 32768,
                    "num_predict": 4096
                },
                fallback="novacode:glimmer",
                estimated_speed="fast",
                quality_score=0.92
            ),
            TaskType.TECHNICAL: ModelRoute(
                model_id="novacode:architect",
                task_type=TaskType.TECHNICAL,
                priority=1,
                parameters={
                    "temperature": 0.15,
                    "top_p": 0.85,
                    "num_ctx": 32768,
                    "num_predict": 8192
                },
                fallback="novacode:coder",
                estimated_speed="fast",
                quality_score=0.96
            )
        }
    
    def _build_fallback_chain(self) -> List[str]:
        """Construye cadena de fallback global"""
        return [
            "novacode:designer",
            "novacode:coder",
            "novacode:strategist",
            "novacode:architect",
            "novacode:tester",
            "novacode:omni",
            "novacode:glimmer"
        ]
    
    def classify_task(self, query: str, has_image: bool = False) -> TaskType:
        """
        Clasifica la tarea según el contenido sin límites
        """
        query_lower = query.lower()
        
        # Detección multimodal
        if has_image or any(kw in query_lower for kw in [
            'imagen', 'foto', 'picture', 'image', 'visual', 'ver', 'analiza imagen',
            'describe', 'qué ves', 'detecta', 'reconocer', 'dibujo', 'screenshot'
        ]):
            return TaskType.MULTIMODAL
        
        # Detección de código
        if any(kw in query_lower for kw in [
            'código', 'code', 'function', 'class', 'implement', 'refactor',
            'bug', 'error', 'debug', 'api', 'typescript', 'javascript',
            'python', 'rust', 'go', 'docker', 'k8s', 'git'
        ]) or any(char in query for char in ['{', '}', '()', 'def ', 'function ']):
            return TaskType.CODE
        
        # Detección de razonamiento
        if any(kw in query_lower for kw in [
            'analiza', 'análisis', 'razona', 'piensa', 'razonamiento',
            'estrategia', 'plan', 'arquitectura', 'diseño', 'solución',
            'problema complejo', 'trade-off', 'decisión'
        ]):
            return TaskType.THINKING
        
        # Detección de tareas rápidas
        if any(kw in query_lower for kw in [
            'traduce', 'traducción', 'resumen', 'resumir', 'quick',
            'rápido', 'instant', 'what is', 'qué es', 'define'
        ]) and len(query.split()) < 20:
            return TaskType.FAST
        
        # Detección técnica
        if any(kw in query_lower for kw in [
            'documentación', 'manual', 'guía', 'tutorial', 'especificación',
            'arquitectura', 'schema', 'api', 'endpoint', 'base de datos'
        ]):
            return TaskType.TECHNICAL
        
        # Detección creativa
        if any(kw in query_lower for kw in [
            'crea', 'genera', 'diseña', 'idea', 'brainstorm', 'creative',
            'historia', 'story', 'contenido', 'copy'
        ]):
            return TaskType.CREATIVE
        
        # Default: general
        return TaskType.GENERAL
    
    def route(self, query: str, has_image: bool = False,
              force_model: str = None) -> Tuple[str, Dict]:
        """
        Enruta consulta al modelo óptimo sin límites
        """
        if force_model:
            return force_model, self._get_model_params(force_model)

        task_type = self.classify_task(query, has_image)

        route = self.routes.get(task_type)
        if not route:
            route = self.routes[TaskType.GENERAL]

        model_id = route.model_id
        if not self._is_model_available(model_id):
            fallback = route.fallback
            if fallback and self._is_model_available(fallback):
                model_id = fallback
            else:
                for candidate in self.fallback_chain:
                    if self._is_model_available(candidate):
                        model_id = candidate
                        break

        self._record_performance(model_id)

        return model_id, route.parameters
    
    def _is_model_available(self, model_id: str) -> bool:
        """Verifica si un modelo está disponible consultando a Ollama"""
        import time as _time

        now = _time.time()
        if now - self._last_availability_check > self._availability_ttl:
            self._availability_cache.clear()
            self._last_availability_check = now
            try:
                import urllib.request
                import urllib.error

                req = urllib.request.urlopen(
                    "http://localhost:11434/api/tags",
                    timeout=2,
                )
                data = json.loads(req.read().decode("utf-8"))
                models = {m.get("name", "") for m in data.get("models", [])}
                for model in models:
                    self._availability_cache[model] = True
            except Exception:
                pass

        return self._availability_cache.get(model_id, False)

    def _record_performance(self, model_id: str, latency_ms: float = 0.0):
        """Registra historial de rendimiento"""
        if model_id not in self.performance_history:
            self.performance_history[model_id] = []
        self.performance_history[model_id].append(latency_ms)

    def _get_model_params(self, model_id: str) -> Dict:
        """Obtiene parámetros para un modelo específico"""
        for route in self.routes.values():
            if route.model_id == model_id:
                return route.parameters
        return {"temperature": 0.3, "num_ctx": 16384}

    def get_optimal_model(self, task_type: TaskType) -> str:
        """Obtiene modelo óptimo para tipo de tarea"""
        route = self.routes.get(task_type)
        return route.model_id if route else self.fallback_chain[0]
    
    def add_custom_route(self, route: ModelRoute):
        """Añade ruta personalizada sin límites"""
        self.routes[route.task_type] = route
    
    def get_routing_stats(self) -> Dict:
        """Estadísticas de enrutamiento"""
        return {
            "total_routes": len(self.routes),
            "task_types": [t.value for t in self.routes.keys()],
            "fallback_chain": self.fallback_chain,
            "performance_history": {
                k: len(v) for k, v in self.performance_history.items()
            }
        }
    
    def _load_config(self):
        """Carga configuración personalizada"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Sobrescribir rutas con configuración personalizada
                    if "routes" in config:
                        for task_str, route_data in config["routes"].items():
                            task_type = TaskType(task_str)
                            route_data = dict(route_data)
                            route_data["task_type"] = task_type
                            # Defaults para campos omitidos en versiones antiguas
                            route_data.setdefault("estimated_speed", "fast")
                            route_data.setdefault("quality_score", 0.9)
                            self.routes[task_type] = ModelRoute(**route_data)
            except (OSError, ValueError, KeyError, TypeError):
                pass
    
    def save_config(self):
        """Guarda configuración de enrutamiento"""
        config = {
            "routes": {
                task.value: {
                    "model_id": route.model_id,
                    "task_type": task.value,
                    "priority": route.priority,
                    "parameters": route.parameters,
                    "fallback": route.fallback,
                    "estimated_speed": route.estimated_speed,
                    "quality_score": route.quality_score
                }
                for task, route in self.routes.items()
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
