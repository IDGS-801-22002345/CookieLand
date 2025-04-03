from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import Proveedores, MateriaPrima, Compra, InventarioMateria, db
from forms.compra_forms import FormCompra
import datetime

registro_compras_bp = Blueprint('registro_compras_bp', __name__, url_prefix='/')

def convertir_a_unidad_base(cantidad, unidad_medida):
    conversiones = {
        'kg': 1000,   # 1 kilo = 1000 gramos
        'g': 1,     # 1 gramo = 1 gramo
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
def compras():
    form = FormCompra()

    # Cargar proveedores y productos desde la base de datos
    proveedores = Proveedores.query.all()
    form.proveedor.choices = [(str(prov.id), prov.nombre) for prov in proveedores] + [("otro", "Otro")]
    
    productos = MateriaPrima.query.all()
    form.producto.choices = [(str(prod.id), prod.nombre) for prod in productos]

    if 'carrito' not in session:
        session['carrito'] = []

    if form.validate_on_submit():
        proveedor_id = form.proveedor.data
        proveedor_nombre = "Otro" if proveedor_id == "otro" else Proveedores.query.get(proveedor_id).nombre
        producto_id = form.producto.data
        cantidad = int(form.cantidad.data or 0)
        unidad_medida = form.unidad_medida.data
        precio_unitario = float(form.precio_unitario.data or 0)

        # Aquí ya no se convierte la cantidad a la unidad base para el total
        total = precio_unitario  # El total es solo el precio unitario del producto

        # Verificamos que el total no sea 0 para evitar agregar productos vacíos
        if total <= 0:
            flash("El precio o la cantidad no son válidos", "danger")
            return redirect(url_for('registro_compras_bp.compras'))

        item = {
            'materia_prima_id': producto_id,
            'nombre': MateriaPrima.query.get(producto_id).nombre,
            'proveedor': proveedor_nombre,
            'cantidad': cantidad,
            'unidad_medida': unidad_medida,
            'precio_unitario': precio_unitario,
            'total': total  # Guardamos el total calculado como solo el precio unitario
        }
        session['carrito'].append(item)
        session.modified = True  # Guardar cambios en sesión

        flash('Producto agregado al carrito', 'success')
        return redirect(url_for('registro_compras_bp.compras'))

    # ✅ Evitar error KeyError asegurando que 'carrito' existe
    compras = session.get('carrito', [])
    total_general = sum(item.get('total', 0) for item in compras)  # Sumamos los totales de cada item, usando get para evitar KeyError

    return render_template('compras/registro_compras.html', form=form, compras=compras, total_general=total_general)



@registro_compras_bp.route('/eliminar-producto', methods=['POST'])
def eliminar_producto():
    producto_index = int(request.form['producto_index'])  

    if 'carrito' in session and 0 <= producto_index < len(session['carrito']):
        session['carrito'].pop(producto_index)
        session.modified = True  
        flash('Producto eliminado del carrito', 'success')
    
    return redirect(url_for('registro_compras_bp.compras'))  

@registro_compras_bp.route('/finalizar-compra', methods=['POST'])
def finalizar_compra():
    if 'carrito' not in session or not session['carrito']:
        flash("No hay productos en el carrito", "warning")
        return redirect(url_for('registro_compras_bp.compras'))

    # Calcular total de la compra, utilizando .get para evitar KeyError
    total_general = sum(item.get('total', 0) for item in session['carrito'])  # Sumamos los totales de cada item

    # Obtener proveedor_id si existe en la BD
    proveedor_id = None
    for item in session['carrito']:
        if item['proveedor'] != "Otro":
            proveedor = Proveedores.query.filter_by(nombre=item['proveedor']).first()
            if proveedor:
                proveedor_id = proveedor.id
            break  # Solo tomamos el primer proveedor

    # Crear la compra con los productos en JSON
    nueva_compra = Compra(
        total=total_general,
        proveedor_id=proveedor_id,
        materias_primas=session['carrito']  # Se guarda directamente como JSON
    )
    db.session.add(nueva_compra)
    db.session.commit()

    # Actualizar el inventario
    for item in session['carrito']:
        # Asegúrate de que el producto existe en la base de datos
        materia_prima = MateriaPrima.query.get(item['materia_prima_id'])
        if materia_prima:
            # Convertimos la cantidad a la unidad base (gramos o mililitros)
            cantidad_convertida = convertir_a_unidad_base(item['cantidad'], item['unidad_medida'])

            # Verificamos si ya existe el producto en el inventario
            inventario = InventarioMateria.query.filter_by(material_id=materia_prima.id).first()
            if inventario:
                # Si ya existe, actualizamos la cantidad
                inventario.cantidad += cantidad_convertida
            else:
                # Si no existe, lo creamos
                inventario = InventarioMateria(
                    material_id=materia_prima.id,
                    cantidad=cantidad_convertida,
                    cantidad_minima=0,
                    estado_stock="Disponible"
                )
                db.session.add(inventario)

        db.session.commit()  # Guardar todos los cambios en la BD

    session.pop('carrito', None)  # Vaciar carrito
    flash("Compra finalizada con éxito", "success")
    
    return redirect(url_for('registro_compras_bp.compras'))



