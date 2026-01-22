# HeyDo - Système de Supervision de Diffusion Sonore

Application web MVC en Python/Flask pour superviser des lecteurs audio distants.

- **Backend**: Flask 3, SQLAlchemy
- **Base de Données**: SQLite (fichier local `app.db`)
- **Frontend**: Bootstrap 5.3 + Jinja2 (Rendu excôté serveur)

### Structure
- `app/models/`: Données SQL (Lecteur, Playlist, Media, Musique, Planning)
- `app/controllers/`: Logique métier par fonctionnalité (Dashboard, Devices, Marketing, Sales, Auth)
- `app/services/`: Logique métier pure (indépendante du web)
- `app/templates/`: Vues HTML

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

### 1. Heartbeat (Battement de coeur)
**POST** `/api/players/<id>/heartbeat`
Body JSON :
```json
{
  "is_audio_playing": true,   // État de la lecture
  "current_track": "http://...", // URL en cours
  "startup": false           // Si le lecteur vient de redémarrer
}
```

### 2. Récupérer Playlist (Sync)
**GET** `/api/players/<id>/playlists/main`
*Retourne la liste des titres à jouer (selon l'heure et le planning).*

### 3. Commandes & Réponses
Le serveur répond au heartbeat avec des instructions :
- `broadcast_command`: "STOP", "CANCEL", ou "URGENT:Titre"
- `needs_sync_main`: true (demande de re-télécharger la playlist)

## Scénarios de Test (Manuel)

## Scénarios de Test (Manuel)

1. **Détection Hors Ligne (Timeout)** : Arrêtez le script `client_sim.py`. Après 15 secondes, rafraîchissez le dashboard : le lecteur passe en **KO (Rouge)**.
2. **Diffusion Urgente** : Allez dans le menu **Urgences**, choisissez un son et cliquez sur "Diffuser". Le client reçoit l'ordre `URGENT:...` instantanément (au prochain heartbeat).
3. **Planning Automatique** : Dans **Marketing**, assignez un son au créneau actuel. Le client va recevoir ce son dans sa playlist par défaut.
4. **Arrêt d'Urgence (Panic Button)** : Sur le Dashboard, cliquez sur **ARRÊTER TOUT LE SON**. Tous les clients reçoivent l'ordre `STOP` et bloquent la lecture.
