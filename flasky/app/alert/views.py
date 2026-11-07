"""Vistas de notificaciones: lista, detalle, búsqueda, destacadas y borrado."""

from flask import render_template, request, redirect, url_for, flash, abort
from . import alert
from ..models import Notification
from ..decorators import csrf_post
import base64
from mongoengine import Q
from flask_login import current_user, login_required

PER_PAGE = 25
MAX_STARRED = 100
MAX_UNSTARRED = 500


def get_own_notification(notification_id):
    """Busca una notificación del usuario de la sesión.

    Args:
        notification_id: Identificador de la notificación.

    Returns:
        La notificación.

    Raises:
        NotFound: Si no existe o es de otra persona (responde 404).
    """
    notification = Notification.objects(id=notification_id, user=current_user.email).first()
    if not notification:
        abort(404)
    return notification


@alert.route('/notifications')
@login_required
def notifications():
    """Muestra las notificaciones del usuario, de la más nueva a la más vieja.

    Returns:
        La página.
    """
    page = request.args.get('page', 1, type=int)
    pagination = Notification.objects(user=current_user.email).order_by('-date_time').paginate(page=page, per_page=PER_PAGE)
    return render_template('alert/notifications.html', load_notifications=pagination.items, pagination=pagination)


@alert.route('/notifications/delete/<notification_id>', methods=['POST'])
@login_required
@csrf_post
def delete_notification(notification_id):
    """Borra una notificación del usuario.

    Args:
        notification_id: Identificador de la notificación.

    Returns:
        Una redirección a la lista.
    """
    get_own_notification(notification_id).delete()
    flash('Notificación eliminada correctamente', 'success')
    return redirect(url_for('alert.notifications'))


@alert.route('/notifications/search_notifications', methods=['GET', 'POST'])
@login_required
def search():
    """Busca entre las notificaciones del usuario por lugar, amenaza, cámara o certeza.

    Returns:
        La lista filtrada, o una redirección a la lista completa si no se buscó nada.
    """
    filter_value = request.form.get('search', '')
    if filter_value == '':
        return redirect(url_for('alert.notifications'))

    page = request.args.get('page', 1, type=int)
    pagination = Notification.objects.filter(Q(place__icontains=filter_value) |
                                             Q(threat__icontains=filter_value) |
                                             Q(camera_name__icontains=filter_value) |
                                             Q(certainty__icontains=filter_value),
                                             user=current_user.email).paginate(page=page, per_page=PER_PAGE)
    return render_template('alert/notifications.html', load_notifications=pagination.items, pagination=pagination)


@alert.route('/notifications/view/<notification_id>')
@login_required
def view_notification(notification_id):
    """Muestra una notificación con su foto y la marca como leída.

    Args:
        notification_id: Identificador de la notificación.

    Returns:
        La página.
    """
    load_notification = get_own_notification(notification_id)
    if not load_notification.read:
        load_notification.update(set__read=True)
    # La plantilla muestra la foto incrustada en base64.
    load_notification.image = base64.b64encode(load_notification.image).decode('utf-8')
    return render_template('alert/details.html', load_notification=load_notification)


@alert.route('/filterStarred')
@login_required
def filter_starred():
    """Muestra solo las notificaciones destacadas.

    Returns:
        La página.
    """
    page = request.args.get('page', 1, type=int)
    pagination = Notification.objects(user=current_user.email, starred=True).paginate(page=page, per_page=PER_PAGE)
    return render_template('alert/notifications.html', load_notifications=pagination.items, pagination=pagination)


@alert.route('/deleteAllNotifications', methods=['POST'])
@login_required
@csrf_post
def delete_all_notifications():
    """Borra las notificaciones del usuario que no están destacadas.

    Returns:
        Una redirección a la lista.
    """
    Notification.objects(user=current_user.email, starred=False).delete()
    flash('Notificaciones eliminadas correctamente', 'success')
    return redirect(url_for('alert.notifications'))


@alert.route('/add-QuitStarred/<notification_id>')
@login_required
def add_quit_starred(notification_id):
    """Destaca una notificación o le quita lo destacado.

    Args:
        notification_id: Identificador de la notificación.

    Returns:
        Una redirección a la lista.
    """
    load_notification = get_own_notification(notification_id)

    if not load_notification.starred:
        # El límite es por usuario, y ahora sí impide destacar más.
        if Notification.objects(user=current_user.email, starred=True).count() >= MAX_STARRED:
            flash("Starred limit reached")
        else:
            load_notification.update(set__starred=True)
            flash("Alerta añadida a destacadas")
    else:
        load_notification.update(set__starred=False)
        unstarred = Notification.objects(user=current_user.email, starred=False)
        if unstarred.count() > MAX_UNSTARRED:
            unstarred.order_by('date_time').first().delete()
        flash("Alerta eliminada de destacadas")

    return redirect(url_for('alert.notifications'))
