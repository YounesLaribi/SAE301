# Script utilitaire pour executer des migrations SQL manuelles ou correctifs sur la base de donnees.
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        with db.engine.connect() as con:
            con.execute(text("ALTER TABLE Lecteur ADD COLUMN ip_address VARCHAR(50)"))
            con.commit()
        print("Migration successful: Added ip_address to Lecteur.")
    except Exception as e:
        print(f"Migration result: {e}")
