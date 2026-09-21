# HYBRID AI SYSTEM - Online + Offline

## 🏗️ Arquitectura

```
         ┌──────────────────────┐
         │   HYBRID ROUTER     │
         └──────────┬───────────┘
                    │
     ┌──────────────┼──────────────┐
     │              │              │
  OFFLINE        ONLINE        FALLBACK
  (Ollama)     (APIs)        (Local)
```

## ✅ Estado Actual

### Offline (siempre activo)
- **22 modelos** locales en Ollama
- **Muse/Nexus** con conciencia ética
- **100% autónomo**, sin internet
- **Multimodal**: visión + texto

### Online (configurable)
- **Groq**: API key opcional
- **Together AI**: API key opcional
- **Fireworks**: API key opcional
- **OpenRouter**: API key opcional

## 🚀 Uso

```bash
# OFFLINE - Solo local
~/.novacode/hybrid.sh offline "Implementa API TypeScript"

# ONLINE - Solo APIs (si están configuradas)
~/.novacode/hybrid.sh online "Explica quantum computing"

# AUTO - Mejor proveedor disponible
~/.novacode/hybrid.sh auto "Analiza esta imagen"
```

## ⚙️ Configuración Online (opcional)

```bash
# 1. Editar providers.json
nano ~/.novacode/hybrid/providers.json

# 2. Habilitar proveedor
{
  "providers": {
    "groq": { "enabled": true }
  }
}

# 3. Configurar API key
export GROQ_API_KEY="tu_key_aquí"

# 4. Usar modo auto
~/.novacode/hybrid.sh auto "tu prompt"
```

## 🎯 Características

- ✅ Offline garantizado (22 modelos)
- ✅ Online potenciado (APIs configurables)
- ✅ Routing automático por tarea
- ✅ Conciencia ética en ambos modos
- ✅ Memoria virtual sin límites
- ✅ Sin dependencias obligatorias

## 📊 Comparación

| Modo | Internet | Modelos | Privacidad | Velocidad |
|------|----------|---------|------------|-----------|
| Offline | ❌ No | 19 locales | ✅ Total | ⚡ Rápido |
| Online | ✅ Sí | Infinitos | ⚠️ Varía | 🚀 Variable |
| Híbrido | 🔄 Auto | 19+ APIs | ✅ Local | ⚡ Mejor |

## 🔧 Verificar Estado

```bash
# Estado de proveedores
python3 ~/.novacode/hybrid/hybrid_ollama.py

# Test offline
~/.novacode/hybrid.sh offline "test"

# Test auto
~/.novacode/hybrid.sh auto "test"
```

El sistema funciona **online cuando hay conexión, offline cuando no**, con la misma conciencia ética en ambos modos.
