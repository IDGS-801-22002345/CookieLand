from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError

class FormCompra(FlaskForm):
    proveedor = SelectField('Proveedor', choices=[], validators=[DataRequired(message="El producto es obligatorio.")])
    producto = SelectField('Producto', choices=[], validators=[DataRequired(message="El producto es obligatorio.")])
    cantidad = DecimalField('Cantidad', validators=[DataRequired(message="La cantidad es obligatoria."), NumberRange(min=0, message="La cantidad debe ser mayor o igual a 0.")], places=2)
    unidad_medida = SelectField('Unidad de Medida', 
                                choices=[('gramos', 'Gramos'), 
                                         ('kilos', 'Kilos'), 
                                         ('mililitros', 'Mililitros'), 
                                         ('litros', 'Litros'), 
                                         ('pieza', 'Pieza')],
                                validators=[DataRequired(message="La unidad de medida es obligatoria.")])

    precio_unitario = DecimalField('Precio Unitario', validators=[DataRequired(message="El precio es obligatorio."), NumberRange(min=0, message="El precio debe ser mayor o igual a 0.")], places=2)
