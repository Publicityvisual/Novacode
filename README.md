# NovaCode CLI

<div align="center">

```text
      ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗  ██████╗ ██████╗ ██████╗ ███████╗
      ████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝
      ██╔██╗ ██║██║   ██║██║   ██║███████║██║     ██║   ██║██║  ██║█████╗  
      ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║     ██║   ██║██║  ██║██╔══╝  
      ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╗╚██████╔╝██████╔╝███████╗
      ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
                              ─── C L I ───                                
```

**La suite de desarrollo autónomo con IA, modelos multimodales sin límites y terminal TUI nativa de ultra-rendimiento.**

[![NovaCode Test Suite](https://img.shields.io/badge/tests-47%20passed%20(100%25)-brightgreen.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Context Window](https://img.shields.io/badge/context-128K%20Tokens-purple.svg)]()
[![Multimodal](https://img.shields.io/badge/multimodal-Vision%20%7C%20Code%20%7C%20Audio%20%7C%20Video-orange.svg)]()

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

### 🧠 3. Multi-Modal Suite & Modelos Sin Límites
- **Proxy Multimodal con Failover Multi-Proveedor (`:18791`)**: Conmutación automática entre NVIDIA NIM, OpenRouter y el motor local.
- **Estudio Multimodal (`novacode generate <prompt>`)**: Generación de imágenes, video, audio y texto omnimodal en alta fidelidad.
- **Ventana de Contexto de 128K**: Admite repositorios y archivos extensos sin desbordamiento de contexto.

---

## 📁 Arquitectura Modular de Paquetes (`packages/`)

```
novacode/
├── packages/
│   ├── cli/              # Entrypoint unificado y launcher
│   ├── core/             # Hyper-Engine, quantum cache, semantic graph, sentinel
│   ├── llm/              # Multi-modal proxy (:18791), router y clientes HTTP
│   ├── agents/           # Autonomous pilot, daemon en segundo plano, swarm y healer
│   ├── tools/            # AST surgeon, docker/git pilots, devtools, sandbox, doctor
│   ├── forge/            # Dataset builder, model trainer, merger y quantizer
│   ├── media/            # Generador multimedia (imagen, video, audio, omni)
│   ├── tui/              # Componentes visuales del renderer TUI
│   └── web/              # Servidor local y dashboard web interactivo (:18795)
├── config/               # Modelos, esquemas y configuraciones
├── scripts/              # Scripts de instalación y runner de pruebas local
├── tests/                # Suite completa de pruebas unitarias (47+ tests)
└── logo.svg              # Identidad visual y logotipo oficial
```

---

## 🚀 Uso Rápido

```bash
# Iniciar sesión interactiva TUI
novacode

# Diagnóstico de salud y configuración
novacode doctor

# Piloto autónomo
novacode auto "Crear API REST con FastAPI"

# Generación multimedia
novacode generate "Ilustración cyberpunk en neón"

# Panel web interactivo
novacode web
```

---

## 🧪 Pruebas y Validación

Para ejecutar la suite de pruebas unitarias:
```bash
./scripts/test.sh
```

---

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la Licencia MIT.
