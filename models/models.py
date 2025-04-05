from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import pytz
from werkzeug.security import generate_password_hash
import datetime
from sqlalchemy.dialects.mysql import JSON


db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)


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
    

class IntentosFallidos(db.Model):
    __tablename__ = 'intentos_fallidos'

    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    intentos = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    ultimo_intento = db.Column(db.DateTime, default=datetime.datetime.now(pytz.timezone("America/Mexico_City")))

    def incrementar_intento(self):
        self.intentos += 1
        self.ultimo_intento = datetime.datetime.now(pytz.timezone("America/Mexico_City"))

        if self.intentos >= 3:
            # Bloqueo de 10 minutos
            self.bloqueado_hasta = datetime.datetime.now(pytz.timezone("America/Mexico_City")) + datetime.timedelta(minutes=10)
        
        db.session.commit()

    def resetear_intentos(self):
        self.intentos = 0
        self.bloqueado_hasta = None
        db.session.commit()

    @property
    def esta_bloqueado(self):
        # Asegurarse de que ambas fechas tengan la misma zona horaria (timezone-aware)
        if self.bloqueado_hasta:
            # Convertir la fecha de bloqueo a zona horaria local para compararla con la hora actual local
            bloqueado_hasta_local = self.bloqueado_hasta.astimezone(pytz.timezone("America/Mexico_City"))
            ahora = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
            return bloqueado_hasta_local > ahora
        return False


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

import datetime
from sqlalchemy.dialects.postgresql import JSON
from models.models import db

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
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'))
    foto = db.Column(db.LargeBinary(length=16777215), nullable=False)  
    
    receta = db.relationship('Receta', back_populates='galletas')
    producciones = db.relationship('Produccion', back_populates='galleta')


class Produccion(db.Model):
    __tablename__ = 'produccion'
    id = db.Column(db.Integer, primary_key=True)
    galleta_id = db.Column(db.Integer, db.ForeignKey('galletas.id'), nullable=False)  
    stock = db.Column(db.Integer, nullable=False, default=0)
    estadoStock = db.Column(db.String(50), nullable=False)
    estadoProduccion = db.Column(db.String(50), nullable=False)
    
    galleta = db.relationship('Galleta', back_populates='producciones')
    mermas = db.relationship('Merma', back_populates='produccion')


class Merma(db.Model):
    __tablename__ = 'Merma'  
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column('fecha', db.DateTime, default=datetime.datetime.now, server_default=db.func.now())  
    tipo_merma = db.Column(db.String(50), nullable=True)
    
    inventario_materia_id = db.Column('inventarioMateriaId', db.Integer, 
                                    db.ForeignKey('inventario_materia.id'), nullable=True)
    produccion_id = db.Column(db.Integer, db.ForeignKey('produccion.id'), nullable=True)  

    inventario_materia = db.relationship('InventarioMateria', back_populates='mermas')
    produccion = db.relationship('Produccion', back_populates='mermas')
    
    
class Auditoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    accion = db.Column(db.String(255), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.datetime.now)
    
    def __repr__(self):
        return f'<Auditoria {self.id} - {self.accion}>'
