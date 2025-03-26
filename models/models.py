# models/materia_prima_model.py
from flask_sqlalchemy import SQLAlchemy
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

class Usuario(db.Model):
    __tablename__ = 'usuarios' 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(10), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasenia = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    rol = db.relationship('Role', backref=db.backref('usuarios', lazy=True))

    def _repr_(self):
        return f'<Usuario{self.nombre}>'
    
class MateriaPrima(db.Model):  
    __tablename__ = 'materia_prima' 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    unidad = db.Column(db.String(50), nullable=False)
    estatus = db.Column(db.Integer, default=1)  # Estatus (0 o 1, por defecto 1)
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


class Proveedores(db.Model):  # Cambiamos de Alumnos a Proveedores
    __tablename__ = 'proveedores'  # Cambiamos el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    telefono = db.Column(db.String(15))  # Nuevo campo para el teléfono
    email = db.Column(db.String(100))
    estatus = db.Column(db.Integer, default=1)  # Estatus (0 o 1, por defecto 1)
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
    
    receta = db.relationship('Receta', back_populates='galletas')
