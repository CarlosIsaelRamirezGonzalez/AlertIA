from flask import render_template, flash, url_for, redirect, jsonify
from flask_login import login_required
from ..decorators import admin_required, post_only
from . import admin
from ..models import Camera, Report
import base64


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


@admin.route('/reports/<report_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def report_panel(report_id):
    report = Report.objects(id=report_id).first()
    image_base64 = base64.b64encode(report.image).decode('utf-8')
    report.image = image_base64
    return render_template('admin/report-panel.html', report = report)


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
