# mc-client-init

## Description Générale
Job **one-shot** d'amorçage de MinIO. Utilise le client en ligne de commande `mc` pour
créer le bucket cible et y copier les images de démonstration, puis s'arrête. N'est pas
un service permanent (`restart: "no"`).

## Structure du Service
| Élément | Rôle |
|---|---|
| Image `minio/mc:latest` | Client MinIO (`mc`) |
| `minio/init/init.sh` | Script d'amorçage (monté en `/init.sh`, lecture seule) |
| `minio/images/` | Images locales copiées vers le bucket (monté en `/images`, lecture seule) |

## Spécifications / Pipeline
Étapes de `minio/init/init.sh` :

1. `mc mb --ignore-existing local/${BUCKET_NAME}` — crée le bucket s'il n'existe pas.
2. `mc cp --recursive /images local/${BUCKET_NAME}` — copie récursive des images.
3. `mc ls --recursive local/${BUCKET_NAME}` — liste le contenu (debug), puis le
   conteneur s'arrête.

L'alias `local` est fourni par la variable `MC_HOST_local` :
`http://${MINIO_ROOT_USER}:${MINIO_ROOT_PASSWORD}@minio:9000`.

## Variables d'environnement
| Variable | Description | Défaut |
|---|---|---|
| `MC_HOST_local` | Alias + auth vers le serveur MinIO | composé depuis `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` |
| `BUCKET_NAME` | Bucket à créer/alimenter | `${MINIO_BUCKET_NAME:-my-bucket}` |

## Flux de Données
- **Entrée** : dossier local `minio/images/` (images `.jpg`).
- **Sortie** : objets dans le bucket MinIO `${MINIO_BUCKET_NAME}`.

## Lancement
```bash
docker compose up -d mc-client-init
docker compose logs -f mc-client-init
```

## Dépendances / Port
Dépend de `minio` (`condition: service_healthy`). Aucun port exposé.
