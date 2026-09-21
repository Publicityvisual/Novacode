#!/bin/bash
# NEXUS SELECTOR - Enrutador inteligente de modelos Novacode
# Uso: ./nexus-selector.sh "tu prompt aquí"
# Selecciona automáticamente el modelo óptimo según el contenido del prompt.

PROMPT="$*"

if [ -z "$PROMPT" ]; then
    echo "❌ Error: debes proporcionar un prompt."
    echo "Uso: $0 'tu prompt aquí'"
    exit 1
fi

# Detectar tipo de tarea
detect_task() {
    local p="$1"
    local pl="${p,,}"
    
    # Multimodal / visión
    if echo "$pl" | grep -qE 'imagen|foto|picture|image|screenshot|analiza imagen|describe esta|qué ves|dibujo|visual|diseño|logo|branding|tipografía|mockup'; then
        echo "multimodal"
        return
    fi
    
    # Código
    if echo "$pl" | grep -qE 'código|code|function|class|implement|refactor|bug|error|debug|api|typescript|javascript|python|rust|go( |$)|docker|k8s|git |```|def |const |import '; then
        echo "code"
        return
    fi
    
    # Tests
    if echo "$pl" | grep -qE 'test|fixture|cobertura|jest|pytest|vitest|playwright|unit test|integration test'; then
        echo "tester"
        return
    fi
    
    # Estrategia / análisis
    if echo "$pl" | grep -qE 'analiza|análisis|estrategia|plan|arquitectura|trade-off|razona|piensa|decision|roadmap|prioridad|evalua|compara'; then
        echo "strategist"
        return
    fi
    
    # Técnico / documentación
    if echo "$pl" | grep -qE 'documentación|manual|guía|tutorial|especificación|schema|endpoint|base de datos|sql|postgres|mongodb'; then
        echo "architect"
        return
    fi
    
    # Rápido
    if echo "$pl" | grep -qE '^traduce|^resumen|^quick|^rápido|^what is|^qué es|^define'; then
        echo "fast"
        return
    fi
    
    # Creativo
    if echo "$pl" | grep -qE 'crea|genera|diseña|idea|brainstorm|story|historia|content|copy|narrativa'; then
        echo "creative"
        return
    fi
    
    # Default
    echo "strategist"
}

TASK=$(detect_task "$PROMPT")

case "$TASK" in
    multimodal)
        MODEL="novacode:glimmer"
        ;;
    code)
        MODEL="novacode:coder"
        ;;
    tester)
        MODEL="novacode:tester"
        ;;
    strategist)
        MODEL="novacode:strategist"
        ;;
    architect)
        MODEL="novacode:architect"
        ;;
    creative)
        MODEL="novacode:designer"
        ;;
    fast)
        MODEL="nexus-fast:latest"
        ;;
    general)
        MODEL="novacode:strategist"
        ;;
    *)
        MODEL="nexus-think:latest"
        ;;
esac

echo "🎯 Tarea detectada: $TASK"
echo "📦 Modelo seleccionado: $MODEL"
echo ""

if ! command -v ollama >/dev/null 2>&1; then
    echo "❌ Error: 'ollama' no está instalado o no está en el PATH."
    exit 1
fi

echo "$PROMPT" | ollama run "$MODEL"