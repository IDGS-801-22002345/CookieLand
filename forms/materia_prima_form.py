from wtforms import Form #type:ignore
from flask_wtf import FlaskForm#type:ignore
 
from wtforms import StringField,IntegerField, SelectField
from wtforms import EmailField
from wtforms import validators
from wtforms import Form, IntegerField, StringField, EmailField, validators
 
class MateriaPrimaForm(FlaskForm):
    id = IntegerField('id', [
        validators.number_range(min=1, max=20, message='Valor no válido')
    ])
    nombre = StringField('Nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=4, max=50, message='Requiere min=4, max=50 caracteres')
    ])
    
    unidad = SelectField('Unidad de medida', choices=[
        ('gr', 'Gramos'),
        ('ml', 'Mililitros'),
        ('pz', 'Piezas')
    ], validators=[validators.DataRequired(message='La unidad de medida es requerida')])