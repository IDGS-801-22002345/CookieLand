from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, EmailField
from wtforms.validators import DataRequired, Length, Email, Regexp, NumberRange

class ProveedorForm(FlaskForm):
    id = IntegerField('id')  # No necesita validación si es autoincremental
    nombre = StringField('Nombre', validators=[
        DataRequired('El nombre es requerido'),
        Length(min=4, max=50, message='El nombre debe tener entre 4 y 50 caracteres')
    ])
    telefono = StringField('Teléfono', validators=[
        DataRequired('El teléfono es requerido'),
        Length(min=10, max=15, message='El teléfono debe tener entre 10 y 15 dígitos'),
        Regexp(r'^\d+$', message='Solo se permiten números')
    ])
    email = EmailField('Email', validators=[
        DataRequired('El email es requerido'),
        Email('Ingrese un email válido'),
        Length(max=50, message='El email no debe exceder 50 caracteres')
    ])
    estatus = IntegerField('Estatus', validators=[
        NumberRange(min=0, max=1, message='El estatus debe ser 0 o 1')
    ])