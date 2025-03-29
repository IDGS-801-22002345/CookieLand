from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import Proveedores, MateriaPrima, DetalleCompra, Compra
from forms.compra_forms import FormCompra

registro_compras_bp = Blueprint('registro_compras_bp', __name__, url_prefix='/')

@registro_compras_bp.route('/registro-compras', methods=['GET', 'POST'])
def compras():
    form = FormCompra()

    # Cargar los proveedores desde la base de datos
    proveedores = Proveedores.query.all()
    
    # Agregar la opción "Otro" al select
    form.proveedor.choices = [(str(prov.id), prov.nombre) for prov in proveedores] + [("otro", "Otro")]
    
    productos = MateriaPrima.query.all()
    form.producto.choices = [(str(prod.id), prod.nombre) for prod in productos]

    # Si el formulario se envía y es válido
    if form.validate_on_submit():
        proveedor_id = form.proveedor.data

        # Si se seleccionó "Otro", asignamos el valor como "Otro"
        if proveedor_id == "otro":
            proveedor_nombre = "Otro"
        else:
            proveedor_nombre = Proveedores.query.get(proveedor_id).nombre

        producto_id = form.producto.data
        cantidad = form.cantidad.data
        unidad_medida = form.unidad_medida.data
        precio_unitario = form.precio_unitario.data

        # Verificar si ya existe el carrito en la sesión, si no, inicializarlo
        if 'carrito' not in session:
            session['carrito'] = []

        # Agregar el nuevo producto al carrito (sesión)
        item = {
            'producto': MateriaPrima.query.get(producto_id).nombre,
            'proveedor': proveedor_nombre,
            'cantidad': cantidad,
            'unidad_medida': unidad_medida,
            'precio_unitario': precio_unitario,
            'total': cantidad * precio_unitario
        }
        session['carrito'].append(item)
        session.modified = True  # Asegurarse de que los cambios se guardan en la sesión

        flash('Producto agregado al carrito', 'success')

        return redirect(url_for('registro_compras_bp.compras'))  # Redirigir para seguir agregando productos

    # Obtener los productos en el carrito de la sesión
    compras = session.get('carrito', [])
    total_general = sum(item['total'] for item in compras)
    return render_template('compras/registro_compras.html', form=form, compras=compras, total_general=total_general)

@registro_compras_bp.route('/eliminar-producto', methods=['POST'])
def eliminar_producto():
    producto_index = int(request.form['producto_index'])  # Obtén el índice del producto

    # Verificar si el carrito existe en la sesión
    if 'carrito' in session:
        # Eliminar el producto en la posición especificada por el índice
        if 0 <= producto_index < len(session['carrito']):
            session['carrito'].pop(producto_index)
            session.modified = True  # Asegurarse de que los cambios se guardan en la sesión
            flash('Producto eliminado del carrito', 'success')

    return redirect(url_for('registro_compras_bp.compras'))  

@registro_compras_bp.route('/finalizar-compra', methods=['POST'])
def finalizar_compra():
    from app import db 
    if 'carrito' not in session or not session['carrito']:
        flash('No hay productos en el carrito', 'warning')
        return redirect(url_for('registro_compras_bp.compras'))

    nueva_compra = Compra() 
    db.session.add(nueva_compra)
    db.session.commit()

    for item in session['carrito']:
        materia_prima = MateriaPrima.query.filter_by(nombre=item['producto']).first()
        proveedor = Proveedores.query.filter_by(nombre=item['proveedor']).first() if item['proveedor'] != "Otro" else None

        detalle = DetalleCompra(
            cantidad=item['cantidad'],
            costo_unitario=item['precio_unitario'],
            total=item['total'],
            compra_id=nueva_compra.id,
            materia_prima_id=materia_prima.id if materia_prima else None,
            proveedor_id=proveedor.id if proveedor else None,
            proveedor_nombre=item['proveedor']
        )
        db.session.add(detalle)

    db.session.commit()

    session.pop('carrito', None)
    flash('Compra finalizada con éxito', 'success')

    return redirect(url_for('registro_compras_bp.compras'))


