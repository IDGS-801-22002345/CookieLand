from wtforms import SelectField, IntegerField, validators
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange


class VentaForm(FlaskForm):
    presentacion = SelectField(
        'Presentación',
        choices=[
            ('1', 'Por pieza'), 
            ('2', 'Por caja (30 pz)'),
            ('3', 'Por kilo (24 pz)'),
        ],
        validators=[
            DataRequired(message='Seleccione una presentación')
        ])
    
    cantidad = IntegerField(
        'Cantidad',
        validators=[
            DataRequired(message='Ingrese la cantidad'),
            NumberRange(
                min=1,
                message='La cantidad debe estar entre 1 y 1000'
            )
        ],default=1 )