# NEXUS OFFLINE - Guía Rápida

## 🚀 Inicio Rápido

```bash
# Verificar estado
~/.novacode/offline.sh check

# Ejecutar modelos
~/.novacode/offline.sh run muse-offline "Analiza esta imagen: [imagen]"
~/.novacode/offline.sh run muse-code-offline "Implementa API TypeScript"
~/.novacode/offline.sh run nexus-think:latest "Razona sobre arquitectura"
~/.novacode/offline.sh run nexus-vision:latest "Describe esta imagen"
```

## 📦 Modelos Offline

| Modelo | Uso | Comando |
|--------|-----|---------|
| MUSE-OFFLINE | Multimodal general | `ollama run muse-offline` |
| MUSE-CODE-OFFLINE | Programación | `ollama run muse-code-offline` |
| NEXUS-VISION | Análisis visual | `ollama run nexus-vision` |
| NEXUS-CODE | Código producción | `ollama run nexus-code` |
| NEXUS-THINK | Razonamiento | `ollama run nexus-think` |
| NEXUS-FAST | Ultra rápido | `ollama run nexus-fast` |
| QWEN2.5-7B | Fallback | `ollama run qwen2.5:7b-instruct-q4_K_M` |

## ⚡ Modo Offline Garantizado

```bash
# 1. Iniciar Ollama
brew services start ollama

# 2. Verificar modelos locales
ollama list

# 3. Usar sin internet
ollama run muse-offline "Tu prompt aquí"

# 4. No necesita conexión
# Todo funciona localmente en tu M5
```

## 🎯 Programación Offline

```bash
# TypeScript/React
ollama run muse-code-offline "Crea hook personalizado TypeScript"

# Python/Django
ollama run muse-code-offline "Implementa API REST Django con tests"

# Rust/CLI
ollama run muse-code-offline "Crea CLI en Rust con argument parsing"

# Go/microservicio
ollama run muse-code-offline "Arquitectura microservicio Go con Docker"
```

## 🧠 Memoria Virtual Offline

```bash
# Sistema de memoria propio
cd ~/.novacode/memory
python3 nexus_orchestrator.py
```

## 🔧 Configuración Kilo Offline

```json
{
  "model": "nexus-think:latest",
  "ollama": {
    "base_url": "http://localhost:11434"
  }
}
```

## ✅ Verificación

```bash
# Test completo offline
~/.novacode/offline.sh check

# Test velocidad
time ollama run nexus-fast "Hola mundo"

# Test multimodal
ollama run muse-offline "Analiza: [imagen local]"
```

## 🚨 Troubleshooting

```bash
# Reiniciar Ollama
brew services restart ollama

# Limpiar modelos
ollama rm $(ollama list | grep -v 'minicpm\|qwen\|sofia' | awk '{print $1}')

# Recrear stack
ollama create muse-offline -f ~/.ollama/modelfiles/muse-offline
```
