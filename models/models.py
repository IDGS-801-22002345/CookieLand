from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import datetime
from sqlalchemy.dialects.mysql import JSON

# Tabla de Roles
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    #Insercion de Roles
    @staticmethod
    def insertar_roles():
        roles = ['admin', 'cliente', 'vendedor', 'produccion']
        for nombre in roles:
            if not Role.query.filter_by(role_name=nombre).first():
                nuevo_rol = Role(role_name=nombre)
                db.session.add(nuevo_rol)
        db.session.commit()

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

    # Insercion de Usuario admin predeterminado
    @staticmethod
    def insertar_admin():
        if not Usuario.query.filter_by(correo='admin@gmail.com').first():
            rol_admin = Role.query.filter_by(role_name='admin').first()
            if rol_admin:
                admin = Usuario(
                    nombre='Admin Predeterminado',
                    username='admin',
                    correo='admin@gmail.com',
                    telefono='1234567890',
                    contrasenia=generate_password_hash('maicookies123'),
                    estatus=1,
                    verificado=True,
                    rol_id=rol_admin.id
                )
                db.session.add(admin)
                db.session.commit()

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


class Proveedores(db.Model):  # Cambiamos de Alumnos a Proveedores
    __tablename__ = 'proveedores'  # Cambiamos el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    telefono = db.Column(db.String(15))  # Nuevo campo para el teléfono
    email = db.Column(db.String(100))
    estatus = db.Column(db.Integer, default=1)  # Estatus (0 o 1, por defecto 1)
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
    producciones = db.relationship('Produccion', back_populates='galleta', cascade="all, delete-orphan")  

class Produccion(db.Model):
    __tablename__ = 'produccion'
    id = db.Column(db.Integer, primary_key=True)
    galleta_id = db.Column(db.Integer, db.ForeignKey('galletas.id'), nullable=False)  
    stock = db.Column(db.Integer, nullable=False, default=0)
    estadoStock = db.Column(db.String(50), nullable=False)
    estadoProduccion = db.Column(db.String(50), nullable=False)
    
    galleta = db.relationship('Galleta', back_populates='producciones')
