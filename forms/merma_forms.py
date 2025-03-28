from wtforms import Form, StringField, IntegerField, TextAreaField, DateTimeField, SelectField
from datetime import datetime

class MermaForm(Form):
    id = IntegerField('ID')
    descripcion = TextAreaField('Descripción')
    cantidad = IntegerField('Cantidad')
    create_date = DateTimeField('Fecha de Creación', format='%Y-%m-%d %H:%M:%S', default=datetime.now)
    tipo_merma = SelectField('Tipo de Merma', choices=[('insumo', 'Insumo'), ('galleta', 'Galleta')])
    
    inventario_materia_id = SelectField('Insumo', choices=[], coerce=int)
    inventario_galletas_id = SelectField('Galleta', choices=[], coerce=int)
