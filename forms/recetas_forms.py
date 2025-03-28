from wtforms import Form  
from wtforms import StringField, IntegerField, SelectField, FieldList, FormField, FileField
from wtforms import validators
from wtforms import ValidationError

class InsumoForm(Form):
    insumo = SelectField(
        'Insumo', 
        coerce=int, 
        validators=[validators.DataRequired(message='El insumo es requerido')],
        choices=[]  # Inicializamos vacío pero manejaremos dinámicamente
    )
    cantidad = IntegerField('Cantidad', [
        validators.DataRequired(message='La cantidad es requerida'),
        validators.number_range(min=1, message='La cantidad debe ser mayor a 0')
    ])

# Validador personalizado para archivos requeridos
def file_required(form, field):
    if not field.data:
        raise ValidationError('El archivo es obligatorio.')

class RecetaForm(Form):
    nombre = StringField('Nombre de la Receta', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=4, max=50, message='Requiere min=4, max=50 caracteres')
    ])
    foto = FileField('Imagen de la Galleta', validators=[
        file_required  # Uso del validador personalizado
    ])


    insumos = FieldList(FormField(InsumoForm), min_entries=1)
    estatus = SelectField('Estatus', choices=[(1, 'Activo'), (0, 'Inactivo')], default=1, coerce=int)