from flask import Blueprint, render_template, redirect, url_for, abort, jsonify, request, flash
from flask_login import login_required, current_user
from app.services.DashboardService import DashboardService

dashboard_service = DashboardService()

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def tableau_de_bord():
    if not current_user.role:
        return "Erreur: Rôle non défini pour cet utilisateur.", 403
        
    role = current_user.role.nom
    if role == 'Marketing':
        return redirect(url_for('admin.tableau_bord_marketing'))
    elif role == 'Sales':
        return redirect(url_for('admin.tableau_bord_ventes'))
        
    stats = dashboard_service.get_admin_stats()
    
    return render_template('dashboard.html', **stats)

@admin_bp.route('/it')
@login_required
def surveillance_it():
    data = dashboard_service.get_monitoring_data()
    return render_template('admin_dashboard.html', **data)

@admin_bp.route('/dashboard/players/add', methods=['POST'])
@login_required
def ajouter_lecteur():
    from app.services.DeviceService import DeviceService 
    device_service = DeviceService()
    
    nom = request.form.get('nom')
    ip = request.form.get('ip')
    localisation = request.form.get('localisation')
    
    if nom and localisation:
        player = device_service.create_player(nom, localisation, ip_address=ip)
        if player:
            flash(f'Lecteur "{nom}" ajouté avec succès (ID: {player.id_lecteur}).', 'success')
        else:
            flash('Erreur lors de la création du lecteur.', 'danger')
    else:
         flash('Champs Nom et Localisation requis.', 'warning')
         
    return redirect(url_for('admin.tableau_de_bord'))

@admin_bp.route('/marketing')
@login_required
def tableau_bord_marketing():
    if current_user.role.nom not in ['Admin', 'Marketing']:
        abort(403)
    data = dashboard_service.get_marketing_data()
    return render_template('marketing.html', **data)

@admin_bp.route('/sales')
@login_required
def tableau_bord_ventes():
    if current_user.role.nom not in ['Admin', 'Sales']:
        abort(403)
    data = dashboard_service.get_sales_data()
    return render_template('sales.html', **data)

@admin_bp.route('/broadcast/stop', methods=['POST'])
@login_required
def arreter_diffusion():
    dashboard_service.trigger_stop_music()
    flash('Arrêt d\'urgence envoyé à tous les lecteurs.', 'danger')
    return redirect(request.referrer or url_for('admin.tableau_de_bord'))

@admin_bp.route('/sales/stop', methods=['POST'])
@login_required
def arreter_ventes():
    dashboard_service.trigger_cancel_broadcast()
    flash('Diffusion Sales annulée. Reprise de la musique.', 'info')
    return redirect(url_for('admin.tableau_bord_ventes'))

@admin_bp.route('/marketing/stop', methods=['POST'])
@login_required
def arreter_marketing():
    dashboard_service.disable_planning()
    dashboard_service.trigger_stop_music()
    flash('Mode Automatique DÉSACTIVÉ. Musique arrêtée (Silence).', 'warning')
    return redirect(url_for('admin.tableau_bord_marketing'))

@admin_bp.route('/marketing/planning/save', methods=['POST'])
@login_required
def sauvegarder_planning():
    matin = request.form.get('matin')
    apres_midi = request.form.get('apres_midi')
    
    dashboard_service.save_planning(matin, apres_midi)
    
    nom_matin = "Aucun"
    nom_pm = "Aucun"
    
    if matin:
        m = dashboard_service.get_track_by_id(int(matin))
        if m: nom_matin = m.nom
        
    if apres_midi:
        m = dashboard_service.get_track_by_id(int(apres_midi))
        if m: nom_pm = m.nom
    
    flash(f'Mode Automatique ACTIVÉ. Matin: {nom_matin} / Après-midi: {nom_pm}', 'success')
    return redirect(url_for('admin.tableau_bord_marketing'))

@admin_bp.route('/urgent/stop', methods=['POST'])
@login_required
def arreter_urgence():
    dashboard_service.trigger_stop_urgent()
    flash('fin de l\'alerte urgente. reprise de la musique.', 'success')
    return redirect(url_for('admin.tableau_bord_urgence'))

@admin_bp.route('/sales/broadcast', methods=['POST'])
@login_required
def diffuser_vente():
    media_id = request.form.get('message')
    if media_id:
        if dashboard_service.trigger_ad_broadcast(media_id):
             flash('diffusion publicitaire lance.', 'warning')
        else:
             flash('ereur : media introuvable.', 'danger')
    else:
        flash('Erreur : Aucun message sélectionné.', 'danger')
    return redirect(url_for('admin.tableau_bord_ventes'))

@admin_bp.route('/api/admin/summary')
@login_required
def resume():
    return jsonify(dashboard_service.get_summary_json())

@admin_bp.route('/media')
@login_required
def titres():
    medias = dashboard_service.get_all_tracks()
    return render_template('tracks.html', tracks=medias)

@admin_bp.route('/media/add', methods=['POST'])
@login_required
def ajouter_titre():
    title = request.form.get('title')
    url = request.form.get('url')
    kind = request.form.get('kind')
    
    if title and url:
        dashboard_service.add_track_to_library(title, url, kind)
        flash('Titre ajouté avec succès.', 'success')
    else:
        flash('Erreur: Titre et URL requis.', 'danger')
        
    return redirect(url_for('admin.titres'))

@admin_bp.route('/media/delete/<int:track_id>', methods=['POST'])
@login_required
def supprimer_titre(track_id):
    if current_user.role.nom != 'Admin':
        abort(403)
        
    if dashboard_service.delete_track(track_id):
        flash('Titre supprimé.', 'success')
    else:
        flash('Erreur lors de la suppression.', 'danger')
        
    return redirect(url_for('admin.titres'))

@admin_bp.route('/media/edit/<int:track_id>', methods=['GET', 'POST'])
@login_required
def modifier_titre(track_id):
    if current_user.role.nom != 'Admin':
        abort(403)
        
    track = dashboard_service.get_track_by_id(track_id)
    if not track:
        abort(404)
        
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        kind = request.form.get('kind')
        
        if dashboard_service.update_track(track_id, title, url, kind):
            flash('Titre mis à jour.', 'success')
            return redirect(url_for('admin.titres'))
        else:
            flash('Erreur lors de la modification.', 'danger')
            
    return render_template('track_edit.html', track=track)

@admin_bp.route('/urgent')
@login_required
def tableau_bord_urgence():
    data = dashboard_service.get_urgent_data()
    return render_template('urgent.html', **data)

@admin_bp.route('/urgent/broadcast', methods=['POST'])
@login_required
def diffuser_urgence():
    media_id = request.form.get('message')
    if media_id:
        dashboard_service.trigger_urgent_broadcast(media_id)
        flash('ALERTE URGENTE DÉCLENCHÉE', 'danger')
    else:
        flash('Erreur : Aucun message sélectionné.', 'danger')
    return redirect(url_for('admin.tableau_bord_urgence'))

@admin_bp.route('/check-health')
@login_required
def verifier_sante():
    return redirect(url_for('admin.tableau_de_bord'))
