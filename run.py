from app import create_app, db

# Point d'entrée principal pour lancer le serveur Web HeyDo.
app = create_app()

if __name__ == '__main__':
    # Au lancement, on affiche la liste des chemins (URLs) disponibles.
    with app.app_context():
        print("Liste des routes enregistrées :")
        for rule in app.url_map.iter_rules():
            print(f"{rule} -> {rule.endpoint}")
            
    print("\n---------------------------------------------------")
    print("Application démarrée. Accédez à : http://127.0.0.1:5001")
    print("---------------------------------------------------\n")
    
    # Lancement du serveur de développement.
    # debug=True permet de voir les erreurs en direct.
    # port=5001 pour éviter les conflits réseau.
    app.run(debug=True, port=5001)
