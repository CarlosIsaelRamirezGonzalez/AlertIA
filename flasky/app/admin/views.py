"""Panel del administrador: todas las cámaras y los reportes de los usuarios."""

from flask import render_template, flash, url_for, redirect, jsonify, abort
from flask_login import login_required
from ..decorators import admin_required, csrf_post
from . import admin
from ..models import Camera, Report
from ..schemas import ApiMessage
import base64


@admin.route('/cameras')
@login_required
@admin_required
def cameras_panel():
    """Muestra todas las cámaras registradas.

    Returns:
        La página.
    """
    cameras = Camera.objects.all()
    return render_template('admin/cameras-panel.html', cameras = cameras)

@admin.route('/reports')
@login_required
@admin_required
def reports_panel():
    """Muestra los reportes de notificaciones erróneas.

    Returns:
        La página.
    """
    reports = Report.objects.all()
    return render_template('admin/reports-panel.html', reports = reports)


@admin.route('/reports/<report_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def report_panel(report_id):
    """Muestra un reporte con su foto.

    Args:
        report_id: Identificador del reporte.

    Returns:
        La página.
    """
    report = Report.objects(id=report_id).first()
    if not report:
        abort(404)
    # La plantilla muestra la foto incrustada en base64.
    report.image = base64.b64encode(report.image).decode('utf-8')
    return render_template('admin/report-panel.html', report = report)


@admin.route('/delete/<id_camera>', methods=['POST'])
@login_required
@admin_required
@csrf_post
def delete_camera_admin(id_camera):
    """Borra cualquier cámara.

    Args:
        id_camera: Identificador de la cámara.

    Returns:
        Una respuesta JSON con el resultado.
    """
    try:
        camera = Camera.objects(id=id_camera).first()
        # jsonify exige un diccionario: el modelo se convierte solo en este punto.
        if not camera:
            return jsonify(ApiMessage(error='Camera not found.').model_dump(exclude_none=True)), 404
        camera.delete()
        return jsonify(ApiMessage(message='Camera deleted successfully.').model_dump(exclude_none=True)), 200
    except Exception as error:
        body = ApiMessage(error='An error occurred while deleting the camera.', details=str(error))
        return jsonify(body.model_dump(exclude_none=True)), 500
