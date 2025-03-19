from flask import Blueprint, render_template, request, redirect, url_for

recetas_bp = Blueprint('recetas_bp', __name__, url_prefix='/recetas')

@recetas_bp.route('/recetas')
def mostrar_recetas():
    return render_template('galletas/recetas.html')

@recetas_bp.route('/galletas')
def mostrar_galletas():
    return render_template('galletas/galletas.html')
