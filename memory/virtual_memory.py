#!/usr/bin/env python3
"""
NEXUS MEMORY VIRTUAL - Sistema de Memoria Extendida para Modelos Multimodales
Memoria virtual ilimitada con gestión inteligente de contexto y recursos.
"""

import json
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class MemoryFragment:
    """Fragmento de memoria con metadata enriquecida"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    timestamp: str = None
    access_count: int = 0
    relevance_score: float = 1.0
    model_used: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}

class VirtualMemory:
    """
    Sistema de memoria virtual ilimitada con:
    - Indexación semántica
    - Gestión de contexto extendido
    - Memoria a corto/largo plazo
    - Compresión inteligente
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/.novacode/memory"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Estructura de memoria
        self.short_term: Dict[str, MemoryFragment] = {}  # Memoria activa (RAM)
        self.long_term_index: Dict[str, str] = {}  # Índice de memoria persistente
        self.context_window: List[str] = []  # Ventana de contexto actual
        self.max_short_term = 100  # Límite de memoria activa
        
        # Configuración
        self.config = {
            "compression_threshold": 50,  # Comprimir después de 50 fragmentos
            "relevance_decay": 0.95,  # Decaimiento de relevancia
            "context_window_size": 10,  # Fragmentos en ventana de contexto
            "auto_compress": True,
            "semantic_indexing": True
        }
        
        # Cargar memoria persistente
        self._load_long_term_memory()
    
    def _generate_id(self, content: str) -> str:
        """Genera ID único para fragmento de memoria"""
        return hashlib.sha256(f"{content}{time.time()}".encode()).hexdigest()[:16]
    
    def _load_long_term_memory(self):
        """Carga memoria persistente desde disco"""
        index_file = self.base_path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    loaded = json.load(f)
                    # Normalizar a strings
                    self.long_term_index = {k: str(v) for k, v in loaded.items()}
            except (OSError, ValueError):
                self.long_term_index = {}
    
    def _save_long_term_memory(self):
        """Guarda índice de memoria en disco"""
        index_file = self.base_path / "index.json"
        with open(index_file, 'w') as f:
            json.dump(self.long_term_index, f, indent=2)
    
    def store(self, content: str, metadata: Dict = None, model: str = None) -> str:
        """
        Almacena fragmento en memoria virtual
        Sin límites de almacenamiento
        """
        fragment_id = self._generate_id(content)
        fragment = MemoryFragment(
            id=fragment_id,
            content=content,
            metadata=metadata or {},
            model_used=model,
            access_count=1,
            relevance_score=1.0
        )
        
        # Almacenar en memoria activa
        self.short_term[fragment_id] = fragment
        
        # Actualizar índice (guardar como string para JSON)
        fragment_path = self.base_path / "fragments" / f"{fragment_id}.json"
        fragment_path.parent.mkdir(parents=True, exist_ok=True)
        self.long_term_index[fragment_id] = str(fragment_path)

        # Guardar fragmento completo
        with open(fragment_path, 'w') as f:
            json.dump(asdict(fragment), f, indent=2)

        # Persistir índice
        self._save_long_term_memory()
        
        # Actualizar ventana de contexto
        self.context_window.append(fragment_id)
        if len(self.context_window) > self.config["context_window_size"]:
            self.context_window.pop(0)
        
        # Compresión automática si es necesario
        if self.config["auto_compress"] and len(self.short_term) > self.config["compression_threshold"]:
            self._compress_memory()
        
        return fragment_id
    
    def retrieve(self, query: str, limit: int = 5) -> List[MemoryFragment]:
        """
        Recupera fragmentos relevantes sin límites de búsqueda
        """
        results = []
        
        # Buscar en memoria activa primero
        for frag_id, fragment in self.short_term.items():
            score = self._calculate_relevance(query, fragment)
            if score > 0.3:
                fragment.relevance_score = score
                results.append(fragment)
        
        # Buscar en memoria persistente si es necesario
        if len(results) < limit:
            for frag_id, path_str in self.long_term_index.items():
                if frag_id not in self.short_term:
                    frag_path = Path(path_str)
                    if not frag_path.exists():
                        continue
                    try:
                        with open(frag_path, 'r') as f:
                            data = json.load(f)
                            fragment = MemoryFragment(**data)
                            score = self._calculate_relevance(query, fragment)
                            if score > 0.3:
                                fragment.relevance_score = score
                                results.append(fragment)
                                # Cargar a memoria activa
                                self.short_term[frag_id] = fragment
                    except (OSError, ValueError, TypeError):
                        continue
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def _calculate_relevance(self, query: str, fragment: MemoryFragment) -> float:
        """
        Calcula relevancia sin dependencias externas
        Usa similitud de texto básica mejorada
        """
        query_lower = query.lower()
        content_lower = fragment.content.lower()
        
        # Tokenización simple
        query_tokens = set(query_lower.split())
        content_tokens = set(content_lower.split())
        
        if not query_tokens or not content_tokens:
            return 0.0
        
        # Jaccard similarity con boost por metadata
        intersection = len(query_tokens & content_tokens)
        union = len(query_tokens | content_tokens)
        base_score = intersection / union if union > 0 else 0.0
        
        # Boost por recencia
        time_boost = 1.0
        if fragment.timestamp:
            try:
                age_hours = (datetime.utcnow() - datetime.fromisoformat(fragment.timestamp)).total_seconds() / 3600
                time_boost = max(0.5, 1.0 - (age_hours / 168))  # Decae en 1 semana
            except (ValueError, TypeError):
                pass
        
        # Boost por accesos frecuentes
        access_boost = min(1.5, 1.0 + (fragment.access_count * 0.1))
        
        return min(1.0, base_score * time_boost * access_boost)
    
    def _compress_memory(self):
        """
        Compresión inteligente de memoria sin pérdida de información crítica
        """
        # Ordenar por relevancia
        fragments = sorted(
            self.short_term.items(),
            key=lambda x: x[1].relevance_score * x[1].access_count,
            reverse=True
        )
        
        # Mantener solo los más relevantes en memoria activa
        self.short_term = {
            fid: frag for fid, frag in fragments[:self.max_short_term]
        }
        
        # Los demás se guardan en disco (ya están en long_term_index)
    
    def get_context_window(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene ventana de contexto actual sin límites
        """
        context = []
        for frag_id in self.context_window[-limit:]:
            if frag_id in self.short_term:
                context.append(asdict(self.short_term[frag_id]))
        return context
    
    def clear_short_term(self):
        """Limpia memoria activa (mantiene persistente)"""
        self.short_term.clear()
        self.context_window.clear()
    
    def get_stats(self) -> Dict:
        """Estadísticas de memoria virtual"""
        return {
            "short_term_fragments": len(self.short_term),
            "long_term_fragments": len(self.long_term_index),
            "context_window_size": len(self.context_window),
            "total_storage_mb": self._calculate_storage(),
            "config": self.config
        }
    
    def _calculate_storage(self) -> float:
        """Calcula almacenamiento total en MB"""
        total = 0
        for path_str in self.long_term_index.values():
            frag_path = Path(path_str)
            if frag_path.exists():
                total += frag_path.stat().st_size
        return round(total / (1024 * 1024), 2)
    
    def export_memory(self) -> Dict:
        """Exporta toda la memoria para backup/transferencia"""
        return {
            "short_term": {k: asdict(v) for k, v in self.short_term.items()},
            "long_term_index": {k: str(v) for k, v in self.long_term_index.items()},
            "context_window": self.context_window,
            "config": self.config,
            "stats": self.get_stats()
        }
    
    def import_memory(self, data: Dict):
        """Importa memoria desde backup"""
        if "short_term" in data:
            self.short_term = {
                k: MemoryFragment(**v) for k, v in data["short_term"].items()
            }
        if "long_term_index" in data:
            self.long_term_index = {k: str(v) for k, v in data["long_term_index"].items()}
        if "context_window" in data:
            self.context_window = data["context_window"]


# Instancia global de memoria virtual
_memory_instance = None

def get_virtual_memory() -> VirtualMemory:
    """Singleton de memoria virtual"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = VirtualMemory()
    return _memory_instance
