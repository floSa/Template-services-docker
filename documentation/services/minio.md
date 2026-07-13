# minio

## Rôle
**Stockage objet S3-compatible**. Expose une API S3 (port `9000`) et une console web
(port `9001`). Sert au stockage/lecture d'images depuis la section « MinIO » de l'app
Streamlit. Le bucket et les images initiales sont chargés par le job `mc-client-init`
(voir [mc-client-init.md](mc-client-init.md)).

## Container(s)
| Container | Image | Port interne | Port exposé | Rôle |
|---|---|---|---|---|
| `minio_server` | `minio/minio:latest` | `9000` (API) / `9001` (console) | `${MINIO_PORT}` (`9000`) + `9001` | Serveur objet + console |

Commande : `server /data --console-address ":9001"`.

## API / Interface
- **API S3** : `http://localhost:9000` (client `minio` SDK Python dans `streamlit/src/app.py`).
- **Console web** : `http://localhost:9001` (identifiants root ci-dessous).
- Sonde : `GET /minio/health/live`.

## Variables d'environnement
| Variable | Description | Défaut (`.env`) |
|---|---|---|
| `MINIO_ROOT_USER` | Utilisateur root / access key | `minioadmin` |
| `MINIO_ROOT_PASSWORD` | Mot de passe root / secret key | `minioadmin` |
| `MINIO_PORT` | Port API publié sur l'hôte | `9000` |
| `MINIO_BUCKET_NAME` | Bucket cible (utilisé par `mc-client-init`) | `my-bucket` |

> Le port console `9001` est publié en dur (`docker-compose.yml:137`), non paramétré.
> La ligne `MINIO_PORT=9000` apparaît deux fois dans `.env` (doublon sans effet).

## Dépendances
Aucune dépendance amont. Dépendant : `mc-client-init` attend son healthcheck.

## Persistence
- Bind mount `./minio/data` → `/data` : buckets et objets persistés sur l'hôte.
- Le dépôt contient déjà un état MinIO amorcé sous `minio/data/` (bucket `my-bucket`,
  images de démonstration).

## Healthcheck
```yaml
test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
interval: 10s
timeout: 5s
retries: 5
```
