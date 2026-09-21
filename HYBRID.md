# HYBRID MODE - Sistema Online/Offline

## 🏗️ Arquitectura Híbrida

```
┌─────────────────────────────────────┐
│         HYBRID ROUTER              │
├─────────────────────────────────────┤
│  1. Ollama Local (offline)          │
│  2. Groq (online, gratuita)         │
│  3. Together AI (online)            │
│  4. Fireworks (online)              │
│  5. OpenRouter (online, modelos)    │
└─────────────────────────────────────┘
```

## 🚀 Uso

```bash
# Modo offline (solo local)
~/.novacode/hybrid.sh offline "Analiza esta imagen"

# Modo online (solo APIs)
~/.novacode/hybrid.sh online "Explica quantum computing"

# Modo auto (mejor disponible)
~/.novacode/hybrid.sh auto "Implementa API TypeScript"
```

## 📦 Proveedores Configurados

### Offline (siempre disponible)
- **Ollama Local**: modelos Muse/Nexus en M5
- Sin internet requerido
- Modelos: muse-conscious, nexus-think, nexus-vision, etc.

### Online (requieren API key)
- **Groq**: `GROQ_API_KEY`
- **Together AI**: `TOGETHER_API_KEY`
- **Fireworks**: `FIREWORKS_API_KEY`
- **OpenRouter**: `OPENROUTER_API_KEY`

## ⚙️ Configuración

### Proveedores Online
```bash
# Groq (gratis, rápido)
export GROQ_API_KEY="tu_key_aquí"

# Together AI
export TOGETHER_API_KEY="tu_key_aquí"

# Fireworks
export FIREWORKS_API_KEY="tu_key_aquí"

# OpenRouter
export OPENROUTER_API_KEY="tu_key_aquí"
```

### Habilitar proveedor
Editar `~/.novacode/hybrid/providers.json`:
```json
{
  "providers": {
    "groq": {
      "enabled": true,
      "env_key": "GROQ_API_KEY"
    }
  }
}
```

## 🔄 Routing Automático

1. **Preferencia local**: Siempre intenta offline primero
2. **Fallback online**: Si local falla, usa APIs
3. **Timeouts**: 60s por defecto
4. **Reintentos**: Automáticos

## 🎯 Modelos por Proveedor

| Tarea | Offline | Groq | Together | Fireworks | OpenRouter |
|-------|---------|------|----------|-----------|------------|
| Multimodal | muse-conscious | - | Llama-3.2-90B-Vision | - | Gemini-2.0 |
| Código | muse-code-offline | Llama-3.3-70B | Qwen2.5-Coder-32B | Llama-3.2-70B | Llama-3.2-70B |
| Rápido | nexus-fast | Llama-3.3-70B | Llama-3.2-3B | Llama-3.2-3B | Gemini-2.0 |
| General | nexus-think | Llama-3.3-70B | Llama-3.2-90B | Llama-3.2-70B | Llama-3.2-70B |

## ✅ Ventajas Híbridas

- **Offline garantizado**: Funciona sin internet
- **Online potenciado**: Modelos más grandes cuando hay conexión
- **Sin dependencias**: No requiere siempre APIs externas
- **Routing inteligente**: Mejor proveedor por tarea
- **Fallback automático**: Si uno falla, usa otro
- **Consciencia ética**: Misma en todos los modos

## 🔧 Troubleshooting

```bash
# Verificar estado de proveedores
python3 ~/.novacode/hybrid/hybrid_ollama.py

# Reiniciar Ollama
brew services restart ollama

# Forzar offline
~/.novacode/hybrid.sh offline "test"
```
