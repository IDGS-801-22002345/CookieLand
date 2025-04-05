from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # type: ignore
from werkzeug.security import generate_password_hash
import datetime
from sqlalchemy.dialects.mysql import JSON

db = SQLAlchemy()

# Tabla de Roles
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)


# Tabla de Usuarios
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(10), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasenia = db.Column(db.String(255), nullable=False)
    estatus = db.Column(db.Integer, default=1)
    verificado = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    last_login = db.Column(db.DateTime) 


    rol = db.relationship('Role', backref=db.backref('usuarios', lazy=True), lazy='joined')

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

    def has_role(self, role_name):
        return self.rol and self.rol.role_name.lower() == role_name.lower()

# Tabla para verificar las cuentas de clientes
class CodigoVerificacion(db.Model):
    __tablename__ = 'codigos_verificacion'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(6), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    expiracion = db.Column(db.DateTime, nullable=False)
    verificado = db.Column(db.Boolean, default=False)
    usuario = db.relationship('Usuario', backref='codigo_verificacion')
    
    
class MateriaPrima(db.Model):  
    __tablename__ = 'materia_prima' 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    unidad = db.Column(db.String(50), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.datetime.now)
    
    inventario = db.relationship('InventarioMateria', back_populates='materia_prima', uselist=False)
    detalles_receta = db.relationship('DetalleReceta', back_populates='insumo')

class InventarioMateria(db.Model):  
    __tablename__ = 'inventario_materia' 
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    cantidad_minima = db.Column(db.Integer, nullable=False)
    estado_stock = db.Column(db.String(50), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materia_prima.id'), unique=True, nullable=False)
    
    materia_prima = db.relationship('MateriaPrima', back_populates='inventario')

    create_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())
    update_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())

    mermas = db.relationship('Merma', back_populates='inventario_materia')


class Proveedores(db.Model):  
    __tablename__ = 'proveedores'  
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    telefono = db.Column(db.String(15))  
    email = db.Column(db.String(100))
    estatus = db.Column(db.Integer, default=1) 
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())


class Compra(db.Model):
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    # Lista de materias primas en formato JSON
    materias_primas = db.Column(JSON, nullable=False, default=[])  

class Receta(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    estatus = db.Column(db.Integer, default=1)
    
    detalles = db.relationship('DetalleReceta', back_populates='receta')
    galletas = db.relationship('Galleta', back_populates='receta')

class DetalleReceta(db.Model):
    __tablename__ = 'detalle_recetas'
    
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), primary_key=True)
    insumo_id = db.Column(db.Integer, db.ForeignKey('materia_prima.id'), primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    
    receta = db.relationship('Receta', back_populates='detalles')
    insumo = db.relationship('MateriaPrima', back_populates='detalles_receta')

class Galleta(db.Model):
    __tablename__ = 'galletas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    foto = db.Column(db.LargeBinary(length=16777215), nullable=False)  
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'))
    stock = db.Column(db.Integer, nullable=False, default=0)
    receta = db.relationship('Receta', back_populates='galletas')
    estadoStock = db.Column(db.String(50), nullable=False)
    producciones = db.relationship('Produccion', back_populates='galleta') 
    mermas = db.relationship('Merma', back_populates='galleta') 


class Produccion(db.Model):
    __tablename__ = 'produccion'
    id = db.Column(db.Integer, primary_key=True)
    galleta_id = db.Column(db.Integer, db.ForeignKey('galletas.id'), nullable=False)  
    estadoProduccion = db.Column(db.String(50), nullable=False)
    fechaDeProduccion = db.Column(db.DateTime, default=datetime.datetime.now,)
    fechaFinalizacion = db.Column(db.DateTime, nullable=True)
    galleta = db.relationship('Galleta', back_populates='producciones')

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import Merma, db, InventarioMateria, Galleta, MateriaPrima
from forms.merma_forms import MermaForm
import traceback 
import datetime

merma_bp = Blueprint('merma_bp', __name__, url_prefix='/mk_merma')

@merma_bp.route("/")
def index():
    create_form = MermaForm(request.form)

    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]

    galletas = Galleta.query.all()
    create_form.galleta_id.choices = [(g.id, g.nombre) for g in galletas]

    mermas = Merma.query.all()

    return render_template("merma/merma.html", form=create_form, mermas=mermas)


@merma_bp.route("/crear", methods=['POST'])
def crear():
    create_form = MermaForm(request.form)

    materias = db.session.query(InventarioMateria.id, MateriaPrima.nombre).join(MateriaPrima).all()
    create_form.inventario_materia_id.choices = [(m.id, m.nombre) for m in materias]

    galletas = Galleta.query.all()
    create_form.galleta_id.choices = [(g.id, g.nombre) for g in galletas]

    if create_form.validate():
        tipo_merma = create_form.tipo_merma.data
        cantidad = create_form.cantidad.data
        inventario_materia_id = create_form.inventario_materia_id.data if tipo_merma == 'insumo' else None
        galleta_id = create_form.galleta_id.data if tipo_merma == 'galleta' else None

        inventario_item = None
        item_nombre = None

        if galleta_id:
            galleta = Galleta.query.get(galleta_id)
            if not galleta:
                flash('Error: Galleta no encontrada.', 'warning')
                return redirect(url_for('merma_bp.index'))
            inventario_item = galleta
            item_nombre = galleta.nombre

        if inventario_materia_id:
            inventario_materia = InventarioMateria.query.get(inventario_materia_id)
            if not inventario_materia:
                flash('Error: Inventario de insumos no encontrado.', 'warning')
                return redirect(url_for('merma_bp.index'))
            inventario_item = inventario_materia
            item_nombre = inventario_materia.materia_prima.nombre if inventario_materia.materia_prima else "Insumo desconocido"

        if inventario_item:
            cantidad_actual = inventario_item.cantidad if hasattr(inventario_item, 'cantidad') else getattr(inventario_item, 'stock', 0)

            if cantidad_actual < cantidad:
                flash(f'Error: No hay suficiente stock de {item_nombre}. Stock actual: {cantidad_actual}', 'warning')
                return redirect(url_for('merma_bp.index'))

            
            if hasattr(inventario_item, 'cantidad'):
                inventario_item.cantidad -= cantidad

                
                if inventario_item.cantidad == 0:
                    inventario_item.estado_stock = 'Agotado'
                    flash(f'¡ALERTA! El stock de {item_nombre} se ha agotado completamente.', 'warning')
                elif inventario_item.cantidad < inventario_item.cantidad_minima:
                    inventario_item.estado_stock = 'Bajo'
                    flash(f'¡Advertencia! Stock bajo de {item_nombre}. Quedan {inventario_item.cantidad} unidades.', 'warning')
                else:
                    inventario_item.estado_stock = 'Completo'  
                    flash(f'Stock actual de {item_nombre}: {inventario_item.cantidad} unidades', 'info')
            else:
                inventario_item.stock -= cantidad  

            merma = Merma(
                descripcion=create_form.descripcion.data,
                cantidad=cantidad,
                tipo_merma=tipo_merma,
                inventario_materia_id=inventario_materia_id,
                galleta_id=galleta_id
            )
            db.session.add(merma)
            db.session.commit()
            flash(f'Merma registrada correctamente', 'success')

    return redirect(url_for('merma_bp.index'))

