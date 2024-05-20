from flask import render_template, flash, url_for, redirect
from flask_login import login_required
from ..decorators import admin_required
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