# ollama

## Rôle
**Serveur LLM local** accéléré GPU. Expose l'API Ollama (port `11434`) et télécharge
automatiquement le modèle `phi4-mini:latest` au démarrage. Consommé par la section
« Ollama » de l'app Streamlit pour un chat de démonstration.

## Container(s)
| Container | Image | Port interne | Port exposé | Rôle |
|---|---|---|---|---|
| `ollama-server` | `ollama/ollama:latest` | `11434` | `${OLLAMA_PORT}` (`11434`) | Serveur d'inférence LLM |

`entrypoint` (compose) : `sh /entrypoint.sh` → monté depuis `ollama/entrypoint.sh`.

## API / Interface
API HTTP native Ollama sur `http://ollama:11434` (nom interne) :

| Méthode | Route | Rôle |
|---|---|---|
| `GET` | `/api/tags` | Liste des modèles disponibles |
| `GET` | `/api/version` | Version du serveur |
| `POST` | `/api/generate` | Génération de texte (`stream: false` utilisé) |

## Variables d'environnement
| Variable | Description | Défaut (`.env`) |
|---|---|---|
| `OLLAMA_HOST` | Adresse d'écoute | `0.0.0.0:11434` |
| `OLLAMA_ORIGINS` | Origines CORS autorisées | `*` |
| `OLLAMA_KEEP_ALIVE` | Durée de maintien du modèle en mémoire | `5m` |
| `OLLAMA_DEBUG` | Logs de debug | `false` |
| `OLLAMA_PORT` | Port publié sur l'hôte | `11434` |

## Dépendances
Aucune dépendance amont. Dépendants : `miniconda` et `streamlit` attendent son
healthcheck. **Réservation matérielle** : 1 GPU NVIDIA (`driver: nvidia`, `capabilities:
[gpu]`) — nécessite `nvidia-container-toolkit` sur l'hôte.

## Persistence
- Volume nommé `ollama_data` → `/root/.ollama` : conserve les modèles téléchargés entre
  redémarrages (évite un re-`pull` de `phi4-mini` à chaque boot).
- `ollama/entrypoint.sh` monté en lecture seule ; lance `ollama serve`, attend la
  disponibilité (timeout `300s`) puis `ollama pull phi4-mini:latest`.

> Le fichier `ollama/init-model.sh` existe dans le dépôt mais **n'est pas monté** par le
> `docker-compose.yml` (script d'init alternatif, non branché).

## Healthcheck
```yaml
test: ["CMD", "ollama", "list"]
interval: 30s
timeout: 10s
retries: 5
start_period: 60s
```
