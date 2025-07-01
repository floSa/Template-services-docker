#!/bin/sh

# Attendre MinIO prêt
sleep 10

# Créer le bucket 'images' s'il n'existe pas
mc alias set local http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
mc mb -q --ignore-existing local/images

# Uploader les deux images
 
mc cp /docker-entrypoint-initdb.d/images/image1.jpg local/images/
mc cp /docker-entrypoint-initdb.d/images/image2.jpg local/images/
