from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import Proveedores, MateriaPrima, Compra, InventarioMateria, db
from forms.compra_forms import FormCompra
import datetime
from utils.decoradores import *

registro_compras_bp = Blueprint('registro_compras_bp', __name__, url_prefix='/')

def convertir_a_unidad_base(cantidad, unidad_medida):
    conversiones = {
        'kg': 1000,   # 1 kilo = 1000 gramos
        'gr': 1,     # 1 gramo = 1 gramo
        'lt': 1000,  # 1 litro = 1000 mililitros
        'ml': 1, # 1 mililitro = 1 mililitro
        'pz': 1,      # 1 pieza = 1 pieza
    }

    # Si la unidad no está en el diccionario de conversiones, lanzamos un error
    if unidad_medida not in conversiones:
        raise ValueError(f"Unidad de medida '{unidad_medida}' no válida.")
    
    # Convertimos la cantidad a la unidad base
    return cantidad * conversiones[unidad_medida]

@registro_compras_bp.route('/registro-compras', methods=['GET', 'POST'])
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
@registrar_accion('Registro de compra')
def compras():
    form = FormCompra()

    # Cargar proveedores y productos desde la base de datos
    proveedores = Proveedores.query.all()
    productos = MateriaPrima.query.all()
    form.producto.choices = [(str(prod.id), prod.nombre) for prod in productos]

    # Inicializar carrito si no existe
    if 'carrito' not in session:
        session['carrito'] = []
        session['proveedor_id'] = None

    # Configurar las opciones del proveedor
    if session['carrito']:
        # Si hay items en el carrito, usar el proveedor almacenado
        proveedor_id = session.get('proveedor_id')
        
        if proveedor_id is not None:
            proveedor = Proveedores.query.get(proveedor_id)
            if proveedor:
                # Configurar el select con solo el proveedor actual
                form.proveedor.choices = [(str(proveedor.id), proveedor.nombre)]
                form.proveedor.data = str(proveedor.id)
            else:
                # Si el proveedor no existe, limpiar el carrito
                session['carrito'] = []
                session['proveedor_id'] = None
                flash("El proveedor seleccionado ya no existe", "warning")
                return redirect(url_for('registro_compras_bp.compras'))
        else:
            # Proveedor es "Otro"
            form.proveedor.choices = [("otro", "Otro")]
            form.proveedor.data = "otro"
    else:
        # Si no hay items, permitir seleccionar cualquier proveedor
        form.proveedor.choices = [(str(prov.id), prov.nombre) for prov in proveedores] + [("otro", "Otro")]

    # Resto del código de manejo del formulario...
    if form.validate_on_submit():
        proveedor_id = form.proveedor.data
        
        # Manejar el proveedor "Otro"
        if proveedor_id == "otro":
            proveedor_nombre = "Otro"
            session['proveedor_id'] = None
        else:
            proveedor = Proveedores.query.get(proveedor_id)
            if not proveedor:
                flash("Proveedor no válido", "danger")
                return redirect(url_for('registro_compras_bp.compras'))
            
            proveedor_nombre = proveedor.nombre
            session['proveedor_id'] = int(proveedor_id)

        # Resto del código para agregar al carrito...
        producto_id = form.producto.data
        cantidad = float(form.cantidad.data or 0)
        unidad_medida = form.unidad_medida.data
        precio_unitario = float(form.precio_unitario.data or 0)
        total = precio_unitario

        if total <= 0:
            flash("El precio o la cantidad no son válidos", "danger")
            return redirect(url_for('registro_compras_bp.compras'))

        # Asegurarnos de que 'carrito' es una lista
        if not isinstance(session['carrito'], list):
            session['carrito'] = []

        item = {
            'materia_prima_id': producto_id,
            'nombre': MateriaPrima.query.get(producto_id).nombre,
            'proveedor': proveedor_nombre,
            'proveedor_id': session['proveedor_id'],
            'cantidad': cantidad,
            'unidad_medida': unidad_medida,
            'precio_unitario': precio_unitario,
            'total': total
        }
        
        session['carrito'].append(item)  # Ahora sí es una lista
        session.modified = True
        flash('Producto agregado al carrito', 'success')
        return redirect(url_for('registro_compras_bp.compras'))

    compras = session.get('carrito', [])
    total_general = sum(item.get('total', 0) for item in compras)

    return render_template('compras/registro_compras.html', 
                         form=form, 
                         compras=compras, 
                         total_general=total_general,
                         proveedor_fijo=bool(session.get('carrito')))

@registro_compras_bp.route('/get_unidad_base/<int:insumo_id>')
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
def get_unidad_base(insumo_id):
    insumo = MateriaPrima.query.get_or_404(insumo_id)
    
    # Normaliza la unidad a minúsculas y sin espacios
    unidad = insumo.unidad.strip().lower()
    
    # Mapeo de unidades alternativas
    unidad_map = {
        'gramos': 'gr',
        'gramo': 'gr',
        'g': 'gr',
        'mililitros': 'ml',
        'mililitro': 'ml',
        'litros': 'lt',
        'litro': 'lt',
        'piezas': 'pz',
        'pieza': 'pz'
    }
    
    # Si la unidad está en el mapeo, usa el valor correspondiente
    unidad_base = unidad_map.get(unidad, unidad)
    
    # Asegúrate que solo devuelve 'gr', 'ml' o 'pz'
    if unidad_base not in ['gr', 'ml', 'pz']:
        unidad_base = 'gr'  # Valor por defecto si no coincide
    
    return {
        'unidad_base': unidad_base
    }

@registro_compras_bp.route('/eliminar-producto', methods=['POST'])
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
@registrar_accion('Eliminar producto')
def eliminar_producto():
    producto_index = int(request.form['producto_index'])  

    if 'carrito' in session and 0 <= producto_index < len(session['carrito']):
        session['carrito'].pop(producto_index)
        session.modified = True
        
        # Si el carrito quedó vacío, limpiar el proveedor
        if not session['carrito']:
            session.pop('proveedor_id', None)
            
        flash('Producto eliminado del carrito', 'success')
    
    return redirect(url_for('registro_compras_bp.compras'))

@registro_compras_bp.route('/finalizar-compra', methods=['POST'])
@login_required
@log_excepciones
@role_required('admin', 'produccion', 'vendedor')
@registrar_accion('Finalizo compra')
def finalizar_compra():
    if 'carrito' not in session or not session['carrito']:
        flash("No hay productos en el carrito", "warning")
        return redirect(url_for('registro_compras_bp.compras'))

    # Usar el proveedor_id almacenado en la sesión
    proveedor_id = session.get('proveedor_id')
    total_general = sum(item.get('total', 0) for item in session['carrito'])

    nueva_compra = Compra(
        total=total_general,
        proveedor_id=proveedor_id,
        materias_primas=session['carrito']
    )
    db.session.add(nueva_compra)
    db.session.commit()

    # Actualizar inventario
    for item in session['carrito']:
        materia_prima = MateriaPrima.query.get(item['materia_prima_id'])
        if materia_prima:
            cantidad_convertida = convertir_a_unidad_base(item['cantidad'], item['unidad_medida'])
            inventario = InventarioMateria.query.filter_by(material_id=materia_prima.id).first()
            if inventario:
                inventario.cantidad += cantidad_convertida
            else:
                inventario = InventarioMateria(
                    material_id=materia_prima.id,
                    cantidad=cantidad_convertida,
                    estado_stock="Disponible"
                )
                db.session.add(inventario)
            db.session.commit()

    # Limpiar carrito y proveedor
    session.pop('carrito', None)
    session.pop('proveedor_id', None)
    flash("Compra finalizada con éxito", "success")
    
    return redirect(url_for('registro_compras_bp.compras'))

