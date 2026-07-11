# postgres

## Rôle
Base de données **relationnelle** du template. Héberge la table `iris`, initialisée au
premier démarrage à partir de `postgres/Iris.csv`. Sert de cible SQL pour les conteneurs
`miniconda` et `streamlit`.

## Container(s)
| Container | Image | Port interne | Port exposé | Rôle |
|---|---|---|---|---|
| `postgres_db` | `postgres:15` | `5432` | `${POSTGRES_PORT}` (`5432`) | Serveur PostgreSQL |

## API / Interface
Aucune API HTTP — accès via le protocole PostgreSQL (port `5432`). Clients dans ce
projet : SQLAlchemy + `psycopg2` (`python/src/connexion_bdd.py`, `streamlit/src/app.py`).

## Variables d'environnement
| Variable | Description | Défaut (`.env`) |
|---|---|---|
| `POSTGRES_USER` | Superutilisateur créé au boot | `myuser` |
| `POSTGRES_PASSWORD` | Mot de passe associé | `mypassword` |
| `POSTGRES_DB` | Base créée au boot | `mydatabase` |
| `POSTGRES_PORT` | Port publié sur l'hôte | `5432` |

> `DATABASE_URL` (`.env`) et `POSTGRES_HOST` (défaut `postgres`, lu côté code) permettent
> aussi la connexion applicative.

## Dépendances
Aucune dépendance amont. Dépendants : `miniconda` et `streamlit` attendent son
healthcheck (`condition: service_healthy`).

## Persistence
- Volume nommé `postgres_data` → `/var/lib/postgresql/data`.
- Init au premier démarrage (volume vide) via les montages dans
  `/docker-entrypoint-initdb.d/` :
  - `postgres/init.sql` → crée la table `iris` puis `COPY` depuis le CSV ;
  - `postgres/Iris.csv` → données source (`150` lignes, en-tête `Id,SepalLengthCm,...`).

Schéma de la table `iris` (`postgres/init.sql`) :

| Colonne | Type |
|---|---|
| `id` | `INTEGER PRIMARY KEY` |
| `sepal_length_cm` | `DOUBLE PRECISION` |
| `sepal_width_cm` | `DOUBLE PRECISION` |
| `petal_length_cm` | `DOUBLE PRECISION` |
| `petal_width_cm` | `DOUBLE PRECISION` |
| `species` | `VARCHAR(50)` |

## Healthcheck
```yaml
test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
interval: 5s
timeout: 5s
retries: 5
```
