from wtforms import Form, StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime  

class MermaForm(Form):
    id = IntegerField('ID')

    descripcion = TextAreaField(
        'Descripción', 
        validators=[DataRequired(message='La descripción es obligatoria')]
    )

    cantidad = IntegerField(
        'Cantidad', 
        validators=[
            DataRequired(message='La cantidad es requerida'),
            NumberRange(min=1, message='La cantidad debe ser mayor a 0')
        ]
    )

    tipo_merma = SelectField(
        'Tipo de Merma', 
        choices=[('', 'Seleccione un tipo'), ('insumo', 'Insumo'), ('galleta', 'Galleta')],
        validators=[DataRequired(message='Debe seleccionar un tipo de merma')]
    )

    inventario_materia_id = SelectField(
        'Insumo', 
        coerce=int, 
        choices=[], 
        validators=[DataRequired(message='Seleccione un insumo')]
    )

    galleta_id = SelectField(
        'Galleta', 
        coerce=int, 
        choices=[], 
        validators=[DataRequired(message='Seleccione una galleta')]
    )
