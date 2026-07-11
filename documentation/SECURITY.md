# Sécurité — Template-services-docker

> Ce projet est un **template de développement local**. La posture ci-dessous reflète cet
> usage : plusieurs points seraient à durcir avant toute exposition réseau ou mise en
> production. Les risques connus sont listés honnêtement en fin de document.

## Secrets & configuration

Les secrets (identifiants BDD, MinIO, config Ollama) sont centralisés dans `.env`, chargé
par Docker Compose (`env_file: .env`) et par les apps (`python-dotenv`).

| Secret | Où | Valeur par défaut | Rotation |
|---|---|---|---|
| `POSTGRES_PASSWORD` | `.env` | `mypassword` | manuelle |
| `MONGO_ROOT_PASSWORD` | `.env` | `your_secure_password` | manuelle |
| `MINIO_ROOT_PASSWORD` | `.env` | `minioadmin` | manuelle |
| `MINIO_ROOT_USER` | `.env` | `minioadmin` | manuelle |

> ⚠️ **`.env` est présent dans le dépôt** et contient des mots de passe. Un `.env` avec
> secrets ne doit jamais être committé. Il n'existe pas de `.env.example`.
> Recommandation : ajouter `.env` au `.gitignore`, committer à la place un `.env.example`
> sans valeurs sensibles, et faire tourner les mots de passe déjà exposés.

## Isolation réseau

Tous les services partagent le réseau bridge `app-network` et se résolvent par nom de
service. Ports publiés sur l'hôte :

| Service | Exposé à l'hôte ? | Port(s) | Justification |
|---|---|---|---|
| `postgres` | oui | `5432` | Accès client SQL depuis l'hôte |
| `mongodb` | oui | `27017` | Accès client Mongo depuis l'hôte |
| `ollama` | oui | `11434` | Appels API LLM |
| `streamlit` | oui | `8501` | Interface web |
| `minio` | oui | `9000` + `9001` | API S3 + console |
| `miniconda` | non | — | Conteneur de calcul interne |
| `mc-client-init` | non | — | Job d'init éphémère |

> ⚠️ En démo locale ces ports sont pratiques ; sur une machine exposée, restreindre les
> publications (`127.0.0.1:<port>:...`) ou ne pas publier les BDD.

## Dépendances

- `streamlit/requirements.txt` : versions **épinglées** (ex. `streamlit==1.28.2`).
- `python/requirements.txt` / `environment.yml` : versions **minimales** non figées
  (`pandas>=2.0.0`, ...) → builds non reproductibles.
- Images `ollama`, `minio`, `minio/mc` en `latest` → non reproductibles.

```bash
# Audit possible des dépendances Python (non configuré dans le projet) :
pip-audit -r streamlit/requirements.txt
```

## Conteneurs

- Images officielles (`postgres`, `mongo`, `ollama`, `minio`, `continuumio/miniconda3`,
  `python:3.12-slim`).
- Exécution **root** dans les conteneurs (aucun `USER` non-root déclaré dans les
  Dockerfiles) — acceptable en local, à durcir sinon.
- `ollama` requiert l'accès au GPU hôte (`nvidia`), ce qui élargit la surface.

## Données & accès

- Identifiants **par défaut faibles** sur les 4 stores (voir tableau des secrets).
- `OLLAMA_ORIGINS=*` : l'API Ollama accepte toutes les origines CORS.
- Aucune donnée personnelle : le seul jeu de données est **Iris** (public).

## Risques connus (non traités)

- ⚠️ **`.env` versionné avec secrets** — à retirer du dépôt et ajouter au `.gitignore`.
- ⚠️ **Identifiants par défaut** (`minioadmin`, `admin`/`your_secure_password`,
  `myuser`/`mypassword`) — à changer avant tout usage non-local.
- ⚠️ **`OLLAMA_ORIGINS=*`** — restreindre aux origines légitimes hors démo.
- ⚠️ **Ports BDD publiés sur l'hôte** — limiter à `127.0.0.1` ou supprimer la publication
  en environnement partagé.
- ⚠️ **Conteneurs en root** — définir un utilisateur non-root pour les images applicatives.
- ⚠️ **Tags `latest`** — épingler pour éviter des mises à jour non maîtrisées.
