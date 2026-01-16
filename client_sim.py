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
    print(f"Serveur cible : {SERVER_URL}")
    print("Démarrage...")

    # État local simulé
    current_track_url = None
    is_playing = False
    manual_stop_active = False # Nouveau flag pour l'arrêt forcé
    broadcast_end_time = 0 # Timestamp pour savoir quand l'alerte finit

    while True:
        try:
            # 1. Envoi du Heartbeat (Battement de coeur)
            print(f"[{time.strftime('%H:%M:%S')}] Envoi Heartbeat...", end="")
            
            payload = {
                "is_audio_playing": is_playing,
                "current_track": current_track_url
            }
            
            response = requests.post(f"{SERVER_URL}/api/players/{PLAYER_ID}/heartbeat", json=payload)
            
            if response.status_code == 200:
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
                        continue

                    elif msg.startswith("URGENT:"):
                        real_msg = msg.split("URGENT:")[1]
                        print(f"\n >>> ☢️ ALERTE INFINIE : {real_msg.upper()} ☢️ <<<")
                        print(" >>> BOUCLE ACTIVE - Attente de l'ordre STOP...")
                        manual_stop_active = False
                        broadcast_end_time = time.time() + 10 # On repousse la fin indéfiniment à chaque heartbeat
                        continue

                    else:
                        print(f"\n >>> 🚨 ALERTE REÇUE DU SERVEUR : {msg.upper()} 🚨 <<<")
                        print(" >>> INTERRUPTION immédiate de la musique en cours...")
                        print(" >>> Diffusion du message prioritaire (durée simulée de 10s)...\n")
                        manual_stop_active = False
                        broadcast_end_time = time.time() + 10 # On bloque la musique de fond pendant 10s
                        continue # On saute la fin de boucle pour ne pas lancer la musique de fond tout de suite
                    
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
                check_playlist_and_play()

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

def check_playlist_and_play():
    # Fonction bonus pour la démo : On va chercher la playlist et si on trouve un truc "Urgent" ou nouveau, on le joue
    # C'est une simulation simplifiée.
    try:
        r = requests.get(f"{SERVER_URL}/api/players/{PLAYER_ID}/playlists/main")
        if r.status_code == 200:
            tracks = r.json()
            if tracks:
                # Prenons le dernier ou le premier
                track = tracks[0]
                # Simuler le lancement (Uniquement si ce n'est pas déjà affiché)
                print(f" >> 🎵 Lecture de fond en cours : {track['title']} ({track['kind']})")
                print(f" >> (Simulation Audio: Lecture de {track['file_url']})")
                pass
    except:
        pass

if __name__ == "__main__":
    main()
