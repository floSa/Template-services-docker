#!/bin/bash

echo "Démarrage de l'application Streamlit..."

# Vérification que les services sont disponibles
echo "Attente des services de base de données..."

# Configuration Streamlit
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Démarrage de Streamlit
echo "Lancement de Streamlit sur le port 8501..."
streamlit run /app/src/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
