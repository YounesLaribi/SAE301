from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models.Utilisateur import Utilisateur
from app.models.Role import Role
from functools import wraps
from app.services.UserService import UserService

# Instance du service
user_service = UserService()

# Définition du Blueprint Utilisateur
user_bp = Blueprint('user', __name__)

# Décorateur personnalisé pour sécuriser l'accès aux administrateurs.
# (Fonction utilitaire dupliquée ou à déplacer dans utils ? Conservée ici pour le moment car spécifique à la gestion des utilisateurs)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role or current_user.role.nom != 'Admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# LISTE DES UTILISATEURS (Section sensible)
@user_bp.route('/users')
@login_required
@admin_required
def users_list():
    """
    Affiche tous les utilisateurs et leurs rôles respectifs.
    """
    users = user_service.get_all_users() # Récupération de tous les comptes
    roles = user_service.get_all_roles() # Pour le formulaire d'ajout
    return render_template('users.html', users=users, roles=roles)

# AJOUT D'UN UTILISATEUR
@user_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def user_add():
    """
    Crée un nouvel utilisateur avec mot de passe haché.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    role_id = request.form.get('role_id')
    
    # Vérification d'unicité
    
    success, message = user_service.create_user(username, password, role_id)
    
    if not success:
        flash(message)
        if "existe déjà" in message:
             return redirect(url_for('user.users_list'))
    else:
        flash(message)
        
    return redirect(url_for('user.users_list'))

# SUPPRESSION D'UN UTILISATEUR
@user_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    """
    Supprime un compte utilisateur, sauf le compte 'admin' de secours.
    """
    success, message = user_service.delete_user(user_id)
    
    flash(message)
    return redirect(url_for('user.users_list'))
