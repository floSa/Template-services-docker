# mongodb

## Rôle
Base de données **documentaire** (NoSQL) du template. Héberge la collection `iris`,
importée au premier démarrage depuis `mongo/Iris.csv`. Sert de cible NoSQL pour
`miniconda` et `streamlit`.

## Container(s)
| Container | Image | Port interne | Port exposé | Rôle |
|---|---|---|---|---|
| `mongodb_db` | `mongo:7` | `27017` | `${MONGO_PORT}` (`27017`) | Serveur MongoDB |

## API / Interface
Aucune API HTTP — accès via le protocole MongoDB (port `27017`). Client dans ce projet :
`pymongo` avec URI `mongodb://<user>:<pass>@mongodb_db:27017/<db>?authSource=admin`.

## Variables d'environnement
| Variable | Description | Défaut (`.env`) |
|---|---|---|
| `MONGO_ROOT_USERNAME` | Utilisateur root (`MONGO_INITDB_ROOT_USERNAME`) | `admin` |
| `MONGO_ROOT_PASSWORD` | Mot de passe root | `your_secure_password` |
| `MONGO_DB` | Base initiale (`MONGO_INITDB_DATABASE`) | `iris_db` |
| `MONGO_PORT` | Port publié sur l'hôte | `27017` |
| `MONGO_HOST` | Hôte lu côté code applicatif | `mongodb_db` |

## Dépendances
Aucune dépendance amont. Dépendants : `miniconda` et `streamlit` attendent son
healthcheck (`condition: service_healthy`).

## Persistence
- Volume nommé `mongodb_data` → `/data/db`.
- Dossier `./mongo` monté dans `/docker-entrypoint-initdb.d/` :
  - `mongo/mongo-init.sh` → `mongoimport` de `Iris.csv` (CSV, `--headerline`) dans la
    collection `iris` ;
  - `mongo/Iris.csv` → données source (en-tête `Id,SepalLengthCm,SepalWidthCm,PetalLengthCm,PetalWidthCm,Species`).

Structure d'un document `iris` (clés PascalCase, `python/src/connexion_bdd.py`) :
`Id`, `SepalLengthCm`, `SepalWidthCm`, `PetalLengthCm`, `PetalWidthCm`, `Species`.

## Healthcheck
```yaml
test: ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand('ping')"]
interval: 10s
timeout: 5s
retries: 5
```
