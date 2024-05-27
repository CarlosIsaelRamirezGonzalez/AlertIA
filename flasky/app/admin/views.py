from flask import render_template, flash, url_for, redirect, jsonify
from flask_login import login_required
from ..decorators import admin_required, post_only
from . import admin
from ..models import Camera, Report


@admin.route('/cameras')
@login_required
@admin_required
def cameras_panel():
    cameras = Camera.objects.all()
    return render_template('admin/cameras-panel.html', cameras = cameras)

@admin.route('/reports')
@login_required
@admin_required
def reports_panel():
    reports = Report.objects.all()
    return render_template('admin/reports-panel.html', reports = reports)


# Is this necessary?
@admin.route('/delete/<id_camera>')
@login_required
@admin_required
@post_only
def delete_camera_admin(id_camera):
    try:
        camera = Camera.query.filter_by(id=id_camera).first()
        if not camera:
            return jsonify({'error': 'Camera not found.'}), 404
        camera.delete()
        return jsonify({'message': 'Camera deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred while deleting the camera.', 'details': str(e)}), 500
