from wtforms import Form  
from flask_wtf import FlaskForm  
from wtforms import StringField, IntegerField, SelectField, FieldList, FormField
from wtforms import validators

class InsumoForm(Form):
    insumo = SelectField('Insumo', coerce=int, validators=[
        validators.DataRequired(message='El insumo es requerido')
    ])
    cantidad = IntegerField('Cantidad', [
        validators.DataRequired(message='La cantidad es requerida'),
        validators.number_range(min=1, message='La cantidad debe ser mayor a 0')
    ])

class RecetaForm(FlaskForm):
    nombre = StringField('Nombre de la Receta', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=4, max=50, message='Requiere min=4, max=50 caracteres')
    ])
    insumos = FieldList(FormField(InsumoForm), min_entries=1)