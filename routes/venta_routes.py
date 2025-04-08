import datetime
from flask import Blueprint, Response, render_template, request, redirect, send_from_directory, url_for, flash, jsonify
from models.models import DetallePedido, Galleta, Pedido, db, Venta, DetalleVenta
from forms.venta_forms import VentaForm
from forms.pedido_forms import PedidoListoForm
from utils.decoradores import login_required, log_excepciones, role_required
from functools import wraps

ventas_bp = Blueprint('ventas_bp', __name__, url_prefix='/ventas')

class VentaActual:
    def __init__(self):
        self.detalles = []
        self.total = 0.0
        self.productos= 0
    
    def agregar_producto(self, galleta_id, nombre, cantidad, precio):
        for item in self.detalles:
            if item['id'] == galleta_id:
                item['cantidad'] += cantidad
                item['subtotal'] = item['cantidad'] * item['precio']
                self.calcular_total()
                return False  
        
        nuevo_item = {
            'id': galleta_id,
            'galleta': nombre,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': cantidad * precio
        }
        self.detalles.append(nuevo_item)
        self.calcular_total()
        self.totalProductos()
        return True  
    
    def calcular_total(self):
        self.total = sum(item['subtotal'] for item in self.detalles)
    def totalProductos(self):
        self.productos = sum(item['cantidad'] for item in self.detalles)
    
    def limpiar_venta(self):
        self.detalles = []
        self.total = 0.0
        self.productos = 0

venta_actual = VentaActual()

@ventas_bp.route("/")
@login_required
@log_excepciones
@role_required('admin')
def index():
    ventaForm = VentaForm()
    pedidoForm = PedidoListoForm()
    galletas = Galleta.query.options(
        db.joinedload(Galleta.receta)
    ).filter(
        Galleta.estatus == 1  
    ).order_by(
        Galleta.nombre.asc()  
    ).all()
    return render_template(
        "venta/venta.html", 
        galletas=galletas, 
        pedidoForm = pedidoForm,
        form=ventaForm, 
        detalles_venta=venta_actual.detalles,
        total=venta_actual.total,
        productos=venta_actual.productos
    )

@ventas_bp.route('/imagen/<int:galleta_id>')
def mostrar_imagen(galleta_id):
    galleta = Galleta.query.get_or_404(galleta_id)
    if not galleta.foto:
        return send_from_directory('static', 'images/default-cookie.png')
    return Response(galleta.foto, mimetype='image/jpeg')


@ventas_bp.route("/eliminar_galleta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def eliminar_galleta():
    try:
        galleta_id = int(request.form.get('galleta_id'))
        
        for i, item in enumerate(venta_actual.detalles):
            if item['id'] == galleta_id:
                venta_actual.detalles.pop(i)
                venta_actual.calcular_total()
                flash('Producto eliminado de la venta', 'success')
                return redirect(url_for('ventas_bp.index'))
        
        flash('Producto no encontrado en la venta', 'error')
    
    except ValueError:
        flash('ID de producto no válido', 'error')
    except Exception as e:
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
    
    return redirect(url_for('ventas_bp.index'))

@ventas_bp.route("/add_galleta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def add_galleta():
    ventaForm = VentaForm(request.form)
    if not ventaForm.validate():
        for field, errors in ventaForm.errors.items():
            for error in errors:
                flash(f"Error en {field}: {error}", 'error')
        return redirect(url_for('ventas_bp.index'))
    
    try:
        galleta_id = int(request.form.get('galleta_id'))
        presentacion = int(ventaForm.presentacion.data)
        cantidad = int(ventaForm.cantidad.data)
        
        galleta = Galleta.query.get_or_404(galleta_id)
        
        if presentacion == 1:  
            unidades_a_agregar  = cantidad
        elif presentacion == 2:  
            unidades_a_agregar  = cantidad * 30
        elif presentacion == 3: 
            unidades_a_agregar  = cantidad * 24
        else:
            flash('Presentación no válida', 'error')
            return redirect(url_for('ventas_bp.index'))
        
        if galleta.stock < unidades_a_agregar:
            flash(f'No hay suficiente stock. Disponible: {galleta.stock} unidades', 'error')
            return redirect(url_for('ventas_bp.index'))

        item_existente = next((item for item in venta_actual.detalles if item['id'] == galleta_id), None)
        total_en_carrito = unidades_a_agregar + (item_existente['cantidad'] if item_existente else 0)

        if total_en_carrito > galleta.stock:
            disponible = galleta.stock - (item_existente['cantidad'] if item_existente else 0)
            flash(f'No hay suficiente stock. Puedes agregar hasta {disponible} unidades más', 'error')
            return redirect(url_for('ventas_bp.index'))
        
        fue_nuevo = venta_actual.agregar_producto(
            galleta_id=galleta_id,
            nombre=galleta.nombre,
            cantidad=unidades_a_agregar ,
            precio=float(galleta.precio)
        )  
    
        mensaje = 'Producto agregado correctamente' if fue_nuevo else 'Cantidad actualizada correctamente'
        flash(mensaje, 'success')
        
    except ValueError as e:
        flash('Error en los datos proporcionados: valores no válidos', 'error')
    except Exception as e:
        flash(f'Error al procesar la venta: {str(e)}', 'error')
    
    return redirect(url_for('ventas_bp.index'))


@ventas_bp.route("/limpiar_venta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def limpiar_venta():
    try:
        venta_actual.limpiar_venta()
        flash('Venta limpiada correctamente', 'success')
    except Exception as e:
        flash(f'Error al limpiar la venta: {str(e)}', 'error')
    
    return redirect(url_for('ventas_bp.index'))


@ventas_bp.route("/realizar_venta", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def realizar_venta():
    try:
        if not venta_actual.detalles:
            flash('No hay productos en la venta', 'error')
            return redirect(url_for('ventas_bp.index'))
        nueva_venta = Venta(
            total=venta_actual.total,
        )

        for item in venta_actual.detalles:
            detalle = DetalleVenta(
                galleta_id=item['id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            nueva_venta.detalles.append(detalle)

            galleta = Galleta.query.get(item['id'])
            galleta.stock -= item['cantidad']
            if galleta.stock < 0:  
                galleta.stock = 0
            db.session.add(galleta)

        db.session.add(nueva_venta)
        db.session.commit()

        venta_actual.limpiar_venta()

        flash('Venta registrada exitosamente', 'success')
        return redirect(url_for('ventas_bp.index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la venta: {str(e)}', 'error')
        return redirect(url_for('ventas_bp.index'))
    

# Realizar venta del pedido

@ventas_bp.route("/detallePedido", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def detallePedido():
    form = PedidoListoForm()
    if form.validate_on_submit():
        pedido_id = form.pedido.data
        
        pedido = Pedido.query.options(
            db.joinedload(Pedido.usuario),
            db.joinedload(Pedido.detalles).joinedload(DetallePedido.galleta)
        ).get(pedido_id)

        if not pedido:
            flash('Pedido no encontrado', 'error')
            return redirect(url_for('ventas_bp.index'))

        galletas_agrupadas = {}
        total = 0
        
        for detalle in pedido.detalles:
            galleta = detalle.galleta
            galleta_id = galleta.id
            
            if galleta_id not in galletas_agrupadas:
                galletas_agrupadas[galleta_id] = {
                    'id': galleta.id,
                    'nombre': galleta.nombre,
                    'cantidad': detalle.cantidad,
                    'precio': detalle.precio_unitario,
                    'subtotal': detalle.cantidad * detalle.precio_unitario
                }
            else:
                galletas_agrupadas[galleta_id]['cantidad'] += detalle.cantidad
                galletas_agrupadas[galleta_id]['subtotal'] += detalle.cantidad * detalle.precio_unitario
            
            total += detalle.cantidad * detalle.precio_unitario

        productos_agrupados = list(galletas_agrupadas.values())

        return render_template("venta/procesar_pago.html",
                            pedido=pedido,
                            productos=productos_agrupados,
                            total=total,
                            form=form)
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Error en {getattr(form, field).label.text}: {error}', 'error')
    
    return redirect(url_for('ventas_bp.index'))


@ventas_bp.route("/realizar_venta_pedido", methods=["POST"])
@login_required
@log_excepciones
@role_required('admin')
def realizar_venta_pedido():
    pedido_id = request.form.get('pedido_id')
    
    if not pedido_id:
        flash('No se especificó un pedido', 'error')
        return redirect(url_for('ventas_bp.index'))

    try:
        pedido_id = int(pedido_id)
    except ValueError:
        flash('ID de pedido inválido', 'error')
        return redirect(url_for('ventas_bp.index'))

    try:
        with db.session.begin():
            pedido = Pedido.query.options(
                db.joinedload(Pedido.detalles).joinedload(DetallePedido.galleta),
                db.joinedload(Pedido.usuario)
            ).get(pedido_id)

            if not pedido:
                flash('Pedido no encontrado', 'error')
                return redirect(url_for('ventas_bp.index'))

            # Agrupar galletas por ID y sumar cantidades
            galletas_agrupadas = {}
            for detalle in pedido.detalles:
                galleta = detalle.galleta
                if galleta.id not in galletas_agrupadas:
                    galletas_agrupadas[galleta.id] = {
                        'galleta': galleta,
                        'cantidad_total': detalle.cantidad,
                        'precio_unitario': detalle.precio_unitario
                    }
                else:
                    galletas_agrupadas[galleta.id]['cantidad_total'] += detalle.cantidad

            # Verificar stock y monto recibido
            total_pedido = sum(d.cantidad * d.precio_unitario for d in pedido.detalles)
            

            for galleta_id, datos in galletas_agrupadas.items():
                if datos['galleta'].stock < datos['cantidad_total']:
                    raise ValueError(f"Stock insuficiente de {datos['galleta'].nombre}. Disponible: {datos['galleta'].stock}, Requerido: {datos['cantidad_total']}")

            # Crear la venta
            venta = Venta(
                total=total_pedido,
                usuario_id=pedido.usuario_id,
            )
            db.session.add(venta)
            db.session.flush()

            # Procesar cada galleta
            for galleta_id, datos in galletas_agrupadas.items():
                galleta = datos['galleta']
                
                # 1. Registrar detalle de venta
                detalle_venta = DetalleVenta(
                    venta_id=venta.id,
                    galleta_id=galleta_id,
                    cantidad=datos['cantidad_total'],
                    precio_unitario=datos['precio_unitario']
                )
                db.session.add(detalle_venta)
                
                # 2. Actualizar stock
                galleta.stock -= datos['cantidad_total']
                
                # 3. Actualizar estado según nuevo stock
                if galleta.stock >= 30:
                    galleta.estadoStock = 'Completo'
                elif galleta.stock >= 10:
                    galleta.estadoStock = 'Bajo'
                else:
                    galleta.estadoStock = 'Agotado'

            # Actualizar estado del pedido
            pedido.estatus = "Finalizado"

            flash('Venta registrada exitosamente', 'success')
            return redirect(url_for('ventas_bp.index'))

    except ValueError as e:
        db.session.rollback()
        flash(str(e), 'error')
        return redirect(url_for('ventas_bp.detallePedido', pedido_id=pedido_id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la venta: {str(e)}', 'error')
        return redirect(url_for('ventas_bp.index'))