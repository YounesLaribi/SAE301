from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.Utilisateur import Utilisateur

# ce module gere l'authentification et les sessions utilisateurs.
# definition du blueprint 'auth' pour gerer les routes de connexion/deconnexion.
# le nom 'auth' est conserve pour maintenir la compatibilite avec les templates (url_for('auth.login')).
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    gere la connexion des utilisateurs. 
    verifie les identifiants et cree une session securisee.
    """
    if request.method == 'POST':
        # recuperation des donnees du formulaire
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Recherche de l'utilisateur via le service
        from app.services.AuthService import AuthService
        auth_service = AuthService()
        user = auth_service.authenticate_user(username, password)
        
        if user:
            login_user(user) # Flask-Login crée la session
            # redirection vers le tableau de bord administrateur apres connexion reussie
            return redirect(url_for('admin.dashboard')) 
            
        # alerte de securite en cas d'echec
        flash('Identifiant ou mot de passe invalide')
    
    # Affichage du formulaire de connexion
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required # il faut etre connecte pour se deconnecter
def logout():
    """
    detruit la session actuelle de l'utilisateur.
    """
    logout_user() # Suppression des cookies de session
    return redirect(url_for('auth.login'))
