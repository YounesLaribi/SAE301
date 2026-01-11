from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app.models.Utilisateur import Utilisateur

# Ce module gère l'authentification et les sessions utilisateurs.
# Définition du Blueprint 'auth' pour gérer les routes de connexion/déconnexion.
# Le nom 'auth' est conservé pour maintenir la compatibilité avec les templates (url_for('auth.login')).
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gère la connexion des utilisateurs. 
    Vérifie les identifiants et crée une session sécurisée.
    """
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Recherche de l'utilisateur via le service
        from app.services.AuthService import AuthService
        auth_service = AuthService()
        user = auth_service.authenticate_user(username, password)
        
        if user:
            login_user(user) # Flask-Login crée la session
            # Redirection vers le tableau de bord administrateur après connexion réussie
            return redirect(url_for('admin.dashboard')) 
            
        # Alerte de sécurité en cas d'échec
        flash('Identifiant ou mot de passe invalide')
    
    # Affichage du formulaire de connexion
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required # Il faut être connecté pour se déconnecter
def logout():
    """
    Détruit la session actuelle de l'utilisateur.
    """
    logout_user() # Suppression des cookies de session
    return redirect(url_for('auth.login'))
