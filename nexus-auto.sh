#!/bin/bash
# NEXUS AUTO - Selección automática inteligente
# Uso: ./nexus-auto.sh "tu prompt aquí"

if [ $# -eq 0 ]; then
    echo "❌ Debes proporcionar un prompt"
    echo "Uso: ./nexus-auto.sh 'tu prompt aquí'"
    exit 1
fi

~/.novacode/nexus-selector.sh "$*"
