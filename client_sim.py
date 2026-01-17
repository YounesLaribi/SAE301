import requests
import time
import json
import webbrowser
import os

# CONFIGURATION
SERVER_URL = "http://localhost:5001"
PLAYER_ID = 1  # L'ID du lecteur que vous simulez (doit exister en base) 1 = paris 2 = lyon
HEARTBEAT_INTERVAL = 3  # En secondes

def main():
    print(f"--- SIMULATEUR CLIENT LECTEUR (ID: {PLAYER_ID}) ---")
    print("--- VERSION 2.0 (FIX_URL) ---")
    print(f"Serveur cible : {SERVER_URL}")


    # État local simulé
    current_track_url = None
    is_playing = False
    manual_stop_active = False # Nouveau flag pour l'arrêt forcé
    manual_stop_active = False # Nouveau flag pour l'arrêt forcé
    broadcast_end_time = 0 # Timestamp pour savoir quand l'alerte finit
    last_played_msg = None # Pour éviter de rouvrir l'onglet audio 50 fois
    
    first_connection = True # Pour signaler au serveur qu'on vient de rebooter

    while True:
        try:
            # 1. Envoi du Heartbeat (Battement de coeur)
            print(f"[{time.strftime('%H:%M:%S')}] Envoi Heartbeat...", end="")
            
            payload = {
                "is_audio_playing": is_playing,
                "current_track": current_track_url,
                "startup": first_connection 
            }
            
            response = requests.post(f"{SERVER_URL}/api/players/{PLAYER_ID}/heartbeat", json=payload)
            
            if response.status_code == 200:
                # Après le premier succès, on repasse à False
                if first_connection: first_connection = False

                print(" OK (Connecté)")
                data = response.json()
                
                # GESTION DU BROADCAST PRIORITAIRE
                if data.get("broadcast_command"):
                    msg = data.get("broadcast_command")
                    
                    if msg == "STOP":
                        print("\n >>> 🛑 ORDRE D'ARRÊT REÇU (STOP) 🛑 <<<")
                        print(" >>> Le son est coupé jusqu'à nouvel ordre.\n")
                        manual_stop_active = True
                        is_playing = False
                    
                    elif msg == "CANCEL":
                        print("\n >>> ↩️ FIN DE DIFFUSION / ANNULATION ↩️ <<<")
                        print(" >>> Reprise du programme musical normal...\n")
                        manual_stop_active = False
                        broadcast_end_time = 0
                        last_played_msg = None # Reset
                        continue

                    else:
                        # Parsing du message "Titre|URL"
                        title = msg
                        url = None
                        if "|" in msg:
                            parts = msg.split("|")
                            title = parts[0]
                            if len(parts) > 1: url = parts[1].strip()
                        
                        if url and url.startswith("/"):
                             url = f"{SERVER_URL}{url}"

                        # Logique URGENT vs STANDARD
                        is_urgent = msg.startswith("URGENT:")
                        if is_urgent:
                            # Nettoyage si le préfixe est resté (théoriquement non si géré avant)
                            title = title.replace("URGENT:", "")
                            print(f"\n >>> ☢️ ALERTE INFINIE : {title.upper()} ☢️ <<<")
                        else:
                             print(f"\n >>> 🚨 ALERTE REÇUE : {title.upper()} 🚨 <<<")

                        # LECTURE AUDIO RÉELLE (Une seule fois par message)
                        if url and url != last_played_msg:
                            # print(f" >>> 🔊 LECTURE AUDIO DÉCLENCHÉE : '{url}'")
                            try:
                                webbrowser.open(url, new=2)
                            except:
                                print(" (Erreur ouverture URL)")
                            last_played_msg = url # On mémorise pour pas spammer les onglets

                        # Logique de boucle
                        manual_stop_active = False
                        if is_urgent:
                            print(" >>> BOUCLE ACTIVE - Attente de l'ordre STOP...")
                            broadcast_end_time = time.time() + 10 
                            continue
                        else:
                            print(" >>> Diffusion du message prioritaire (durée simulée de 10s)...\n")
                            broadcast_end_time = time.time() + 10 
                            continue
                    
                # Vérification des commandes ou synchronisation (simulée ici basiquement)
                if data.get("needs_sync_main") and not data.get("broadcast_command"):
                     # On ne sync que si ce n'est pas déjà géré par le broadcast direct
                    print(" >> Ordre reçu : Synchronisation Playlist demandée !")
                    sync_playlist()

            else:
                print(f" ERREUR HTTP {response.status_code}")

            # 2. Simulation de lecture (Polling de playlist pour la démo)
            
            if manual_stop_active:
                # Si arrêt forcé, on ne fait rien
                pass
            elif time.time() < broadcast_end_time:
                # Si une alerte est en train de parler, on ne relance pas la musique de fond
                print(f"    (Priorité en cours... Background music en pause)")
            else:
                # Gestion de la musique de fond (Main Loop)
                try:
                    r_playlist = requests.get(f"{SERVER_URL}/api/players/{PLAYER_ID}/playlists/main")
                    if r_playlist.status_code == 200:
                        tracks = r_playlist.json()
                        # DEBUG
                        # print(f"DEBUG: Tracks={len(tracks)} LastMsg={last_played_msg}") 
                        
                        if tracks:
                            track = tracks[0]
                            background_url = track['file_url'].strip() if track['file_url'] else ""
                            bg_title = track['title']
                            
                            if background_url and background_url.startswith("/"):
                                background_url = f"{SERVER_URL}{background_url}"
                            
                            # Si la musique change ou qu'on sort d'une alerte (le simulateur considère que c'est une nouvelle session)
                            # Note: Pour éviter de relancer la musique en boucle, on vérifie last_played_msg
                            if background_url and background_url != last_played_msg:
                                print(f" >>> 🎵 REPRISE MUSIQUE DE FOND : {bg_title}")
                                # print(f" >>> 🔊 LECTURE AUDIO : '{background_url}'") # Debug URL
                                try:
                                    webbrowser.open(background_url, new=2)
                                except: pass
                                last_played_msg = background_url
                        else:
                             print(" (Aucune musique de fond planifiée)")
                    else:
                        print(f" (Erreur API Playlist: {r_playlist.status_code})")
                except Exception as e:
                    print(f" (Erreur Playlist: {e})")

        except requests.exceptions.ConnectionError:
            print(" ERREUR : Impossible de contacter le serveur (Est-il lancé ?)")
        except Exception as e:
            print(f" ERREUR INCONNUE : {e}")

        time.sleep(HEARTBEAT_INTERVAL)

def sync_playlist():
    # Récupération de la playlist
    try:
        r = requests.get(f"{SERVER_URL}/api/players/{PLAYER_ID}/playlists/main")
        if r.status_code == 200:
            tracks = r.json()
            print(f" >> Playlist reçue : {len(tracks)} titres")
            for t in tracks:
                print(f"    - {t['title']} ({t['file_url']})")
    except Exception as e:
        print(f"Echec sync: {e}")



if __name__ == "__main__":
    main()
