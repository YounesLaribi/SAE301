# HeyDo - Système de Supervision de Diffusion Sonore

Application web MVC en Python/Flask pour superviser des lecteurs audio distants.

- **Backend**: Flask, SQLAlchemy, Flask-Migrate
- **Base de Données**: SQLite (dev) ou PostgreSQL (prod)
- **Frontend**: Bootstrap 5, Jinja2, JS (Polling)

- `app/models/`: Définition des données (Lecteur, Playlist, Media, etc.)
- `app/controllers/`: Routes API et Panels Spécifiques
- `app/templates/` & `app/static/`: Interface Web (Jinja2 / CSS / JS)

## Installation & Lancement

1. **Prérequis**: Python 3.8+
2. **Installation des dépendances**:
   Ouvrez un terminal dans le dossier du projet et lancez :
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancement de l'application**:
   ```bash
   python run.py
   ```

> **Note importante** : La base de données (SQLite) et les données de test (Admin, Rôles, Lecteurs exemples) sont créées **automatiquement** au tout premier lancement. Vous n'avez aucune commande de base de données à taper.

**Accès à l'interface :**
- URL : [http://localhost:5001](http://localhost:5001)

**Identifiants de test :**
- **Admin** (Supervision & Gestion) : `admin` / `admin`
- **Marketing** (Playlists & Musique) : `marketing` / `marketing`
- **Sales** (Publicités & Urgences) : `sales` / `sales`


## API Lecteurs (Documentation Simplifiée)

Authentification via Header `X-API-KEY`.

### 1. Heartbeat
**POST** `/api/players/<id>/heartbeat`
Body:
```json
{
  "now_playing": "Title - Artist",
  "local_main_playlist_hash": "hash_string",
  "local_fallback_hash": "hash_string",
  "is_audio_playing": true
}
```

### 2. Récupérer Playlist
**GET** `/api/players/<id>/playlists/main`
**GET** `/api/players/<id>/playlists/fallback`

### 3. Commandes
**GET** `/api/players/<id>/commands`

## Scénarios de Test (Manuel)

1. **Coupure Réseau**: Arrêter d'envoyer des heartbeats pour un lecteur. Attendre 1 minute. Vérifier que le statut passe à KO sur le dashboard.
2. **Coupure Électrique (Simulée)**: Envoyer un heartbeat avec `"is_audio_playing": false`. Vérifier l'alerte "NO_AUDIO" sur le dashboard.
3. **Mise à jour Playlist**: Modifier la playlist dans l'admin. Le hash serveur change. Au prochain heartbeat du lecteur (avec l'ancien hash), une alerte "Playlist Outdated" apparaît.
4. **Planning Pub**: Vérifier via l'API `/api/players/<id>/playlists/main` que des pubs (AD) sont insérées toutes les N musiques.
