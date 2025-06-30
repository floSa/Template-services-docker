#!/bin/bash
# Script d'initialisation pour télécharger le modèle phi4-mini:latest

set -e  # Arrêter en cas d'erreur

echo "Démarrage du téléchargement du modèle phi4-mini:latest..."

# Attendre qu'Ollama soit disponible avec timeout
TIMEOUT=300  # 5 minutes
COUNTER=0
until curl -s http://localhost:11434/api/version > /dev/null 2>&1; do
    echo "En attente du démarrage d'Ollama... ($COUNTER/$TIMEOUT)"
    sleep 5
    COUNTER=$((COUNTER + 5))
    if [ $COUNTER -ge $TIMEOUT ]; then
        echo "Timeout: Ollama n'a pas démarré dans les temps"
        exit 1
    fi
done

echo "Ollama est disponible, téléchargement du modèle..."

# Télécharger le modèle phi4-mini:latest
if ollama pull phi4-mini:latest; then
    echo "Modèle phi4-mini:latest téléchargé avec succès"
else
    echo "Erreur lors du téléchargement du modèle phi4-mini:latest"
    exit 1
fi

# Vérifier que le modèle a été téléchargé
if ollama list | grep -q "phi4-mini:latest"; then
    echo "Modèle phi4-mini:latest confirmé dans la liste"
else
    echo "Attention: Modèle non trouvé dans la liste"
fi

echo "Configuration Ollama terminée"
