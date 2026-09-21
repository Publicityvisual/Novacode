#!/bin/bash
# NOVA QUICK - Accesos rápidos Novacode
# Uso: ./novacode-quick.sh [tipo] [prompt]

case "${1:-help}" in
    architect)
        shift
        ~/.novacode/nexus-selector.sh "Arquitectura técnica: $*"
        ;;
    coder)
        shift
        ~/.novacode/nexus-selector.sh "Código/programación: $*"
        ;;
    tester)
        shift
        ~/.novacode/nexus-selector.sh "Tests/fixture/cobertura: $*"
        ;;
    strategist)
        shift
        ~/.novacode/nexus-selector.sh "Estrategia/análisis: $*"
        ;;
    designer)
        shift
        ~/.novacode/nexus-selector.sh "Diseño visual/branding: $*"
        ;;
    muse)
        shift
        ~/.novacode/nexus-selector.sh "Creatividad/narrativa: $*"
        ;;
    vision)
        shift
        ~/.novacode/nexus-selector.sh "Analiza esta imagen: $*"
        ;;
    code)
        shift
        ~/.novacode/nexus-selector.sh "Código general: $*"
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
        echo "🚀 NOVA QUICK - Accesos rápidos Novacode"
        echo ""
        echo "Uso: ./novacode-quick.sh [tipo] [prompt]"
        echo ""
        echo "Tipos (modelos propios Novacode):"
        echo "  architect   - Arquitectura, patrones, producción"
        echo "  coder       - Código production-ready, debug, refactor"
        echo "  tester      - Tests, fixtures, cobertura"
        echo "  strategist  - Análisis, estrategia, toma de decisiones"
        echo "  designer    - Diseño visual, marca, tipografía"
        echo "  muse        - Creatividad multimodal, narrativa"
        echo "  vision      - Análisis de imagen"
        echo "  code        - Código general"
        echo "  think       - Razonamiento"
        echo "  fast        - Respuesta rápida"
        echo ""
        echo "Ejemplos:"
        echo "  ./novacode-quick.sh architect 'Diseña arquitectura de microservicios'"
        echo "  ./novacode-quick.sh coder 'Implementa API TypeScript con tests'"
        echo "  ./novacode-quick.sh tester 'Crea suite de tests para este módulo'"
        echo "  ./novacode-quick.sh strategist 'Analiza si migrar a microservicios'"
        echo "  ./novacode-quick.sh designer 'Analiza paleta de colores de esta marca'"
        exit 1
        ;;
esac