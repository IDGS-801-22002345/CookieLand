from datetime import datetime
from app import db

# Tabla para Material
class Materia(db.Model):
    __tablename__ = 'material'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    unidad = db.Column(db.String(255), nullable=False)
    
    inventarios = db.relationship('InventarioMateria', backref='material', lazy=True)
    
    def __repr__(self):
        return f'<Material {self.nombre}>'

# Tabla para InventarioMateria
class InventarioMateria(db.Model):
    __tablename__ = 'inventario_materia'
    
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    cantidad_minima = db.Column(db.Integer, nullable=False)
    estado_stock = db.Column(db.Boolean, default=True)  # 1: disponible, 0: no disponible
    fecha_caducidad = db.Column(db.Date)
    porcentaje_merma = db.Column(db.Numeric(5, 2), default=0.0)
    
    materia_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    
    def __repr__(self):
        return f'<InventarioMateria {self.material.nombre} - {self.cantidad}>'
