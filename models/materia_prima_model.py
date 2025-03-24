# models/materia_prima_model.py
from flask_sqlalchemy import SQLAlchemy
import datetime
from .db import db
from .receta_model import detalle_recetas  # Importa la tabla de asociación

class MateriaPrima(db.Model):  
    __tablename__ = 'materia_prima' 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    unidad = db.Column(db.String(50), nullable=False)
    estatus = db.Column(db.Integer, default=1)  # Estatus (0 o 1, por defecto 1)
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())
    update_date = db.Column(db.DateTime, default=datetime.datetime.now, server_default=db.func.now())
    
    # Relación con InventarioMateria
    inventario = db.relationship('InventarioMateria', back_populates='materia_prima', uselist=False)

    # Relación many-to-many con Receta
    recetas = db.relationship(
        'Receta',  # Nombre del modelo de Receta
        secondary=detalle_recetas,  # Tabla de asociación
        back_populates='insumos'  # Nombre de la relación en el modelo de Receta
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