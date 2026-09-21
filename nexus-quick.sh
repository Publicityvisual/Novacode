#!/bin/bash
# NEXUS QUICK - Accesos rápidos offline

case "${1:-help}" in
    ts)
        shift
        ~/.novacode/nexus-selector.sh "TypeScript/JavaScript: $*"
        ;;
    py)
        shift
        ~/.novacode/nexus-selector.sh "Python: $*"
        ;;
    rust)
        shift
        ~/.novacode/nexus-selector.sh "Rust: $*"
        ;;
    go)
        shift
        ~/.novacode/nexus-selector.sh "Go: $*"
        ;;
    db)
        shift
        ~/.novacode/nexus-selector.sh "Base de datos/SQL: $*"
        ;;
    vision)
        shift
        ~/.novacode/nexus-selector.sh "Analiza esta imagen: $*"
        ;;
    code)
        shift
        ~/.novacode/nexus-selector.sh "Código/programación: $*"
        ;;
    think)
        shift
        ~/.novacode/nexus-selector.sh "Razonamiento/estrategia: $*"
        ;;
    fast)
        shift
        ~/.novacode/nexus-selector.sh "Respuesta rápida: $*"
        ;;
    *)
        echo "🚀 NEXUS QUICK - Accesos rápidos offline"
        echo ""
        echo "Uso: ./nexus-quick.sh [tipo] [prompt]"
        echo ""
        echo "Tipos:"
        echo "  ts      - TypeScript/JavaScript"
        echo "  py      - Python"
        echo "  rust    - Rust"
        echo "  go      - Go"
        echo "  db      - Base de datos/SQL"
        echo "  vision  - Análisis de imagen"
        echo "  code    - Código general"
        echo "  think   - Razonamiento"
        echo "  fast    - Respuesta rápida"
        echo ""
        echo "Ejemplos:"
        echo "  ./nexus-quick.sh ts 'Crea hook personalizado useState'"
        echo "  ./nexus-quick.sh py 'API FastAPI con CRUD'"
        echo "  ./nexus-quick.sh rust 'CLI con Clap'"
        echo "  ./nexus-quick.sh db 'Schema PostgreSQL para ecommerce'"
        echo "  ./nexus-quick.sh vision 'Describe esta imagen'"
        exit 1
        ;;
esac
