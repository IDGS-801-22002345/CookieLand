from datetime import datetime
from .db import db

detalle_recetas = db.Table(
    'DetalleRecetas',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('recetaId', db.Integer, db.ForeignKey('Recetas.id'), nullable=False),
    db.Column('insumoId', db.Integer, db.ForeignKey('materia_prima.id'), nullable=False),
    db.Column('cantidad', db.Integer, nullable=False)
)

class Receta(db.Model):
    __tablename__ = 'Recetas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)

    insumos = db.relationship(
        'MateriaPrima',  
        secondary=detalle_recetas,  
        back_populates='recetas'  
    )

    galletas = db.relationship('Galleta', back_populates='receta')

    def __repr__(self):
        return f"<Receta(id={self.id}, nombre='{self.nombre}')>"

class Galleta(db.Model):
    __tablename__ = 'Galleta'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    recetasId = db.Column(db.Integer, db.ForeignKey('Recetas.id'), nullable=False)

    receta = db.relationship('Receta', back_populates='galletas')

    def __repr__(self):
        return f"<Galleta(id={self.id}, nombre='{self.nombre}', recetasId={self.recetasId})>"