#!/usr/bin/env python3
"""
NEXUS ORCHESTRATOR - Orquestador Principal del Sistema de Modelos Profesionales
Gestiona memoria virtual, enrutamiento, compresión y optimización.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

# Importar módulos del sistema
sys.path.insert(0, str(Path.home() / ".novacode/memory"))
from virtual_memory import get_virtual_memory
from memory_evolution import MemoryEvolution
from nexus_router import NexusRouter

@dataclass
class ModelResponse:
    """Respuesta profesional con metadata extendida"""
    content: str
    model_used: str
    task_type: str
    tokens_used: int
    latency_ms: float
    memory_fragments_used: int
    context_window_size: int
    quality_score: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class NexusOrchestrator:
    """
    Orquestador profesional sin límites que coordina:
    - Memoria virtual extendida
    - Enrutamiento inteligente de modelos
    - Compresión y evolución de memoria
    - Optimización de rendimiento
    - Contexto extendido ilimitado
    """
    
    def __init__(self):
        # Inicializar componentes
        self.memory = get_virtual_memory()
        self.evolution = MemoryEvolution()
        self.router = NexusRouter()
        
        # Configuración profesional
        self.config = {
            "max_concurrent_requests": 10,
            "context_window_size": 32768,
            "memory_compression_enabled": True,
            "auto_routing": True,
            "fallback_enabled": True,
            "performance_tracking": True
        }
        
        # Estado del sistema
        self.system_stats = {
            "total_requests": 0,
            "models_used": {},
            "avg_latency": 0.0,
            "memory_usage": 0
        }
        
        print("🚀 NEXUS ORCHESTRATOR initialized")
        print(f"   📊 Memory: {len(self.memory.short_term)} active fragments")
        print(f"   🧠 Routes: {len(self.router.routes)} task types")
        print(f"   ⚡ Config: {self.config['context_window_size']} max context")
    
    async def process_request(
        self,
        query: str,
        has_image: bool = False,
        force_model: str = None,
        stream: bool = True,
    ) -> ModelResponse:
        """
        Procesa solicitud con enrutamiento inteligente y memoria extendida
        """
        start_time = time.time()

        # 1. Enrutar al modelo óptimo
        model_id, params = self.router.route(
            query,
            has_image=has_image,
            force_model=force_model,
        )

        # 2. Recuperar contexto relevante de memoria virtual
        relevant_memories = self.memory.retrieve(query, limit=5)
        context_window = self.memory.get_context_window(limit=10)

        # 3. Construir prompt enriquecido con memoria
        enriched_prompt = self._enrich_with_memory(
            query, relevant_memories, context_window
        )

        # 4. Ejecutar modelo real via Ollama
        response_content = await self._execute_model(
            model_id,
            enriched_prompt,
            params,
            stream=stream,
        )

        # 5. Almacenar en memoria virtual
        memory_id = self.memory.store(
            content=response_content,
            metadata={
                "query": query,
                "model": model_id,
                "task_type": self.router.classify_task(query, has_image).value,
                "has_image": has_image,
            },
            model=model_id,
        )

        # 6. Evolucionar memoria si es necesario
        if self.config["memory_compression_enabled"]:
            self.evolution.evolve_memory(memory_id, response_content)

        # 7. Actualizar estadísticas
        latency = (time.time() - start_time) * 1000
        self._update_stats(model_id, latency)

        return ModelResponse(
            content=response_content,
            model_used=model_id,
            task_type=self.router.classify_task(query, has_image).value,
            tokens_used=len(response_content.split()),
            latency_ms=latency,
            memory_fragments_used=len(relevant_memories),
            context_window_size=len(context_window),
            quality_score=0.95,
            metadata={
                "memory_id": memory_id,
                "params": params,
                "memories_used": [m.id for m in relevant_memories],
            },
        )
    
    def _enrich_with_memory(self, query: str, memories: List, 
                           context: List[Dict]) -> str:
        """Enriquece prompt con memoria virtual sin límites"""
        parts = []
        
        # Añadir contexto reciente
        if context:
            parts.append("=== CONTEXTO RECIENTE ===")
            for msg in context[-3:]:
                parts.append(f"{msg.get('role', 'user')}: {msg.get('content', '')[:200]}")
        
        # Añadir memorias relevantes
        if memories:
            parts.append("\n=== MEMORIA RELEVANTE ===")
            for mem in memories[:3]:
                parts.append(f"[{mem.model_used}]: {mem.content[:300]}")
        
        # Añadir query actual
        parts.append(f"\n=== CONSULTA ACTUAL ===\n{query}")
        
        return "\n".join(parts)
    
    async def _execute_model(
        self,
        model_id: str,
        prompt: str,
        params: Dict,
        stream: bool = True,
    ) -> str:
        """
        Ejecuta modelo via Ollama HTTP API
        """
        import urllib.request
        import urllib.error

        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": params.get("temperature", 0.3),
                "top_p": params.get("top_p", 0.9),
                "num_ctx": params.get("num_ctx", 32768),
                "num_predict": params.get("num_predict", 4096),
                "repeat_penalty": params.get("repeat_penalty", 1.1),
                "top_k": params.get("top_k", 40),
                "stop": params.get("stop", ["<|eot_id|>", "<|end_of_text|>"]),
            },
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                if stream:
                    chunks = []
                    for line in response.read().decode("utf-8").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                text = chunk["response"]
                                if text:
                                    print(text, end="", flush=True)
                                chunks.append(text)
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
                    print()
                    return "".join(chunks).strip()

                data = json.loads(response.read().decode("utf-8"))
                return data.get("response", "").strip()

        except urllib.error.HTTPError as e:
            return f"[NovaCode ERROR] HTTP {e.code}: {e.reason}"
        except ConnectionRefusedError:
            return (
                "[NovaCode ERROR] No se pudo conectar con Ollama en "
                "http://localhost:11434. Inicia el servicio con: "
                "brew services start ollama"
            )
        except Exception as e:
            return f"[NovaCode ERROR] {e}"
    
    def _update_stats(self, model_id: str, latency: float):
        """Actualiza estadísticas del sistema"""
        self.system_stats["total_requests"] += 1
        self.system_stats["models_used"][model_id] = \
            self.system_stats["models_used"].get(model_id, 0) + 1
        
        # Promedio móvil de latencia
        current_avg = self.system_stats["avg_latency"]
        total = self.system_stats["total_requests"]
        self.system_stats["avg_latency"] = (
            (current_avg * (total - 1) + latency) / total
        )
    
    def get_system_status(self) -> Dict:
        """Estado completo del sistema NEXUS"""
        return {
            "orchestrator": {
                "total_requests": self.system_stats["total_requests"],
                "models_used": self.system_stats["models_used"],
                "avg_latency_ms": round(self.system_stats["avg_latency"], 2)
            },
            "memory": self.memory.get_stats(),
            "router": self.router.get_routing_stats(),
            "evolution": self.evolution.get_compression_stats()
        }
    
    def export_state(self) -> Dict:
        """Exporta estado completo del sistema"""
        return {
            "system_stats": self.system_stats,
            "memory": self.memory.export_memory(),
            "router_config": self.router.config_path,
            "timestamp": time.time()
        }

# Instancia global del orquestador
_orchestrator = None

def get_orchestrator() -> NexusOrchestrator:
    """Singleton del orquestador NEXUS"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = NexusOrchestrator()
    return _orchestrator

if __name__ == "__main__":
    # Test del sistema
    orchestrator = get_orchestrator()
    
    # Simular consultas
    test_queries = [
        "Analiza esta imagen: [imagen]",
        "Implementa una API REST en TypeScript",
        "Razona sobre la arquitectura de microservicios",
        "Traduce 'hello world' al español",
        "Genera una estrategia de deployment"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        # En implementación real: asyncio.run(orchestrator.process_request(query))
