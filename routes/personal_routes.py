from flask import Blueprint, render_template

personal_bp = Blueprint('personal_bp', __name__, url_prefix='/')

@personal_bp.route('/ventas')
def ventas():
    return render_template('personal/ventas.html')