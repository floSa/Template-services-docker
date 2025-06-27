#!/bin/sh

echo "[INFO] Import automatique de Iris.csv..."

mongoimport \
  --host localhost \
  --port 27017 \
  --username "$MONGO_INITDB_ROOT_USERNAME" \
  --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin \
  --db "$MONGO_INITDB_DATABASE" \
  --collection iris \
  --type csv \
  --headerline \
  --file /docker-entrypoint-initdb.d/Iris.csv

echo "[INFO] Import terminé avec succès."
