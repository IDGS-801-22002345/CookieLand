# models/materia_prima_model.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # type: ignore
import datetime

db=SQLAlchemy()

detalle_recetas = db.Table(
    'DetalleRecetas',
    db.Column('recetaId', db.Integer, db.ForeignKey('recetas.id'), primary_key=True),  
    db.Column('insumoId', db.Integer, db.ForeignKey('materia_prima.id'), primary_key=True),  
    db.Column('cantidad', db.Integer, nullable=False)
)

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
    username = db.Column(db.String(50), unique=True, nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    rol = db.relationship(Role, backref=db.backref('usuarios', lazy=True), lazy='joined')

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

    def has_role(self, role_name):
        return self.rol and self.rol.role_name.lower() == role_name.lower()
    
class MateriaPrima(db.Model):  
    __tablename__ = 'materia_prima' 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    unidad = db.Column(db.String(50), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())
    update_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())
    
    inventario = db.relationship('InventarioMateria', back_populates='materia_prima', uselist=False)

    recetas = db.relationship(
        'Receta',
        secondary=detalle_recetas, 
        back_populates='insumos' 
    )

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

class Receta(db.Model):
    __tablename__ = 'recetas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    estatus =  db.Column(db.Integer, default=1)

    insumos = db.relationship(
        'MateriaPrima',
        secondary=detalle_recetas,  
        back_populates='recetas'  
    )
    
    galletas = db.relationship('Galleta', back_populates='receta')


class Galleta(db.Model):
    __tablename__ = 'galletas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    receta_id    = db.Column(db.Integer, db.ForeignKey('recetas.id'))
    foto = db.Column(db.LargeBinary, nullable=False) 
    receta = db.relationship('Receta', back_populates='galletas')

    inventario = db.relationship('InventarioGalletas', back_populates='galleta', uselist=False)


class Merma(db.Model):
    __tablename__ = 'Merma'  
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column('fecha', db.DateTime, default=datetime.datetime.now, server_default=db.func.now())  
    tipo_merma = db.Column(db.String(50), nullable=True)
    
    inventario_materia_id = db.Column('inventarioMateriaId', db.Integer, 
                                    db.ForeignKey('inventario_materia.id'), nullable=True)
    inventario_galletas_id = db.Column('inventarioGalletasId', db.Integer, 
                                     db.ForeignKey('InventarioGalletas.id'), nullable=True)

    inventario_materia = db.relationship('InventarioMateria', back_populates='mermas')
    inventario_galletas = db.relationship('InventarioGalletas', back_populates='mermas')


class InventarioGalletas(db.Model):
    __tablename__ = 'InventarioGalletas'
    
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    cantidad_minima = db.Column("cantidadMinima",db.Integer, nullable=False)
    estado_stock = db.Column("estadoStock",db.String(50), nullable=False)

    galleta_id = db.Column("galletaId",db.Integer, db.ForeignKey('galletas.id'), unique=True, nullable=False)
    galleta = db.relationship('Galleta', back_populates='inventario')
    
    mermas = db.relationship('Merma', back_populates='inventario_galletas')
