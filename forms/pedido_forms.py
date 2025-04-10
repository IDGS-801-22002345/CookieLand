from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired

from models.models import Pedido, Usuario

class PedidoListoForm(FlaskForm):
    pedido = SelectField('Seleccionar Pedido', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(PedidoListoForm, self).__init__(*args, **kwargs)
        self.pedido.choices = self.obtener_pedidos_listos()
    
    def obtener_pedidos_listos(self):
        pedidos = Pedido.query.filter_by(estatus='Listo para recoger')\
                             .join(Usuario)\
                             .with_entities(
                                 Pedido.id,
                                 Usuario.nombre
                             )\
                             .all()
        
        return [(p.id, f"Pedido #{p.id} - {p.nombre}") for p in pedidos]