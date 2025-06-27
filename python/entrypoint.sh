#!/bin/bash
set -euo pipefail

echo "=== Démarrage du service conda pur ==="

# Variables
ENV_NAME="mon_env_test"

# Attente de PostgreSQL
echo "Attente de la disponibilité de PostgreSQL..."
until pg_isready -h postgres -p 5432 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"; do
    echo "PostgreSQL n'est pas encore prêt — nouvelle tentative dans 2 s..."
    sleep 2
done
echo "PostgreSQL est prêt !"

# Activation de l'env
echo "Activation de l'environnement conda '${ENV_NAME}'…"
source /opt/conda/etc/profile.d/conda.sh
conda activate "${ENV_NAME}"

# Afficher les paquets installés
echo "=== Paquets installés dans '${ENV_NAME}' ==="
conda list | grep -E "(pandas|sqlalchemy|psycopg2|python-dotenv|pymongo)"

# Lancer le script Python
echo "=== Exécution du script de connexion BDD ==="
cd /app/src
python connexion_bdd.py

# Garder le conteneur vivant pour debug
echo "=== Script terminé avec succès ==="
echo "Conteneur prêt. Tapez 'docker exec -it miniconda_app bash' pour interagir."
tail -f /dev/null
