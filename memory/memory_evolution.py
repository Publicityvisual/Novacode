#!/usr/bin/env python3
"""
NEXUS MEMORY MANAGER - Gestor de Memoria Extendida
Compresión, evolución y orquestación de memoria para modelos profesionales.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import re

@dataclass
class CompressedMemory:
    """Memoria comprimida con metadatos de evolución"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    content: str
    metadata: Dict[str, Any]
    timestamp: str
    model_signature: str
    evolution_stage: int  # 0=raw, 1=compressed, 2=synthesized
    
class MemoryEvolution:
    """
    Sistema de evolución de memoria que comprime y sintetiza
    recuerdos sin perder información crítica.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/.novacode/memory"))
        self.evolution_path = self.base_path / "evolution"
        self.evolution_path.mkdir(parents=True, exist_ok=True)
        
        self.compression_levels = {
            0: {"name": "raw", "threshold": 50, "action": "compress"},
            1: {"name": "compressed", "threshold": 200, "action": "synthesize"},
            2: {"name": "synthesized", "threshold": 1000, "action": "archive"}
        }
    
    def evolve_memory(self, memory_id: str, content: str) -> CompressedMemory:
        """
        Evoluciona un fragmento de memoria según su etapa
        """
        current_stage = self._get_stage(memory_id)
        if current_stage not in self.compression_levels:
            current_stage = 0
        
        if current_stage == 0:
            return self._compress_to_stage1(memory_id, content)
        elif current_stage == 1:
            return self._synthesize_to_stage2(memory_id, content)
        else:
            return self._archive_to_stage3(memory_id, content)
    
    def _compress_to_stage1(self, memory_id: str, content: str) -> CompressedMemory:
        """Comprime contenido crudo"""
        # Extraer información clave (sin pérdida de significado)
        sentences = content.split('.')
        key_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            # Mantener oraciones con datos concretos, decisiones, código
            if any(keyword in sentence.lower() for keyword in [
                'decisión', 'decidió', 'implementó', 'creó', 'eliminó',
                'configuró', 'error', 'solución', 'importante', 'crítico',
                'function', 'class', 'const', 'import', 'return', 'def '
            ]):
                key_sentences.append(sentence)
            elif len(key_sentences) < 3:
                key_sentences.append(sentence)
        
        compressed = '. '.join(key_sentences[:5])  # Máximo 5 oraciones clave
        
        return CompressedMemory(
            original_size=len(content),
            compressed_size=len(compressed),
            compression_ratio=len(compressed) / len(content) if content else 0,
            content=compressed,
            metadata={"stage": 1, "compression_date": datetime.utcnow().isoformat()},
            timestamp=datetime.utcnow().isoformat(),
            model_signature="compressed_v1",
            evolution_stage=1
        )
    
    def _synthesize_to_stage2(self, memory_id: str, content: str) -> CompressedMemory:
        """Sintetiza contenido comprimido en conocimiento abstracto"""
        # Extraer conceptos fundamentales
        words = re.findall(r'\b[a-zA-Záéíóúñ]+\b', content.lower())
        word_freq = defaultdict(int)
        for word in words:
            if len(word) > 3:
                word_freq[word] += 1
        
        # Top conceptos
        top_concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        synthesis = f"CONCEPTOS: {', '.join([c[0] for c in top_concepts])}"
        
        return CompressedMemory(
            original_size=len(content),
            compressed_size=len(synthesis),
            compression_ratio=len(synthesis) / len(content) if content else 0,
            content=synthesis,
            metadata={"stage": 2, "synthesis_date": datetime.utcnow().isoformat()},
            timestamp=datetime.utcnow().isoformat(),
            model_signature="synthesized_v2",
            evolution_stage=2
        )
    
    def _archive_to_stage3(self, memory_id: str, content: str) -> CompressedMemory:
        """Archiva contenido sintetizado para almacenamiento permanente"""
        archive = f"[ARCHIVED:{memory_id}] {content[:100]}..."
        
        return CompressedMemory(
            original_size=len(content),
            compressed_size=len(archive),
            compression_ratio=len(archive) / len(content) if content else 0,
            content=archive,
            metadata={"stage": 3, "archive_date": datetime.utcnow().isoformat()},
            timestamp=datetime.utcnow().isoformat(),
            model_signature="archived_v3",
            evolution_stage=3
        )
    
    def _get_stage(self, memory_id: str) -> int:
        """Obtiene etapa actual de memoria"""
        stage_file = self.evolution_path / f"{memory_id}_stage.json"
        if stage_file.exists():
            try:
                with open(stage_file, 'r') as f:
                    data = json.load(f)
                    return data.get("stage", 0)
            except (OSError, ValueError):
                return 0
        return 0
    
    def save_evolution(self, memory_id: str, compressed: CompressedMemory):
        """Guarda memoria evolucionada"""
        stage_file = self.evolution_path / f"{memory_id}_stage.json"
        with open(stage_file, 'w') as f:
            json.dump({
                "stage": compressed.evolution_stage,
                "content": compressed.content,
                "metadata": compressed.metadata,
                "timestamp": compressed.timestamp
            }, f, indent=2)
    
    def get_compression_stats(self) -> Dict:
        """Estadísticas de compresión"""
        stats = {"total_files": 0, "stages": defaultdict(int), "space_saved": 0}
        
        for stage_file in self.evolution_path.glob("*_stage.json"):
            try:
                with open(stage_file, 'r') as f:
                    data = json.load(f)
                    stats["total_files"] += 1
                    stats["stages"][data.get("stage", 0)] += 1
                    if "original_size" in data:
                        stats["space_saved"] += data["original_size"] - len(data["content"])
            except (OSError, ValueError):
                continue
        
        return stats


class ContextManager:
    """
    Gestor de contexto extendido que simula ventanas de contexto infinitas
    mediante compresión y recuperación inteligente.
    """
    
    def __init__(self, max_context: int = 32768):
        self.max_context = max_context
        self.current_context: List[Dict] = []
        self.context_compression_threshold = max_context * 0.8
    
    def add_to_context(self, message: Dict, memory_manager):
        """
        Añade mensaje al contexto con gestión automática de tamaño
        """
        self.current_context.append(message)
        
        # Si el contexto supera el umbral, comprimir
        if len(self._tokenize_context()) > self.context_compression_threshold:
            self._compress_context(memory_manager)
    
    def _tokenize_context(self) -> int:
        """Estima tokens en contexto actual"""
        total_chars = sum(len(str(msg)) for msg in self.current_context)
        return total_chars // 4  # Estimación: 4 caracteres por token
    
    def _compress_context(self, memory_manager):
        """
        Comprime contexto antiguo en memoria persistente
        """
        if len(self.current_context) < 10:
            return
        
        # Separar contexto reciente (últimos 10 mensajes) del antiguo
        recent = self.current_context[-10:]
        old_context = self.current_context[:-10]
        
        # Comprimir contexto antiguo
        compressed = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')[:200]}"
            for msg in old_context
        ])
        
        # Almacenar comprimido en memoria virtual
        memory_manager.store(
            content=f"[CONTEXTO COMPRIMIDO]\n{compressed}",
            metadata={"type": "compressed_context", "messages_count": len(old_context)}
        )
        
        # Mantener solo contexto reciente
        self.current_context = recent
    
    def get_context_window(self, window_size: int = 20) -> List[Dict]:
        """Obtiene ventana de contexto optimizada"""
        return self.current_context[-window_size:]
    
    def expand_context(self, memory_manager, query: str) -> List[Dict]:
        """
        Expande contexto con memoria relevante (sin límites)
        """
        # Recuperar memorias relevantes
        relevant_memories = memory_manager.retrieve(query, limit=5)
        
        # Integrar en contexto
        expanded = self.current_context.copy()
        for mem in relevant_memories:
            expanded.append({
                "role": "system",
                "content": f"[MEMORIA RELEVANTE]\n{mem.content}"
            })
        
        return expanded
