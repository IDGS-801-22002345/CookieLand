from wtforms import  IntegerField, validators, HiddenField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

  
class ProduccionForm(FlaskForm):
    id = HiddenField('ID')
    cantidad = IntegerField('Cantidad: ', [
        DataRequired(message='La cantidad es requerida'),
        validators.NumberRange(min=1, message='La cantidad debe ser mayor a 0')
    ], default=1)  