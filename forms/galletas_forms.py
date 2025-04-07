from wtforms import StringField,FileField, SelectField, IntegerField, FloatField
from flask_wtf.file import FileAllowed, FileRequired, FileSize
from wtforms import validators
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional, NumberRange


class GalletasForm(FlaskForm):
    nombre = StringField('Nombre de la galleta ', [
        validators.DataRequired(message='El nombre de la galleta es requerido'),
        validators.Length(min=4, max=50, message='Requiere min=4, max=50 caracteres')
    ])
    precio = FloatField('Precio de la galleta', [
        DataRequired(message='El precio es requerido'),
        validators.NumberRange(min=0.01, message='El precio debe ser mayor a 0')
    ])
    foto = FileField('Foto', validators=[
        FileRequired(message='La foto es requerida'),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Solo imágenes JPG, JPEG o PNG'),
        FileSize(max_size=5*1024*1024, message='Máximo 5MB permitido')
    ])
    
class GalletasEditForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    precio = FloatField('Precio de la galleta', validators=[
        Optional(),  
        NumberRange(min=0.01, message='El precio debe ser mayor a 0')
    ])
    foto = FileField('Nueva imagen de galleta', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Solo se permiten imágenes (JPG, PNG)')
    ])


class InsumosForm(FlaskForm):
      insumo = SelectField(
        'Material:',
        validators=[DataRequired(message='El material es requerido')],
        choices=[], 
        validate_choice=False  
    )
      cantidad = IntegerField('Cantidad: ', [
        DataRequired(message='La cantidad es requerida'),
        validators.NumberRange(min=1, message='La cantidad debe ser mayor a 0')
    ])

      def __init__(self, *args, **kwargs):
        super(InsumosForm, self).__init__(*args, **kwargs)
        self._cargar_insumos()

      def _cargar_insumos(self):
        from models.models import MateriaPrima
        self.insumo.choices = [(i.id, f"{i.nombre} ({i.unidad})") for i in MateriaPrima.query.all()]