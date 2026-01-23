from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        print("Liste des routes enregistrées :")
        for rule in app.url_map.iter_rules():
            print(f"{rule} -> {rule.endpoint}")
            
    print("\n---------------------------------------------------")
    print("Application démarrée. Accédez à : http://127.0.0.1:5001")
    print("---------------------------------------------------\n")
    
    app.run(host='0.0.0.0', debug=True, port=5001)
