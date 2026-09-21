# NOVA-CODE — Stack de Modelos Propios

## 🎯 Modelos Novacode (Publicados en ollama.com/publicityvisual)

| Modelo | Base | Tamaño | Rol |
|--------|------|--------|-----|
| `novacode:omni` | publicityvisual/novaai-god-omni | ~3.3 GB | Monstruo multimodal definitivo (visión + razonamiento agente) |
| `novacode:glimmer` | muse-offline (MiniCPM-V 8B) | ~5.5 GB | Agente multimodal, tool-calling, reasoning (inspirado en Meta Muse Glimmer 30B) |
| `novacode:designer` | muse-offline (MiniCPM-V 8B) | ~5.5 GB | Diseño visual, marca, tipografía, paleta, OCR |
| `novacode:strategist` | nexus-think (Gemma3 4.3B) | ~3.3 GB | Análisis, estrategia, toma de decisiones, razonamiento profundo |
| `novacode:coder` | muse-code-offline (Gemma3 4.3B) | ~3.3 GB | Código production-ready, debug, refactor |
| `novacode:architect` | muse-code-offline (Gemma3 4.3B) | ~3.3 GB | Arquitectura, patrones, producción, documentación técnica |
| `novacode:tester` | muse-code-offline (Gemma3 4.3B) | ~3.3 GB | Tests, fixtures, cobertura, Jest/Pytest/Vitest |

## 📦 Modelos Base (Fallback)

| Modelo | Base | Tamaño | Rol |
|--------|------|--------|-----|
| `nexus-think:latest` | Gemma3 4.3B | ~3.3 GB | Razonamiento general |
| `nexus-fast:latest` | Sofia Nova | ~3.3 GB | Respuestas ultra rápidas |
| `nexus-code:latest` | Gemma3 4.3B | ~3.3 GB | Código/arquitectura |
| `nexus-vision:latest` | MiniCPM-V 8B | ~5.5 GB | Análisis visual |
| `minicpm-v:8b` | MiniCPM-V 8B | ~5.5 GB | Multimodal base |

## 🔌 Proveedores externos

### Nvidia (API) — DESHABILITADO
- La API key actual no tiene funciones de chat disponibles en `integrate.api.nvidia.com` (HTTP 404 *Function not found*).
- Se usa **100% offline** con modelos locales propios en Ollama.
- Si en el futuro se obtiene una key válida, habilitar en `providers.json` y usar modelos como `google/gemma-3-12b-it` o `deepseek-ai/deepseek-v4-flash-0731`.

### Anthropic (API) — deshabilitado por defecto
- No hay `ANTHROPIC_API_KEY` configurada en el entorno.
- Para activarlo, exportar la variable y habilitar `anthropic` en `providers.json`.
- Modelo por defecto: `claude-sonnet-4-20250514`.

## 🚀 Uso Rápido

```bash
# Selección automática
~/.novacode/novacode-quick.sh architect "Diseña arquitectura de microservicios"
~/.novacode/novacode-quick.sh coder "Implementa API TypeScript con tests"
~/.novacode/novacode-quick.sh tester "Crea suite de tests para este módulo"
~/.novacode/novacode-quick.sh strategist "Analiza si migrar a microservicios"
~/.novacode/novacode-quick.sh designer "Analiza paleta de colores de esta marca"
~/.novacode/novacode-quick.sh vision "Describe esta imagen"

# Modelos propios
ollama run novacode:omni "Analiza esta imagen y razona sobre el diseño"
ollama run novacode:glimmer "Razona sobre este screenshot y propón tool-calling"
ollama run novacode:coder "Implementa API FastAPI con CRUD y tests"
ollama run novacode:strategist "Diseña estrategia de pricing para SaaS B2B"

# Publicados en registry
ollama pull publicityvisual/novacode:omni
ollama pull publicityvisual/novacode:glimmer
ollama pull publicityvisual/novacode:designer
ollama pull publicityvisual/novacode:strategist
ollama pull publicityvisual/novacode:coder
ollama pull publicityvisual/novacode:architect
ollama pull publicityvisual/novacode:tester

# Verificar sistema
~/.novacode/offline.sh check
ollama list | grep novacode
```

## ⚡ Optimizaciones Aplicadas

- **Flash Attention**: Activado
- **GPU Layers**: 20/20
- **Contexto**: 32768 tokens
- **Modelos en GPU**: 2 simultáneos
- **Cuantización**: Q4_K_M / Q4_0
- **Memoria virtual**: Sin límites

## 🔧 Configuración Ollama

```ini
[settings]
max_loaded_models = 2
default_num_ctx = 32768
num_gpu = 20
flash_attention = true
parallel_requests = true
max_queue = 10
```

## 🎨 Características

- ✅ 100% offline, sin internet
- ✅ Multimodal: visión + texto
- ✅ Modelos propios personalizados
- ✅ Optimizados para Apple M-series
- ✅ Publicados en ollama.com/publicityvisual
- ✅ Selección automática por tarea
- ✅ Código production-ready