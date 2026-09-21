#!/bin/bash
# NEXUS OFFLINE - Sistema 100% autónomo sin internet
# Uso: ./offline.sh [comando] [argumentos]

set -e

MODELS=(
    "novacode:omni"
    "novacode:glimmer"
    "novacode:designer"
    "novacode:strategist"
    "novacode:coder"
    "novacode:architect"
    "novacode:tester"
    "novacode:glimmer"
)

check_offline() {
    echo "🔍 Verificando modo offline..."
    
    # Verificar que Ollama esté corriendo
    if ! ollama list >/dev/null 2>&1; then
        echo "❌ Ollama no está corriendo. Iniciando..."
        brew services start ollama
        sleep 3
    fi
    
    # Verificar modelos locales
    echo "📦 Verificando modelos locales..."
    for model in "${MODELS[@]}"; do
        if ollama list | grep -qF -- "$model"; then
            echo "  ✅ $model"
        else
            echo "  ❌ $model NO ENCONTRADO"
        fi
    done
    
    # Verificar sin internet
    echo "🌐 Verificando conexión..."
    if ping -c 1 google.com >/dev/null 2>&1; then
        echo "  ⚠️  Hay conexión a internet (pero no se necesita)"
    else
        echo "  ✅ Modo offline confirmado"
    fi
}

run_offline() {
    local model=$1
    shift
    local prompt="$*"
    
    if [ -z "$prompt" ]; then
        echo "❌ Debes proporcionar un prompt"
        exit 1
    fi
    
    echo "🚀 Ejecutando modelo: $model"
    echo "📝 Prompt: $prompt"
    echo ""
    
    echo "$prompt" | ollama run "$model"
}

case "${1:-check}" in
    check)
        check_offline
        ;;
    run)
        if [ -z "$2" ]; then
            echo "Uso: ./offline.sh run <modelo> <prompt>"
            echo "Modelos disponibles:"
            printf '  - %s\n' "${MODELS[@]}"
            exit 1
        fi
        model=$2
        shift 2
        run_offline "$model" "$@"
        ;;
    list)
        echo "📦 Modelos offline disponibles:"
        ollama list | grep -E 'novacode|nexus-fast|minicpm'
        ;;
    *)
        echo "Uso: ./offline.sh [check|run|list]"
        echo ""
        echo "Comandos:"
        echo "  check              - Verificar estado offline"
        echo "  run <modelo> <prompt> - Ejecutar modelo"
        echo "  list               - Listar modelos offline"
        echo ""
        echo "Ejemplos:"
        echo "  ./offline.sh check"
        echo "  ./offline.sh run novacode:omni 'Analiza esta imagen y razona sobre el diseño'"
        echo "  ./offline.sh run novacode:coder 'Implementa API FastAPI con CRUD y tests'"
        echo "  ./offline.sh run novacode:strategist 'Diseña estrategia de pricing para SaaS B2B'"
        echo "  ./offline.sh run novacode:designer 'Genera concepto creativo para portada'"
        exit 1
        ;;
esac
