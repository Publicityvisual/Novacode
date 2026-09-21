# HYBRID MODE - Online + Offline

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

## 🚀 Uso Inmediato

```bash
# OFFLINE - Sin internet, modelos locales
~/.novacode/hybrid.sh offline "Implementa API TypeScript"

# ONLINE - Con APIs configuradas
~/.novacode/hybrid.sh online "Explica arquitectura cloud"

# AUTO - Mejor opción disponible
~/.novacode/hybrid.sh auto "Analiza esta imagen: [imagen]"
```

## 📦 Stack Offline (siempre disponible)

| Modelo | Tamaño | Función |
|--------|--------|---------|
| `muse-conscious` | 5.5 GB | Multimodal consciente |
| `muse-code-offline` | 3.3 GB | Programación ética |
| `muse-ts/py/rust/go/db` | 3.3 GB cada uno | Especializados |
| `nexus-vision` | 5.5 GB | Visión profesional |
| `nexus-think` | 3.3 GB | Razonamiento |
| `nexus-fast` | 3.3 GB | Ultra rápido |

## 🌐 Proveedores Online (opcionales)

### 1. Groq (Gratis, muy rápido)
```bash
export GROQ_API_KEY="tu_key"
```
- Llama 3.3 70B Versatile
- Sin costo, límites generosos

### 2. Together AI
```bash
export TOGETHER_API_KEY="tu_key"
```
- Llama 3.2 90B Vision
- Qwen2.5 Coder 32B
- Modelos especializados

### 3. Fireworks AI
```bash
export FIREWORKS_API_KEY="tu_key"
```
- Llama 3.2 3B/70B
- Baja latencia

### 4. OpenRouter
```bash
export OPENROUTER_API_KEY="tu_key"
```
- Acceso a múltiples modelos
- Gemini 2.0 Flash
- Modelos gratuitos y de pago

## ⚙️ Configuración Rápida

### Solo Offline (recomendado)
```bash
# No requiere configuración
~/.novacode/hybrid.sh auto "tu prompt"
```

### Offline + Online
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
export GROQ_API_KEY="tu_key"

# 4. Usar modo auto
~/.novacode/hybrid.sh auto "tu prompt"
```

## 🎯 Routing Inteligente

1. **Local primero**: Ollama siempre intenta primero
2. **Fallback online**: Si local no está disponible
3. **Por tarea**: Mejor modelo para cada caso
4. **Sin interrupciones**: Transición transparente

## ✅ Ventajas

- **Offline garantizado**: Funciona sin internet
- **Online potenciado**: Modelos más grandes cuando hay conexión
- **Configurable**: Agrega tus propias APIs
- **Consciente**: Misma ética en ambos modos
- **Rápido**: Selección automática de proveedor

## 🔧 Verificar Estado

```bash
# Ver proveedores disponibles
python3 ~/.novacode/hybrid/hybrid_ollama.py

# Test offline
~/.novacode/hybrid.sh offline "Hola"

# Test auto
~/.novacode/hybrid.sh auto "Hola"
```

## 📊 Comparación

| Característica | Offline | Online | Híbrido |
|----------------|---------|--------|---------|
| Internet | ❌ No | ✅ Sí | 🔄 Auto |
| Privacidad | ✅ Total | ⚠️ Depende | ✅ Local primero |
| Velocidad | ⚡ Rápido | 🚀 Variable | ⚡ Mejor opción |
| Modelos | 19 locales | Infinitos | 🎯 Mejor de ambos |
| Costo | Gratis | Varía | 💰 Optimizado |
| Ética | ✅ Sí | ✅ Sí | ✅ Sí |

El sistema funciona **online cuando hay conexión, offline cuando no**, sin configuración obligatoria y con la misma conciencia ética en ambos modos.
