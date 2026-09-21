#!/bin/bash
# PUBLICA MODELOS NOVACODE EN OLLAMA.COM
# Requiere: cuenta en ollama.com + `ollama login`
# Uso: ./publish-novacode.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NOVA-CODE MODEL PUBLISHER"
echo "  Publicando modelos propios en ollama.com/novacode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Verificar login
echo "🔐 Verificando sessión de Ollama..."
if ! ollama whoami >/dev/null 2>&1; then
    echo "❌ No has iniciado sessión."
    echo "   Ejecuta: ollama login"
    echo "   Ve a https://ollama.com y crea tu cuenta."
    exit 1
fi
echo "   ✅ Sessión activa: $(ollama whoami)"
echo ""

# 2. Crear namespace si no existe
echo "📦 Verificando namespace 'novacode'..."
# (El namespace se crea automáticamente al hacer push del primer modelo)
echo ""

# 3. Lista de modelos a publicar
MODELS=(
    "novacode:omni"
    "novacode:glimmer"
    "novacode:designer"
    "novacode:strategist"
    "novacode:coder"
    "novacode:architect"
    "novacode:tester"
)

# 4. Publicar cada modelo
for model in "${MODELS[@]}"; do
    echo "🚀 Publicando $model..."
    if ollama push "$model" 2>&1; then
        echo "   ✅ $model publicado en ollama.com/novacode/${model#*:}"
    else
        echo "   ❌ Error publicando $model"
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ PUBLICACIÓN COMPLETA"
echo "  Tus modelos están en: https://ollama.com/novacode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"