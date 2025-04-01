from wtforms import Form, StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime  

class MermaForm(Form):
    id = IntegerField('ID')
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    tipo_merma = SelectField('Tipo de Merma', 
                           choices=[('insumo', 'Insumo'), ('galleta', 'Galleta')],
                           validators=[DataRequired()])
    inventario_materia_id = SelectField('Insumo', coerce=int, choices=[])
    inventario_galletas_id = SelectField('Galleta', coerce=int, choices=[])