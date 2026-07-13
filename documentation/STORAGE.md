# Stockage — Template-services-docker

Le template embarque **quatre stores** de natures différentes. Ce document récapitule ce
qui est persisté, où, et comment c'est initialisé.

---

## 1. Vue d'ensemble

| Store | Type | Service | Persistance | Donnée de démo |
|---|---|---|---|---|
| PostgreSQL | Relationnel (SQL) | `postgres` | volume `postgres_data` | Table `iris` |
| MongoDB | Documentaire (NoSQL) | `mongodb` | volume `mongodb_data` | Collection `iris` |
| MinIO | Objet (S3) | `minio` | bind mount `./minio/data` | Bucket `my-bucket` + images |
| Ollama | Modèles LLM | `ollama` | volume `ollama_data` | Modèle `phi4-mini:latest` |

---

## 2. PostgreSQL

- **Chemin persistant** : volume `postgres_data` → `/var/lib/postgresql/data`.
- **Initialisation** (premier démarrage, volume vide) : `postgres/init.sql` crée la table
  `iris` puis `COPY` depuis `postgres/Iris.csv` (`150` lignes).
- **Schéma** : voir [services/postgres.md](services/postgres.md).
- **Attention** : les scripts `/docker-entrypoint-initdb.d/` ne s'exécutent **qu'au premier
  boot** (BDD vide). Pour rejouer l'init : `docker compose down -v` puis `up` (détruit les
  données).

## 3. MongoDB

- **Chemin persistant** : volume `mongodb_data` → `/data/db`.
- **Initialisation** : `mongo/mongo-init.sh` exécute `mongoimport` de `mongo/Iris.csv`
  (`--headerline`) dans la collection `iris` de la base `${MONGO_DB}` (`iris_db`).
- **Format document** : clés PascalCase (`Id`, `SepalLengthCm`, ...).

## 4. MinIO (stockage objet)

- **Chemin persistant** : bind mount `./minio/data` → `/data`. Contrairement aux deux
  BDD, les données vivent **directement dans l'arborescence du dépôt**.
- **État préexistant** : le dépôt contient déjà un store MinIO amorcé
  (`minio/data/.minio.sys/`, bucket `my-bucket`, images `Image1.png`, `images/image1.jpg`,
  `images/image2.jpg`).
- **Initialisation applicative** : le job `mc-client-init` (re)crée le bucket
  `${MINIO_BUCKET_NAME}` et y copie `minio/images/`. Voir
  [services/mc-client-init.md](services/mc-client-init.md).
- **Attention** : committer `minio/data/` versionne des fichiers internes MinIO (métadonnées
  `xl.meta`) — à envisager d'ajouter au `.gitignore`.

## 5. Ollama (modèles)

- **Chemin persistant** : volume `ollama_data` → `/root/.ollama`.
- **Contenu** : modèles téléchargés (`phi4-mini:latest`), conservés entre redémarrages
  pour éviter un re-téléchargement (`~1–3 Go` selon le modèle, `<à confirmer>`).

---

## 6. Réinitialisation

```bash
# Tout remettre à zéro (SUPPRIME les volumes nommés : Postgres, Mongo, Ollama) :
docker compose down -v

# Attention : ./minio/data étant un bind mount, il n'est PAS supprimé par `down -v`.
# Pour réinitialiser MinIO, vider manuellement ./minio/data (hors .minio.sys si besoin).
```
