#!/bin/bash
# HYBRID MODE - Sistema híbrido online/offline
# Uso: ./hybrid.sh [offline|online|auto] [prompt]

set -e

MODE="${1:-auto}"
shift || true

if [ "$MODE" = "offline" ]; then
    echo "🔒 Modo OFFLINE - Solo modelos locales"
    if [ $# -eq 0 ]; then
        echo "Uso: ./hybrid.sh offline <prompt>"
        exit 1
    fi
    ~/.novacode/nexus-selector.sh "$*"
elif [ "$MODE" = "online" ]; then
    echo "🌐 Modo ONLINE - APIs externas"
    if [ $# -eq 0 ]; then
        echo "Uso: ./hybrid.sh online <prompt>"
        exit 1
    fi
    python3 ~/.novacode/hybrid/hybrid_ollama.py --online "$*"
elif [ "$MODE" = "auto" ]; then
    echo "🔄 Modo AUTO - Mejor proveedor disponible"
    if [ $# -eq 0 ]; then
        echo "Uso: ./hybrid.sh auto <prompt>"
        exit 1
    fi
    python3 ~/.novacode/hybrid/hybrid_ollama.py "$*"
else
    echo "❌ Modo inválido: $MODE"
    echo "Uso: ./hybrid.sh [offline|online|auto] <prompt>"
    exit 1
fi
