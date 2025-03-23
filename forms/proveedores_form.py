from wtforms import Form #type:ignore
from flask_wtf import FlaskForm#type:ignore
 
from wtforms import StringField,IntegerField#type:ignore
from wtforms import EmailField#type:ignore
from wtforms import validators#type:ignore
from wtforms import Form, IntegerField, StringField, EmailField, validators
 
class ProveedorForm(Form):  
    id = IntegerField('id', [
        validators.number_range(min=1, max=20, message='Valor no válido')
    ])
    nombre = StringField('nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.length(min=4, max=50, message='Requiere min=4, max=50')
    ])
    telefono = StringField('teléfono', [
        validators.DataRequired(message='El teléfono es requerido'),
        validators.length(min=10, max=15, message='Requiere min=10, max=15')
    ])
    email = EmailField('correo', [
        validators.DataRequired(message='El correo es requerido'),
        validators.Email(message='Ingrese un correo válido')
    ])
    estatus = IntegerField('estatus', [
        validators.DataRequired(message='El estatus es requerido'),
        validators.number_range(min=0, max=1, message='El estatus debe ser 0 o 1')
    ])