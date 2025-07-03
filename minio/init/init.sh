#!/bin/sh
set -eu

# 1. créer le bucket s’il n’existe pas (ignore si déjà présent)
mc mb --ignore-existing local/${BUCKET_NAME}

# 2. copier récursivement toutes les images
mc cp --recursive /images local/${BUCKET_NAME}

# 3. (optionnel) lister le contenu pour debug
mc ls --recursive local/${BUCKET_NAME}

# Fin : le conteneur mc-client-init s’arrête automatiquement