import requests
import time
import json
import webbrowser
import os
import subprocess
import platform

# --- CONFIGURATION (A MODIFIER SELON VOS VMS) ---
# --- CONFIGURATION (A MODIFIER SELON VOS VMS) ---
SERVER_IP = "192.168.1.36"       # L'IP de votre VM Serveur
SERVER_PORT = "5001"             # Le port Flask
SERVER_USER = "oussama"          # Le nom d'utilisateur SSH de la VM Serveur
SERVER_PATH = "~/SAE301/app/static/audio/" # Le dossier source sur le serveur

LOCAL_MUSIC_DIR = "musiques_locales" # Dossier local sur le client
PLAYER_ID = 1
HEARTBEAT_INTERVAL = 3

# Construction de l'URL HTTP pour l'API
SERVER_API_URL = f"http://{SERVER_IP}:{SERVER_PORT}"

# --- DETECTION DE L'OS ---
SYSTEM = platform.system() # 'Windows' ou 'Linux'
print(f"--- SYSTEME DETECTE : {SYSTEM} ---")

def ensure_local_dir():
    if not os.path.exists(LOCAL_MUSIC_DIR):
        os.makedirs(LOCAL_MUSIC_DIR)
        print(f"Dossier créé : {LOCAL_MUSIC_DIR}")

def sync_files_rsync():
    """Synchronise les fichiers musique via RSYNC (Linux uniquement)"""
    if SYSTEM == "Windows":
        print(" [!] Rsync ignoré sur Windows (Mode Simulation Web)")
        return

    print(" [Rsync] Synchronisation des fichiers...")
    ensure_local_dir()
    
    # Commande: rsync -avz --delete user@ip:source/ destination/
    # --delete permet de supprimer les fichiers qui n'existent plus sur le serveur (bon pour le nettoyage)
    cmd = [
        "rsync", "-avz", "--timeout=10",
        f"{SERVER_USER}@{SERVER_IP}:{SERVER_PATH}",
        f"{LOCAL_MUSIC_DIR}/"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # Analyse de la sortie pour voir si des fichiers ont été copiés
            output_lines = result.stdout.strip().splitlines()
            # On cherche les fichiers (ce qui n'est ni le header ni le footer de stats)
            files_transferred = [line for line in output_lines 
                               if line.strip() and 
                               not line.startswith("sending incremental file list") and 
                               not line.startswith("sent ") and 
                               not line.startswith("total size is") and
                               not line.startswith("speedup is")]

            if files_transferred:
                print(f" [Rsync] Mise à jour effectuée ({len(files_transferred)} fichiers).")
                for f in files_transferred:
                    print(f"   + {f}")
            else:
                print(" [Rsync] Déjà à jour (Aucun changement nécessaire).")
        else:
            print(" [Rsync] ERREUR !")
            print(result.stderr)
    except Exception as e:
        print(f" [Rsync] Exception : {e}")

def play_audio(filename_or_url, loop=False):
    """Joue un fichier audio.
       - Sur Linux : Joue le fichier LOCAL via 'mpv' (ou 'mpg123')
       - Sur Windows : Ouvre l'URL via le navigateur (Mode Dégradé)
    """
    if SYSTEM == "Windows":
        # Mode Dégradé
        print(f" [Lecture Windows] Ouverture URL : {filename_or_url}")
        webbrowser.open(filename_or_url, new=2)
        return

    # Mode PRO (Linux)
    # On joue le fichier LOCAL qui a été téléchargé par Rsync
    # On extrait juste le nom du fichier de l'URL (ex: 'http://.../son.mp3' -> 'son.mp3')
    filename = filename_or_url.split("/")[-1] 
    local_path = os.path.join(LOCAL_MUSIC_DIR, filename)

    if not os.path.exists(local_path):
        print(f" [Erreur Lecture] Fichier introuvable localement : {local_path}")
        print(" (Avez-vous bien configuré le Rsync ?)")
        return

    print(f" [Lecture Linux] Lancement MPV : {local_path} (Loop={loop})")
    # On lance mpv en arrière plan (ou bloquant si on veut, mais attention au heartbeat)
    # Ici on utilise Popen pour ne pas bloquer le script
    try:
        # On tue les anciennes instances mpv pour eviter le capharnaüm (facultatif)
        subprocess.run(["pkill", "mpv"], capture_output=True)
        
        cmd = ["mpv", "--no-terminal", local_path]
        if loop:
            cmd.append("--loop")
            
        subprocess.Popen(cmd)
    except Exception as e:
        print(f" [Erreur MPV] {e}")

def stop_audio():
    if SYSTEM == "Windows":
        print(" [Stop] Impossible de fermer le navigateur automatiquement.")
    else:
        print(" [Stop] Arrêt du lecteur MPV.")
        subprocess.run(["pkill", "mpv"], capture_output=True)


def main():
    print(f"--- CLIENT LECTEUR (ID: {PLAYER_ID}) ---")
    print(f"Serveur API : {SERVER_API_URL}")
    print(f"Utilisateur SSH : {SERVER_USER}")
    
    ensure_local_dir()
    
    # 1. Sync initiale au démarrage
    sync_files_rsync()

    current_track_url = None
    is_playing = False
    
    while True:
        try:
            # --- HEARTBEAT ---
            payload = {
                "is_audio_playing": is_playing,
                "current_track": current_track_url,
                "startup": False 
            }
            
            try:
                response = requests.post(f"{SERVER_API_URL}/api/players/{PLAYER_ID}/heartbeat", json=payload, timeout=2)
            except:
                print(" [!] Serveur injoignable (Timeout)")
                time.sleep(HEARTBEAT_INTERVAL)
                continue

            if response.status_code == 200:
                data = response.json()
                print(".", end="", flush=True) # Petit point pour dire "je suis vivant"
                
                # --- COMMANDES (STOP/URGENT) ---
                cmd = data.get("broadcast_command")
                
                if cmd == "STOP":
                    if is_playing: # On stop seulement si ça jouait
                        print("\n [ORDRE] STOP TOUT !")
                        stop_audio()
                        is_playing = False
                        current_track_url = None
                
                elif cmd and "URGENT:" in cmd:
                    # Format: URGENT:Titre|URL
                    parts = cmd.split("|")
                    url = parts[1] if len(parts) > 1 else ""
                    if url != current_track_url:
                        print(f"\n [ORDRE] URGENCE : {url}")
                        # On lance une sync rapide au cas où on n'a pas le fichier alerte
                        sync_files_rsync() 
                        play_audio(url, loop=True)
                        is_playing = True
                        current_track_url = url
                    else:
                        # Déjà en train de jouer l'urgence, on ne fait rien
                        pass
                
                # --- SYNC PLAYLIST ---
                elif data.get("needs_sync_main"):
                    print("\n [INFO] Mise à jour playlist demandée...")
                    sync_files_rsync()
                # --- LECTURE PROGRAMMEE (Fond) ---
                else:
                    # On demande la playlist standard
                    # Note: Dans une vraie implémentation, on garderait la playlist en mémoire.
                    # Ici on fait simple : on demande "quoi jouer" à chaque boucle si on ne joue rien.
                    if not is_playing: # Si on ne joue rien
                        r = requests.get(f"{SERVER_API_URL}/api/players/{PLAYER_ID}/playlists/main")
                        if r.status_code == 200:
                            tracks = r.json()
                            if tracks:
                                track = tracks[0]
                                url = track['file_url']
                                 
                                 # Si c'est un nouveau titre
                                if url != current_track_url:
                                    print(f"\n [PLAYLIST] Nouvelle piste : {track['title']}")
                                    sync_files_rsync() # Check rapide
                                    play_audio(url)
                                    current_track_url = url
                                    is_playing = True
                                     
            else:
                print(f" [!] Erreur API: {response.status_code}")

        except Exception as e:
            print(f"\n [ERREUR CRITIQUE] {e}")
            time.sleep(5)

        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()
