# NovaCode CLI

<div align="center">

```text
   _   __                     ______          __     
  / | / /___ _   ______ _    / ____/___  ____/ /__   
 /  |/ / __ \ | / / __ `/   / /   / __ \/ __  / _ \  
/ /|  / /_/ / |/ / /_/ /   / /___/ /_/ / /_/ /  __/  
/_/ |_/\____/|___/\__,_/____\____/\____/\__,_/\___/   
                      /_____/                          
```

**La suite de desarrollo autónomo con IA y terminal TUI de nueva generación.**

[![NovaCode CI Matrix](https://github.com/Publicityvisual/Novacode/actions/workflows/ci.yml/badge.svg)](https://github.com/Publicityvisual/Novacode/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-purple.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-Modular%20Packages-orange.svg)]()

</div>

---

## 🌟 Características Principales

### 🖥️ 1. Terminal TUI Nativa de Alto Rendimiento
- **Interfaz Reactiva**: Diseñada con bordes estilizados, temas oscuros y claros, resaltado de sintaxis en tiempo real y soporte para navegación con ratón.
- **Diffs Interactivos y Edición Segura**: Revisa y aprueba modificaciones de código bloque por bloque.
- **Paleta de Comandos Dinámica**: Acceso rápido con `/help`, `/init`, `/compact`, `/review`, `/model`, entre otros.

### 🚗 2. Autonomous Goal Pilot & Multi-Agent Swarm
- **Piloto Autónomo (`novacode auto <meta>`)**: Descompone cualquier objetivo complejo en pasos ejecutables, genera código y valida resultados automáticamente.
- **Enjambre Paralelo (`novacode swarm <tarea>`)**: Orquesta agentes especializados (arquitectura, seguridad, pruebas TDD, frontend) en paralelo con aceleración 4x.

### 🧠 3. Multi-Modal Proxy & Generación Sin Límites
- **Proxy Multimodal Ultra-Rápido (`:18791`)**: Enrutamiento unificado para modelos de vanguardia (NVIDIA NIM, OpenRouter, Ollama, Zen).
- **Estudio Multimodal (`novacode generate <prompt>`)**: Generación de imágenes, video, audio y texto omnimodal en alta fidelidad.

### 🛡️ 4. Sandbox Instantáneo & Sentinel Auto-Healer
- **Instant Rollback Sandbox**: Ejecuta comandos potencialmente riesgosos con captura de snapshots y restauración instantánea.
- **Sentinel Daemon (`novacode sentinel`)**: Monitorización continua del código fuente para corregir sintaxis y bugs de forma preventiva.

### 🔨 5. Model Forge Suite
- **Fine-Tuning & Merge**: Herramientas integradas para generar datasets, entrenar adaptadores LoRA, fusionar modelos con SLERP y cuantizar a formato GGUF (`Q4_K_M`, etc.).

---

## 📁 Arquitectura Modular de Paquetes (`packages/`)

```
novacode/
├── packages/
│   ├── cli/              # Entrypoint unificado y puente del launcher
│   ├── core/             # Hyper-Engine, quantum cache, semantic graph, sentinel
│   ├── llm/              # Multi-modal proxy (:18791), router y clientes HTTP
│   ├── agents/           # Autonomous pilot, daemon en segundo plano, swarm y healer
│   ├── tools/            # AST surgeon, docker/git pilots, devtools, sandbox, doctor
│   ├── forge/            # Dataset builder, model trainer, merger y quantizer
│   ├── media/            # Generador multimedia (imagen, video, audio, omni)
│   ├── tui/              # Componentes visuales del renderer TUI
│   └── web/              # Servidor local y dashboard web interactivo
├── config/               # Modelos, esquemas y configuraciones
├── scripts/              # Scripts de instalación y herramientas del sistema
├── tests/                # Suite completa de pruebas unitarias (43+ tests)
└── logo.svg              # Identidad visual y logotipo oficial
```

---

## 🚀 Instalación y Uso Rápido

### 1. Iniciar la Interfaz TUI
Simplemente ejecuta:
```bash
novacode
```

### 2. Comandos Principales
```bash
# Diagnóstico de salud del sistema y configuración
novacode doctor

# Listar modelos y proveedores activos
novacode models
novacode providers list

# Ejecutar una meta con el piloto autónomo
novacode auto "Crear un microservicio de autenticación en FastAPI"

# Generación multimedia
novacode generate "Retrato cyberpunk de una IA futurista en neón"

# Iniciar servidor web de control
novacode web
```

---

## 🧪 Pruebas y Validación

Para ejecutar la suite de pruebas unitarias multiplataforma:
```bash
python3 -m unittest discover tests -v
```

---

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la Licencia MIT.
