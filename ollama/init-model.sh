#!/bin/bash
# Script d'initialisation pour télécharger le modèle phi4-mini:latest

echo "Démarrage du téléchargement du modèle phi4-mini:latest..."

# Attendre qu'Ollama soit disponible
until ollama list > /dev/null 2>&1; do
    echo "En attente du démarrage d'Ollama..."
    sleep 5
done

# Télécharger le modèle phi4-mini:latest
echo "Téléchargement du modèle phi4-mini:latest..."
ollama pull phi4-mini:latest

# Vérifier que le modèle a été téléchargé
if ollama list | grep -q "phi3.5:latest"; then
    echo "Modèle phi4-mini:latest téléchargé avec succès"
else
    echo "Erreur lors du téléchargement du modèle phi4-mini:latest"
    exit 1
fi

echo "Configuration Ollama terminée"
