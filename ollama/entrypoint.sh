#!/bin/sh
# Entrypoint personnalisé pour Ollama

set -e

echo "Démarrage d'Ollama..."

# Démarrer Ollama en arrière-plan
ollama serve &
OLLAMA_PID=$!

# Attendre qu'Ollama soit prêt
echo "Attente du démarrage d'Ollama..."
sleep 10

# Boucle d'attente avec timeout
TIMEOUT=300
COUNTER=0
until ollama list > /dev/null 2>&1; do
    echo "Ollama non disponible, attente... ($COUNTER/$TIMEOUT)"
    sleep 5
    COUNTER=$((COUNTER + 5))
    if [ $COUNTER -ge $TIMEOUT ]; then
        echo "Timeout: Ollama n'a pas démarré"
        exit 1
    fi
done

echo "Ollama est prêt, téléchargement du modèle..."

# Télécharger le modèle
if ollama pull phi4-mini:latest; then
    echo "Modèle phi4-mini:latest téléchargé avec succès"
else
    echo "Erreur lors du téléchargement"
    exit 1
fi

echo "Configuration terminée, Ollama fonctionne"

# Attendre le processus Ollama
wait $OLLAMA_PID
