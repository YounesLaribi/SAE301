import requests
import time
import json
import webbrowser
import os
import subprocess
import platform

# --- CONFIGURATION (A MODIFIER SELON VOS VMS) ---
SERVER_IP = "192.168.1.36"       # L'IP de votre VM Serveur
SERVER_PORT = "5001"             # Le port Flask
SERVER_USER = "oussama"          # Le nom d'utilisateur SSH de la VM Serveur
SERVER_PATH = "~/SAE301/app/static/audio/" # Le dossier source sur le serveur

LOCAL_MUSIC_DIR = "musiques_locales" # Dossier local sur le client
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
            # On cherche les fichiers
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
    """Joue un fichier audio."""
    if SYSTEM == "Windows":
        # Mode Dégradé
        print(f" [Lecture Windows] Ouverture URL : {filename_or_url}")
        webbrowser.open(filename_or_url, new=2)
        return "SimulatedProcess"

    # Mode PRO (Linux)
    filename = filename_or_url.split("/")[-1] 
    local_path = os.path.join(LOCAL_MUSIC_DIR, filename)

    if not os.path.exists(local_path):
        print(f" [Erreur Lecture] Fichier introuvable localement : {local_path}")
        try:
            print(f"   [DEBUG] Contenu du dossier '{LOCAL_MUSIC_DIR}' : {os.listdir(LOCAL_MUSIC_DIR)}")
        except:
             print("   [DEBUG] Dossier inaccessible.")
        print(" (Avez-vous bien configuré le Rsync ?)")
        return None

    print(f" [Lecture Linux] Lancement MPV : {local_path} (Loop={loop})")
    try:
        subprocess.run(["pkill", "mpv"], capture_output=True)
        
        cmd = ["mpv", "--no-terminal", local_path]
        if loop:
            cmd.append("--loop")
            
        return subprocess.Popen(cmd)
    except Exception as e:
        print(f" [Erreur MPV] {e}")
        return None

def stop_audio():
    if SYSTEM == "Windows":
        print(" [Stop] Impossible de fermer le navigateur automatiquement.")
    else:
        print(" [Stop] Arrêt du lecteur MPV.")
        subprocess.run(["pkill", "mpv"], capture_output=True)
        time.sleep(0.5)

def main():
    print(f"--- CLIENT LECTEUR (AUTO-IP) ---")
    print(f"Serveur API : {SERVER_API_URL}")
    print(f"Utilisateur SSH : {SERVER_USER}")
    
    ensure_local_dir()
    sync_files_rsync()

    current_track_url = None
    is_playing = False
    is_urgent_mode = False
    current_process = None
    manual_stop_req = False
    
    # ID du joueur récupéré dynamiquement
    dynamic_player_id = None 
    
    while True:
        try:
            # --- VERIFICATION FIN LECTURE (AUTO-RESUME) ---
            if current_process and not isinstance(current_process, str) and current_process.poll() is not None:
                if not is_urgent_mode:
                    print("\n [INFO] Fin de lecture détectée. Retour à la normale.")
                    is_playing = False
                    current_track_url = None
                    current_process = None
            
            # --- HEARTBEAT ---
            payload = {
                "is_audio_playing": is_playing,
                "current_track": current_track_url,
                "startup": False 
            }
            
            try:
                if dynamic_player_id:
                     url = f"{SERVER_API_URL}/api/players/{dynamic_player_id}/heartbeat"
                else:
                     url = f"{SERVER_API_URL}/api/heartbeat/auto"
                
                response = requests.post(url, json=payload, timeout=2)
                
            except:
                print(" [!] Serveur injoignable (Timeout)")
                time.sleep(HEARTBEAT_INTERVAL)
                continue

            if response.status_code == 200:
                data = response.json()
                print(".", end="", flush=True)
                
                # Si le serveur nous a donné notre ID, on le stocke
                if 'player_id' in data and not dynamic_player_id:
                    dynamic_player_id = data['player_id']
                    print(f"\n [INFO] Authentifié avec succès ! (PLAYER ID: {dynamic_player_id})")
                
                # --- COMMANDES ---
                cmd = data.get("broadcast_command")
                
                if cmd == "STOP":
                    if is_playing or not manual_stop_req: 
                        print("\n [ORDRE] STOP TOUT !")
                        stop_audio()
                        is_playing = False
                        current_track_url = None
                        is_urgent_mode = False
                        current_process = None
                        manual_stop_req = True

                elif cmd == "CANCEL":
                    if is_playing:
                        print("\n [ORDRE] ANNULATION DIFFUSION")
                        stop_audio()
                        is_playing = False
                        current_track_url = None
                        current_process = None
                        manual_stop_req = False 
                
                elif cmd and "URGENT:" in cmd:
                    parts = cmd.split("|")
                    url = parts[1] if len(parts) > 1 else ""
                    if url != current_track_url:
                        print(f"\n [ORDRE] URGENCE : {url}")
                        sync_files_rsync() 
                        current_process = play_audio(url, loop=True)
                        is_playing = True
                        current_track_url = url
                        is_urgent_mode = True
                        manual_stop_req = False

                elif cmd:
                    parts = cmd.split("|")
                    url = parts[1] if len(parts) > 1 else ""
                    print(f"\n [ORDRE] PUBLICITÉ : {url}")
                    sync_files_rsync()
                    current_process = play_audio(url, loop=False)
                    is_playing = True
                    current_track_url = url
                    manual_stop_req = False

                elif data.get("needs_sync_main"):
                    print("\n [INFO] Mise à jour playlist demandée...")
                    sync_files_rsync()
                else:
                    if is_urgent_mode:
                        print("\n [INFO] Fin de l'urgence. Arrêt de l'alarme.")
                        stop_audio()
                        is_urgent_mode = False
                        is_playing = False
                        current_track_url = None
                        current_process = None

                    if not is_playing and not manual_stop_req and dynamic_player_id:
                        r = requests.get(f"{SERVER_API_URL}/api/players/{dynamic_player_id}/playlists/main")
                        if r.status_code == 200:
                            tracks = r.json()
                            if tracks:
                                track = tracks[0]
                                url = track['file_url']
                                if url != current_track_url:
                                    print(f"\n [PLAYLIST] Nouvelle piste : {track['title']}")
                                    sync_files_rsync()
                                    proc = play_audio(url)
                                    if proc:
                                        current_process = proc
                                        current_track_url = url
                                        is_playing = True
                                    else:
                                        is_playing = False
                                        current_track_url = None
            
            elif response.status_code == 403:
                # IP Inconnue
                if not dynamic_player_id:
                     print(" [!] Client non reconnu par le serveur (IP not registered). En attente...", end="\r")
            else:
                print(f" [!] Erreur API: {response.status_code}")

        except Exception as e:
            print(f"\n [ERREUR CRITIQUE] {e}")
            time.sleep(5)

        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()
